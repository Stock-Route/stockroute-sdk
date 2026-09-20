"""本地周/月线聚合——节假日/停牌免疫,全社区统一口径。

设计要点(与服务端 ktype=w/m 同口径):
- 按【实际交易日】分桶(数据里没有的日期不会产生空桶,节假日天然免疫)
- bar 日期 = 期内最后一个交易日
- 涨跌幅由聚合后 close 链重算(首根用 preclose 兜底)
- 停牌行(tradestatus=0)建议聚合前过滤:df[df["tradestatus"]=="1"]
"""
import pandas as pd


def to_period_bars(df: pd.DataFrame, period: str = "W") -> pd.DataFrame:
    """日线 DataFrame → 周/月线。period: "W"(周)或 "M"(月)。"""
    if df is None or len(df) == 0:
        return df.copy() if df is not None else pd.DataFrame()
    d = df.copy()
    dti = pd.to_datetime(d["date"])
    per = "W" if str(period).upper().startswith("W") else "M"
    d["_k"] = dti.dt.to_period(per).astype(str)
    agg = {"date": ("date", "last"), "code": ("code", "first"),
           "open": ("open", "first"), "high": ("high", "max"),
           "low": ("low", "min"), "close": ("close", "last"),
           "volume": ("volume", "sum"), "amount": ("amount", "sum")}
    for c in ("turn", "pctChg", "peTTM", "psTTM",
              "pcfNcfTTM", "pbMRQ", "adjustflag", "tradestatus"):
        if c in d.columns:
            agg[c] = (c, "last")
    if "preclose" in d.columns:              # 周首日前收(月/周涨跌幅首根兜底用)
        agg["preclose"] = ("preclose", "first")
    if "isST" in d.columns:
        agg["isST"] = ("isST", "max")
    out = d.groupby("_k").agg(**agg).sort_values("date").reset_index(drop=True)
    if "close" in out.columns and len(out):
        pc = (out["close"] / out["close"].shift(1) - 1) * 100
        if "preclose" in out.columns:
            pc = pc.fillna((out["close"] / out["preclose"] - 1) * 100)
        out["pctChg"] = pc.round(4)
    return out


def to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """日线 → 周线。"""
    return to_period_bars(df, "W")


def to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """日线 → 月线。"""
    return to_period_bars(df, "M")
