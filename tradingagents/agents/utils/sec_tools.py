from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_sec_filings(
    ticker: Annotated[str, "ticker symbol of the company"],
    filing_type: Annotated[str, "filing type e.g. 10-K, 10-Q, 8-K"] = "10-K",
    limit: Annotated[int, "max number of filings to return"] = 3,
) -> str:
    """
    Fetch recent SEC EDGAR filings for a company. Returns filing dates,
    descriptions, URLs, and content excerpts.
    Args:
        ticker (str): Ticker symbol (e.g. AAPL, NVDA)
        filing_type (str): Filing type filter (default "10-K"). Options: 10-K, 10-Q, 8-K
        limit (int): Max number of filings to return (default 3)
    Returns:
        str: SEC filing report with dates, descriptions, and excerpts
    """
    return route_to_vendor("get_sec_filings", ticker, filing_type, limit)
