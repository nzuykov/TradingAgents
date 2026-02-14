from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_options_chain(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve options chain data for a ticker symbol including calls, puts,
    implied volatility, volume, open interest, and put/call ratio.
    Args:
        symbol (str): Ticker symbol (e.g. AAPL, NVDA)
        curr_date (str): Current date in yyyy-mm-dd format
    Returns:
        str: Formatted options chain summary with IV, volume, OI, and put/call ratios
    """
    return route_to_vendor("get_options_chain", symbol, curr_date)
