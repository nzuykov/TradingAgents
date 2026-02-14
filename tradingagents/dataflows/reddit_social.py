"""Reddit sentiment data from investing subreddits."""

import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated


def get_reddit_sentiment_praw(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 7,
) -> str:
    """
    Get Reddit sentiment for a ticker from r/wallstreetbets, r/stocks, r/investing.
    Top posts mentioning the ticker with upvotes, comments, and sentiment summary.

    Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.

    Args:
        ticker: Ticker symbol (e.g. "AAPL")
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 7)

    Returns:
        Formatted string with Reddit sentiment data
    """
    try:
        import praw
    except ImportError:
        return "Error: praw package not installed. Run: pip install praw"

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        return "Error: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables not set. Get free credentials at https://www.reddit.com/prefs/apps"

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="TradingAgents/1.0 (research bot)",
        )

        subreddits = ["wallstreetbets", "stocks", "investing"]
        ticker_upper = ticker.upper()

        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        cutoff_dt = curr_dt - relativedelta(days=look_back_days)

        report = f"# Reddit Sentiment: ${ticker_upper} (past {look_back_days} days)\n\n"

        total_posts = 0
        total_upvotes = 0
        total_comments = 0
        bullish_signals = 0
        bearish_signals = 0

        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                posts_found = []

                # Search for ticker mentions
                for post in subreddit.search(ticker_upper, sort="relevance", time_filter="week", limit=25):
                    post_dt = datetime.fromtimestamp(post.created_utc)
                    if post_dt < cutoff_dt:
                        continue

                    title_lower = post.title.lower()
                    # Simple sentiment signals
                    bull_words = ["buy", "calls", "moon", "bullish", "long", "undervalued", "breakout", "rocket"]
                    bear_words = ["sell", "puts", "crash", "bearish", "short", "overvalued", "dump", "bubble"]

                    post_bull = sum(1 for w in bull_words if w in title_lower)
                    post_bear = sum(1 for w in bear_words if w in title_lower)
                    bullish_signals += post_bull
                    bearish_signals += post_bear

                    posts_found.append({
                        "title": post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "date": post_dt.strftime("%Y-%m-%d"),
                        "url": f"https://reddit.com{post.permalink}",
                        "sentiment": "bullish" if post_bull > post_bear else "bearish" if post_bear > post_bull else "neutral",
                    })

                    total_posts += 1
                    total_upvotes += post.score
                    total_comments += post.num_comments

                if posts_found:
                    report += f"## r/{sub_name} ({len(posts_found)} posts)\n\n"
                    # Sort by score descending
                    posts_found.sort(key=lambda x: x["score"], reverse=True)
                    for p in posts_found[:5]:
                        report += f"- **[{p['sentiment'].upper()}]** {p['title']}\n"
                        report += f"  Score: {p['score']} | Comments: {p['num_comments']} | Date: {p['date']}\n\n"

            except Exception as e:
                report += f"## r/{sub_name}\nError: {str(e)}\n\n"

        # Overall summary
        report += "## Sentiment Summary\n"
        report += f"**Total Posts:** {total_posts}\n"
        report += f"**Total Upvotes:** {total_upvotes:,}\n"
        report += f"**Total Comments:** {total_comments:,}\n"
        report += f"**Bullish Signals:** {bullish_signals} | **Bearish Signals:** {bearish_signals}\n"

        if bullish_signals + bearish_signals > 0:
            bull_pct = bullish_signals / (bullish_signals + bearish_signals) * 100
            overall = "BULLISH" if bull_pct > 60 else "BEARISH" if bull_pct < 40 else "MIXED"
            report += f"**Overall Sentiment:** {overall} ({bull_pct:.0f}% bullish)\n"
        else:
            report += "**Overall Sentiment:** INSUFFICIENT DATA\n"

        if total_posts == 0:
            report += f"\nNo recent Reddit posts found for ${ticker_upper}. This may indicate low retail interest.\n"

        return report

    except Exception as e:
        return f"Error fetching Reddit data for {ticker}: {str(e)}"
