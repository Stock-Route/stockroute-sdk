# stockroute-sdk

StockRoute 数据 API 官方 Python SDK(A 股行情 / 财务 / 资讯 / 元数据,统一 DataFrame-first 体验)。

> 🚧 项目处于开发中(v0.1 筹备)。当前仓库仅包含规划说明,首个可用版本即将发布。

## 计划特性
- 覆盖 StockRoute 开放 API 全部端点:K线(多档历史深度)/ 点时财务(PIT 强制)/ 通用数据直查(60+ 数据集)/ 每日估值 / 全市场列表 / 快讯
- **DataFrame-first**:返回 pandas DataFrame,单位口径(units)与档位信息自动挂载到 `attrs`
- **类型化异常**:鉴权 / 档位不足 / 配额超限 / 服务限流分层清晰,报错即指引
- 自动分页与限速友好(429 / Retry-After 自动处理)
- 点时财务(PIT):`as_of` 参数强制显式,杜绝前视

## 文档
接口文档站:https://m-stock.600044.xyz

## 许可
MIT(首个版本发布时附 LICENSE)

---

StockRoute · 面向量化研究者的 A 股数据质量层
