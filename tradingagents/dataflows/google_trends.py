"""Google Trends search interest data."""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated


def get_search_trends_google(
    ticker: Annotated[str, "ticker symbol or search term"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 30,
) -> str:
    """
    Get Google Trends search interest over time for a ticker/term.

    Args:
        ticker: Ticker symbol or search term
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 30)

    Returns:
        Formatted string with search interest data
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        return "Error: pytrends package not installed. Run: pip install pytrends"

    try:
        pytrends = TrendReq(hl="en-US", tz=360)

        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = curr_dt - relativedelta(days=look_back_days)
        timeframe = f"{start_dt.strftime('%Y-%m-%d')} {curr_dt.strftime('%Y-%m-%d')}"

        # Search for ticker and company-related terms
        keywords = [ticker.upper()]

        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo="", gprop="")
        interest_over_time = pytrends.interest_over_time()

        report = f"# Google Trends: {ticker.upper()} ({start_dt.strftime('%Y-%m-%d')} to {curr_date})\n\n"

        if interest_over_time.empty:
            report += "No search interest data available for this period.\n"
            return report

        # Main trend data
        col = ticker.upper()
        if col in interest_over_time.columns:
            data = interest_over_time[col]

            report += "## Search Interest Over Time (0-100 scale)\n"
            for date_idx, value in data.items():
                report += f"  {date_idx.strftime('%Y-%m-%d')}: {value}\n"

            # Summary stats
            report += f"\n**Average Interest:** {data.mean():.1f}\n"
            report += f"**Peak Interest:** {data.max()} (on {data.idxmax().strftime('%Y-%m-%d')})\n"
            report += f"**Min Interest:** {data.min()} (on {data.idxmin().strftime('%Y-%m-%d')})\n"

            # Recent trend direction
            if len(data) >= 3:
                recent_avg = data.tail(3).mean()
                earlier_avg = data.head(3).mean()
                if earlier_avg > 0:
                    change_pct = ((recent_avg - earlier_avg) / earlier_avg) * 100
                    direction = "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable"
                    report += f"**Trend Direction:** {direction} ({change_pct:+.1f}% recent vs earlier)\n"

        # Related queries
        try:
            related = pytrends.related_queries()
            if ticker.upper() in related and related[ticker.upper()]["top"] is not None:
                top_queries = related[ticker.upper()]["top"]
                report += "\n## Top Related Queries\n"
                for _, row in top_queries.head(10).iterrows():
                    report += f"  - {row['query']} (score: {row['value']})\n"

            if ticker.upper() in related and related[ticker.upper()]["rising"] is not None:
                rising_queries = related[ticker.upper()]["rising"]
                report += "\n## Rising Related Queries\n"
                for _, row in rising_queries.head(5).iterrows():
                    report += f"  - {row['query']} (score: {row['value']})\n"
        except Exception:
            pass  # Related queries can fail, non-critical

        return report

    except Exception as e:
        return f"Error fetching Google Trends data for {ticker}: {str(e)}"
