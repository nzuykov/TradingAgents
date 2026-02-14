from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_crypto_data(
    symbol: Annotated[str, "crypto symbol e.g. BTC, ETH, SOL"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 30,
) -> str:
    """
    Get cryptocurrency market data: price, volume, market cap, supply info,
    price history, and community metrics from CoinGecko.
    Args:
        symbol (str): Crypto symbol (e.g. BTC, ETH, SOL)
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days of history (default 30)
    Returns:
        str: Comprehensive crypto market data report
    """
    return route_to_vendor("get_crypto_data", symbol, curr_date, look_back_days)


@tool
def get_crypto_fear_greed() -> str:
    """
    Get the Crypto Fear & Greed Index (0-100) with recent trend.
    0 = Extreme Fear, 100 = Extreme Greed.
    Returns:
        str: Crypto Fear & Greed report with score and historical trend
    """
    return route_to_vendor("get_crypto_fear_greed")
