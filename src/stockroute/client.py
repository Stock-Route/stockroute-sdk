"""StockRoute 客户端:统一鉴权/重试/类型化异常/DataFrame-first。"""
import os
import time

import pandas as pd
import requests

from .exceptions import (AuthError, NotFoundError, QuotaError, RateLimited,
                         ServerError, TierError)

DEFAULT_BASE = "https://api-stock.600044.xyz"


def _parse_detail(body) -> str:
    if isinstance(body, dict):
        for k in ("detail", "message"):
            if body.get(k):
                return str(body[k])
    return str(body)[:300]


class StockRoute:
    """StockRoute 数据 API 客户端。

    token: 访问令牌(门户「Token」页签发);缺省读环境变量 STOCKROUTE_TOKEN。
    base:  API 地址,默认公网入口,一般无需修改。
    """

    def __init__(self, token: str = None, base: str = None, timeout: int = 30, retries: int = 2):
        self.token = token or os.environ.get("STOCKROUTE_TOKEN")
        if not self.token:
            raise AuthError("缺少 token:构造传参,或设置环境变量 STOCKROUTE_TOKEN")
        self.base = (base or DEFAULT_BASE).rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._sess = requests.Session()
        self._sess.headers.update({"Authorization": f"Bearer {self.token}",
                                   "Accept": "application/json"})

    # ── 底层 ──
    def _get(self, path: str, params: dict = None) -> dict:
        """GET + 自动重试(502/503/网络抖动)+ 类型化异常。200 → JSON dict。"""
        url = self.base + path
        r = None
        for i in range(self.retries + 1):
            try:
                r = self._sess.get(url, params=params or {}, timeout=self.timeout)
            except requests.RequestException as e:
                if i < self.retries:
                    time.sleep(0.5 * (i + 1))
                    continue
                raise ServerError(f"网络错误: {e}", status=0)
            if r.status_code in (502, 503) and i < self.retries:
                time.sleep(0.5 * (i + 1))
                continue
            break
        if r.status_code == 200:
            return r.json()
        detail = _parse_detail_body(r)
        if r.status_code == 401:
            raise AuthError(detail)
        if r.status_code == 403 and "tier below min_points" in detail:
            have, need = _extract_have_need(detail)
            raise TierError(f"档位不足:需 {need} 分,当前 {have} 分。到门户「充值」页升级",
                            have=have, need=need)
        if r.status_code == 403 and "exceeded" in detail:
            raise QuotaError(detail)
        if r.status_code == 429:
            raise RateLimited(detail, retry_after=int(r.headers.get("Retry-After", "60")))
        if r.status_code == 404:
            raise NotFoundError(detail)
        raise ServerError(f"HTTP {r.status_code}: {detail}", status=r.status_code)

    @staticmethod
    def _to_df(payload: dict) -> pd.DataFrame:
        """rows → DataFrame;units/count/total 等挂 attrs(与数据一起自然传递)。"""
        df = pd.DataFrame(payload.get("rows") or [])
        df.attrs["units"] = payload.get("units") or {}
        df.attrs["count"] = payload.get("count")
        df.attrs["total"] = payload.get("total")
        df.attrs["raw"] = {k: v for k, v in payload.items() if k != "rows"}
        return df

    # ── 数据端点 ──
    def kline(self, code: str, start: str = None, end: str = None) -> pd.DataFrame:
        """个股日 K(OHLCV/涨跌幅/复权/ST/估值尾列)。
        历史深度按档位:免费3年 / 基础5年 / 标准及以上全历史。"""
        p = self._get("/api/kline", _clean(code=code, start=start, end=end))
        return self._to_df(p)

    def financial(self, code: str, kind: str, as_of: str) -> pd.DataFrame:
        """点时财务(PIT 强制):只返回公告日严格早于 as_of 的记录,杜绝前视。
        kind: profit/growth/balance/cashflow/dividend/forecast/express/dupont"""
        p = self._get("/api/financial", _clean(code=code, kind=kind, as_of=as_of))
        df = self._to_df(p)
        df.attrs["pit_rule"] = p.get("pit_rule")
        return df

    def daily_basic(self, code: str, date: str = None) -> pd.DataFrame:
        """单股每日估值全套(PE/PB/股息率/换手/市值)。date 缺省=最新。"""
        p = self._get("/api/daily_basic", _clean(code=code, date=date))
        return self._to_df(p)

    def query(self, dataset: str, code: str = None, start: str = None,
              end: str = None, limit: int = None) -> pd.DataFrame:
        """通用数据直查(60+ 数据集)。可选集见 self.datasets() 或接口文档。
        无过滤参数时返回最新一个日期切片;行数按档位封顶。"""
        p = self._get("/api/query", _clean(dataset=dataset, code=code,
                                           start=start, end=end, limit=limit))
        return self._to_df(p)

    def stocks(self, status: str = "L", industry: str = None, keyword: str = None,
               limit: int = 1000, offset: int = 0, paginate: bool = False) -> pd.DataFrame:
        """全 A 股列表(代码/名称/行业分类/上市退市日)。
        paginate=True 自动翻页拉全量(total≈3800)。"""
        out = []
        off = offset
        while True:
            p = self._get("/api/meta/stocks", _clean(status=status, industry=industry,
                                                     keyword=keyword, limit=limit, offset=off))
            rows = p.get("rows") or []
            out.extend(rows)
            total = p.get("total")
            off += len(rows)
            if not paginate or not rows or (total is not None and off >= total):
                break
        df = pd.DataFrame(out)
        df.attrs["total"] = total
        df.attrs["raw"] = {"offset": offset, "limit": limit, "paginate": paginate}
        return df

    def news(self, since: str = None, code: str = None, keyword: str = None,
             cat: str = None, src: str = None, limit: int = None) -> pd.DataFrame:
        """全市场快讯(增量游标 since=上次最新 ts;支持按股/关键词/类别)。"""
        p = self._get("/api/news", _clean(since=since, code=code, keyword=keyword,
                                          cat=cat, src=src, limit=limit))
        df = self._to_df(p)
        if len(df):
            df.attrs["last_ts"] = df.iloc[0].get("ts")   # 增量游标:下次作 since
        return df

    # ── 元数据 ──
    def datasets(self) -> dict:
        """数据集契约字典(units/SLA/min_points/PIT 规则),按当前档位过滤。"""
        return self._get("/api/datasets")


def _clean(**kw) -> dict:
    """去 None 参数。"""
    return {k: v for k, v in kw.items() if v is not None}


def _parse_detail_body(r) -> str:
    try:
        body = r.json()
    except Exception:
        return (r.text or "")[:300]
    if isinstance(body, dict):
        for k in ("detail", "message"):
            if body.get(k):
                return str(body[k])
    return str(body)[:300]


def _extract_have_need(detail: str):
    import re
    m_have = re.search(r"have (\d+)pts", detail)
    m_need = re.search(r"need (\d+)", detail)
    return (int(m_have.group(1)) if m_have else None,
            int(m_need.group(1)) if m_need else None)
