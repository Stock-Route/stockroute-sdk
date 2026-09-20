"""StockRoute SDK 异常类型——按错误语义分层,报错即指引。"""


class StockRouteError(Exception):
    """所有 StockRoute 异常的基类。"""


class AuthError(StockRouteError):
    """401:Token 缺失/无效/已吊销。到门户「Token」页重签。"""


class TierError(StockRouteError):
    """403:当前档位不足以访问该数据集。

    属性:
        have: 当前累计积分
        need: 该数据集所需积分
    """

    def __init__(self, message: str, have=None, need=None):
        super().__init__(message)
        self.have = have
        self.need = need


class QuotaError(StockRouteError):
    """403/429:配额超限(月点数/月行数/日点数/日行数/月次数)。
    message 内含具体额度;日/月配额自然周期重置。"""


class RateLimited(StockRouteError):
    """429:触发档位限速。建议按 retry_after 秒后重试。"""

    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class NotFoundError(StockRouteError):
    """404:无数据(代码/日期窗口无匹配)或数据集不可直查。"""


class ServerError(StockRouteError):
    """5xx:服务端错误/权限服务不可达(fail-closed)。SDK 已自动重试,建议稍后再试。"""

    def __init__(self, message: str, status: int = 500):
        super().__init__(message)
        self.status = status
