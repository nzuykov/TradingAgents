from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_macro_indicators(
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve key macroeconomic indicators from FRED: Fed Funds Rate, CPI,
    Unemployment Rate, GDP, 10-Year Treasury Yield, 10Y-2Y Spread,
    and Consumer Sentiment.
    Args:
        curr_date (str): Current date in yyyy-mm-dd format
    Returns:
        str: Formatted report of macro indicators with recent trends
    """
    return route_to_vendor("get_macro_indicators", curr_date)
