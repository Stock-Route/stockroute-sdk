# stockroute-sdk

StockRoute 数据 API 官方 Python SDK(A 股行情 / 财务 / 资讯 / 元数据,统一 DataFrame-first 体验)。

> ✅ v0.1.0 已发布(PyPI:`pip install stockroute`)

```python
from stockroute import StockRoute
sr = StockRoute()                      # 读环境变量 STOCKROUTE_TOKEN
df = sr.kline("600519")                # 日K:免费3年/基础5年/标准+全历史
print(df.attrs["units"])               # 字段单位口径
```

## 计划特性
- 覆盖 StockRoute 开放 API 全部端点:K线(多档历史深度)/ 点时财务(PIT 强制)/ 通用数据直查(60+ 数据集)/ 每日估值 / 全市场列表 / 快讯
- **DataFrame-first**:返回 pandas DataFrame,单位口径(units)与档位信息自动挂载到 `attrs`
- **类型化异常**:鉴权 / 档位不足 / 配额超限 / 服务限流分层清晰,报错即指引
- 自动分页与限速友好(429 / Retry-After 自动处理)
- 点时财务(PIT):`as_of` 参数强制显式,杜绝前视

## 本地派生周/月线(配额最优实践)
```python
import stockroute
df = sr.kline("600519")                # 拉 1 次日线
wk = stockroute.to_weekly(df)          # 周/月线本地派生,零额外配额
mo = stockroute.to_monthly(df)
```
聚合按实际交易日分桶:节假日/临时休市天然免疫,bar 日期=期内最后交易日,涨跌幅由聚合后 close 链重算。
临时看一眼也可用服务端:`sr.kline("600519", ktype="w")`。

## 文档
接口文档站:https://m-stock.600044.xyz

## 许可
MIT(见 LICENSE)

---

StockRoute · 面向量化研究者的 A 股数据质量层
