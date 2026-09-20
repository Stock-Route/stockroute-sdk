"""StockRoute Python SDK——A 股数据(行情/财务/资讯/元数据)统一访问。

快速开始:
    from stockroute import StockRoute
    sr = StockRoute()                      # 读环境变量 STOCKROUTE_TOKEN
    df = sr.kline("600519")                # 近3年日K(档位越高历史越长)
    df = sr.query("board.zt_pools")        # 通用数据直查
    df.attrs["units"]                      # 字段单位口径
"""

from .client import StockRoute
from .exceptions import (AuthError, NotFoundError, QuotaError, RateLimited,
                         ServerError, StockRouteError, TierError)

__version__ = "0.1.1"
__all__ = ["StockRoute", "StockRouteError", "AuthError", "TierError",
           "QuotaError", "RateLimited", "NotFoundError", "ServerError"]
