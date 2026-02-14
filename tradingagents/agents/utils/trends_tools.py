from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_search_trends(
    ticker: Annotated[str, "ticker symbol or search term"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 30,
) -> str:
    """
    Get Google Trends search interest over time for a ticker or term.
    Shows interest level (0-100), trend direction, and related queries.
    Args:
        ticker (str): Ticker symbol or search term
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days to look back (default 30)
    Returns:
        str: Formatted report with search interest trends and related queries
    """
    return route_to_vendor("get_search_trends", ticker, curr_date, look_back_days)
