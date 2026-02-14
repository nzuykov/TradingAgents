"""Stocktwits sentiment data."""

import requests
from typing import Annotated


def get_stocktwits_sentiment_api(
    ticker: Annotated[str, "ticker symbol"],
) -> str:
    """
    Get Stocktwits sentiment for a ticker: bull/bear ratio, trending status,
    and recent messages.

    No API key needed. Uses public Stocktwits API.

    Args:
        ticker: Ticker symbol (e.g. "AAPL")

    Returns:
        Formatted string with Stocktwits sentiment data
    """
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker.upper()}.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 404:
            return f"Ticker {ticker} not found on Stocktwits"
        if response.status_code == 429:
            return "Stocktwits rate limit reached. Try again later."

        response.raise_for_status()
        data = response.json()

        symbol_info = data.get("symbol", {})
        messages = data.get("messages", [])

        report = f"# Stocktwits Sentiment: ${ticker.upper()}\n\n"

        # Symbol info
        if symbol_info:
            report += f"**Symbol:** {symbol_info.get('symbol', ticker)}\n"
            report += f"**Title:** {symbol_info.get('title', 'N/A')}\n"
            if symbol_info.get("watchlist_count"):
                report += f"**Watchlist Count:** {symbol_info['watchlist_count']:,}\n"

        # Analyze sentiment from messages
        bullish = 0
        bearish = 0
        total = len(messages)

        report += f"\n## Recent Messages ({total} posts)\n\n"

        for msg in messages[:10]:
            sentiment = msg.get("entities", {}).get("sentiment", {})
            sentiment_label = sentiment.get("basic", "neutral") if sentiment else "neutral"

            if sentiment_label == "Bullish":
                bullish += 1
            elif sentiment_label == "Bearish":
                bearish += 1

            username = msg.get("user", {}).get("username", "unknown")
            body = msg.get("body", "")[:200]
            created = msg.get("created_at", "")[:10]
            likes = msg.get("likes", {}).get("total", 0)

            report += f"- **[{sentiment_label.upper()}]** @{username} ({created})\n"
            report += f"  {body}\n"
            if likes > 0:
                report += f"  Likes: {likes}\n"
            report += "\n"

        # Count sentiment from all messages
        for msg in messages[10:]:
            sentiment = msg.get("entities", {}).get("sentiment", {})
            sentiment_label = sentiment.get("basic", "neutral") if sentiment else "neutral"
            if sentiment_label == "Bullish":
                bullish += 1
            elif sentiment_label == "Bearish":
                bearish += 1

        # Summary
        report += "## Sentiment Summary\n"
        report += f"**Bullish:** {bullish} | **Bearish:** {bearish} | **Neutral/Unknown:** {total - bullish - bearish}\n"
        if bullish + bearish > 0:
            bull_ratio = bullish / (bullish + bearish) * 100
            overall = "BULLISH" if bull_ratio > 60 else "BEARISH" if bull_ratio < 40 else "MIXED"
            report += f"**Bull/Bear Ratio:** {bull_ratio:.0f}% bullish\n"
            report += f"**Overall Sentiment:** {overall}\n"

        return report

    except requests.exceptions.RequestException as e:
        return f"Error fetching Stocktwits data for {ticker}: {str(e)}"
    except Exception as e:
        return f"Error processing Stocktwits data for {ticker}: {str(e)}"
