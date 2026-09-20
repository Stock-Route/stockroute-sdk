"""三行拉茅台全历史日K(标准档及以上;免费/基础档按档位截取)。"""
from stockroute import StockRoute

sr = StockRoute()                      # 读环境变量 STOCKROUTE_TOKEN
df = sr.kline("600519")
print(len(df), "行 |", df["date"].min(), "→", df["date"].max())
print("单位口径:", df.attrs["units"])

# 点时财务(PIT):决策日 2026-06-30 只看公告日早于它的财报
fin = sr.financial("600519", kind="profit", as_of="2026-06-30")
print("PIT 净利润最新值:", fin.iloc[0].get("netProfit"))

# 通用直查:涨停池
zt = sr.query("board.zt_pools", limit=10)
print(zt[["代码", "名称"]].head())
