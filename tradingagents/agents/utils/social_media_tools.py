from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_reddit_sentiment(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 7,
) -> str:
    """
    Get Reddit sentiment for a ticker from r/wallstreetbets, r/stocks, r/investing.
    Returns top posts with upvotes, comments, and overall sentiment summary.
    Args:
        ticker (str): Ticker symbol (e.g. AAPL, NVDA)
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days to look back (default 7)
    Returns:
        str: Reddit sentiment report with bull/bear analysis
    """
    return route_to_vendor("get_reddit_sentiment", ticker, curr_date, look_back_days)


@tool
def get_stocktwits_sentiment(
    ticker: Annotated[str, "ticker symbol"],
) -> str:
    """
    Get Stocktwits sentiment for a ticker: bull/bear ratio, trending status,
    and recent messages from the Stocktwits community.
    Args:
        ticker (str): Ticker symbol (e.g. AAPL, NVDA)
    Returns:
        str: Stocktwits sentiment report with bull/bear breakdown
    """
    return route_to_vendor("get_stocktwits_sentiment", ticker)


@tool
def get_fear_greed_index(
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Get the CNN Fear & Greed Index score (0-100) and components.
    0 = Extreme Fear, 100 = Extreme Greed. Useful as a contrarian indicator.
    Args:
        curr_date (str): Current date in yyyy-mm-dd format
    Returns:
        str: Fear & Greed report with score, rating, and historical comparison
    """
    return route_to_vendor("get_fear_greed_index", curr_date)
