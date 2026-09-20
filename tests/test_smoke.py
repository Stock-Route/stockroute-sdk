"""冒烟:未联网部分(异常层级/参数清洗)。真实调用见 examples/。"""
from stockroute import (AuthError, NotFoundError, QuotaError, RateLimited,
                        ServerError, StockRoute, StockRouteError, TierError)
from stockroute.client import _clean


def test_exception_hierarchy():
    assert issubclass(TierError, StockRouteError)
    assert issubclass(QuotaError, StockRouteError)
    assert issubclass(RateLimited, StockRouteError)


def test_tier_error_attrs():
    e = TierError("需 5000 分,当前 1000 分", have=1000, need=5000)
    assert e.have == 1000 and e.need == 5000


def test_clean_drops_none():
    assert _clean(a=1, b=None) == {"a": 1}
