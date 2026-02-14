"""CoinGecko cryptocurrency data."""

import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated


# Common crypto symbol to CoinGecko ID mapping
CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "BNB": "binancecoin",
    "ARB": "arbitrum",
    "OP": "optimism",
    "APT": "aptos",
    "SUI": "sui",
    "NEAR": "near",
}

BASE_URL = "https://api.coingecko.com/api/v3"


def _resolve_coin_id(symbol: str) -> str:
    """Resolve a ticker symbol to a CoinGecko coin ID."""
    upper = symbol.upper().replace("-USD", "").replace("USD", "")
    if upper in CRYPTO_ID_MAP:
        return CRYPTO_ID_MAP[upper]
    # Try lowercase as coin ID directly
    return symbol.lower()


def get_crypto_data_coingecko(
    symbol: Annotated[str, "crypto symbol e.g. BTC, ETH, SOL"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "number of days to look back"] = 30,
) -> str:
    """
    Get cryptocurrency price, volume, and market cap data from CoinGecko.

    No API key needed. Free tier: 30 calls/min.

    Args:
        symbol: Crypto symbol (e.g. "BTC", "ETH")
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 30)

    Returns:
        Formatted string with crypto market data
    """
    try:
        coin_id = _resolve_coin_id(symbol)

        # Current data
        current_url = f"{BASE_URL}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "true",
            "developer_data": "false",
        }
        resp = requests.get(current_url, params=params, timeout=10)

        if resp.status_code == 404:
            return f"Cryptocurrency '{symbol}' not found on CoinGecko. Try using the full name (e.g., 'bitcoin' instead of 'BTC')."
        resp.raise_for_status()
        coin_data = resp.json()

        market_data = coin_data.get("market_data", {})

        report = f"# {coin_data.get('name', symbol)} ({coin_data.get('symbol', symbol).upper()}) — Crypto Data\n\n"

        # Current price and market info
        price_usd = market_data.get("current_price", {}).get("usd")
        market_cap = market_data.get("market_cap", {}).get("usd")
        total_volume = market_data.get("total_volume", {}).get("usd")
        price_change_24h = market_data.get("price_change_percentage_24h")
        price_change_7d = market_data.get("price_change_percentage_7d")
        price_change_30d = market_data.get("price_change_percentage_30d")
        ath = market_data.get("ath", {}).get("usd")
        ath_change = market_data.get("ath_change_percentage", {}).get("usd")
        atl = market_data.get("atl", {}).get("usd")

        report += "## Current Market Data\n"
        if price_usd is not None:
            report += f"**Price:** ${price_usd:,.2f}\n"
        if market_cap is not None:
            report += f"**Market Cap:** ${market_cap:,.0f}\n"
        if total_volume is not None:
            report += f"**24h Volume:** ${total_volume:,.0f}\n"
        report += f"**Market Cap Rank:** #{coin_data.get('market_cap_rank', 'N/A')}\n\n"

        report += "## Price Changes\n"
        if price_change_24h is not None:
            report += f"**24h:** {price_change_24h:+.2f}%\n"
        if price_change_7d is not None:
            report += f"**7d:** {price_change_7d:+.2f}%\n"
        if price_change_30d is not None:
            report += f"**30d:** {price_change_30d:+.2f}%\n"
        if ath is not None:
            report += f"**ATH:** ${ath:,.2f} ({ath_change:+.2f}% from ATH)\n"
        if atl is not None:
            report += f"**ATL:** ${atl:,.6f}\n"
        report += "\n"

        # Supply info
        circulating = market_data.get("circulating_supply")
        total_supply = market_data.get("total_supply")
        max_supply = market_data.get("max_supply")

        report += "## Supply\n"
        if circulating:
            report += f"**Circulating:** {circulating:,.0f}\n"
        if total_supply:
            report += f"**Total:** {total_supply:,.0f}\n"
        if max_supply:
            report += f"**Max:** {max_supply:,.0f}\n"
        report += "\n"

        # Historical price data
        market_chart_url = f"{BASE_URL}/coins/{coin_id}/market_chart"
        chart_params = {
            "vs_currency": "usd",
            "days": str(look_back_days),
            "interval": "daily",
        }
        chart_resp = requests.get(market_chart_url, params=chart_params, timeout=10)

        if chart_resp.status_code == 200:
            chart_data = chart_resp.json()
            prices = chart_data.get("prices", [])
            volumes = chart_data.get("total_volumes", [])

            if prices:
                report += f"## Price History (last {look_back_days} days)\n"
                report += "| Date | Price | Volume |\n"
                report += "|------|-------|--------|\n"
                for i, (ts, price) in enumerate(prices):
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                    vol = volumes[i][1] if i < len(volumes) else 0
                    report += f"| {date_str} | ${price:,.2f} | ${vol:,.0f} |\n"
                report += "\n"

        # Community data
        community = coin_data.get("community_data", {})
        if community:
            report += "## Community Metrics\n"
            if community.get("twitter_followers"):
                report += f"**Twitter Followers:** {community['twitter_followers']:,}\n"
            if community.get("reddit_subscribers"):
                report += f"**Reddit Subscribers:** {community['reddit_subscribers']:,}\n"
            if community.get("reddit_average_posts_48h"):
                report += f"**Reddit Posts (48h avg):** {community['reddit_average_posts_48h']:.1f}\n"
            report += "\n"

        return report

    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinGecko data for {symbol}: {str(e)}"
    except Exception as e:
        return f"Error processing CoinGecko data for {symbol}: {str(e)}"


def get_crypto_fear_greed_coingecko() -> str:
    """
    Get the Crypto Fear & Greed Index from alternative.me.
    0 = Extreme Fear, 100 = Extreme Greed.

    Returns:
        Formatted string with crypto fear & greed data
    """
    try:
        url = "https://api.alternative.me/fng/?limit=10"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        entries = data.get("data", [])
        if not entries:
            return "No Crypto Fear & Greed data available"

        report = "# Crypto Fear & Greed Index\n\n"

        latest = entries[0]
        score = int(latest.get("value", 0))
        classification = latest.get("value_classification", "N/A")
        timestamp = latest.get("timestamp", "")

        if timestamp:
            date_str = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
        else:
            date_str = "N/A"

        report += f"**Current Score:** {score} / 100\n"
        report += f"**Classification:** {classification}\n"
        report += f"**Date:** {date_str}\n\n"

        # Historical trend
        report += "## Recent Trend\n"
        report += "| Date | Score | Classification |\n"
        report += "|------|-------|----------------|\n"
        for entry in entries:
            e_score = entry.get("value", "N/A")
            e_class = entry.get("value_classification", "N/A")
            e_ts = entry.get("timestamp", "")
            e_date = datetime.fromtimestamp(int(e_ts)).strftime("%Y-%m-%d") if e_ts else "N/A"
            report += f"| {e_date} | {e_score} | {e_class} |\n"
        report += "\n"

        return report

    except requests.exceptions.RequestException as e:
        return f"Error fetching Crypto Fear & Greed: {str(e)}"
    except Exception as e:
        return f"Error processing Crypto Fear & Greed data: {str(e)}"
