from typing import Annotated

# Import from vendor-specific modules
from .y_finance import (
    get_YFin_data_online,
    get_stock_stats_indicators_window,
    get_fundamentals as get_yfinance_fundamentals,
    get_balance_sheet as get_yfinance_balance_sheet,
    get_cashflow as get_yfinance_cashflow,
    get_income_statement as get_yfinance_income_statement,
    get_insider_transactions as get_yfinance_insider_transactions,
)
from .yfinance_news import get_news_yfinance, get_global_news_yfinance
from .alpha_vantage import (
    get_stock as get_alpha_vantage_stock,
    get_indicator as get_alpha_vantage_indicator,
    get_fundamentals as get_alpha_vantage_fundamentals,
    get_balance_sheet as get_alpha_vantage_balance_sheet,
    get_cashflow as get_alpha_vantage_cashflow,
    get_income_statement as get_alpha_vantage_income_statement,
    get_insider_transactions as get_alpha_vantage_insider_transactions,
    get_news as get_alpha_vantage_news,
    get_global_news as get_alpha_vantage_global_news,
)
from .alpha_vantage_common import AlphaVantageRateLimitError

# Phase 1: Options, FRED, Google Trends
from .yfinance_options import get_options_chain_yfinance
from .fred_macro import get_macro_indicators_fred
from .google_trends import get_search_trends_google

# Phase 2: Reddit, Stocktwits, Fear & Greed
from .reddit_social import get_reddit_sentiment_praw
from .stocktwits_social import get_stocktwits_sentiment_api
from .fear_greed import get_fear_greed_index_cnn

# Phase 3: SEC EDGAR, CoinGecko
from .sec_edgar import get_sec_filings_edgar
from .coingecko import get_crypto_data_coingecko, get_crypto_fear_greed_coingecko

# Configuration and routing logic
from .config import get_config

# Tools organized by category
TOOLS_CATEGORIES = {
    "core_stock_apis": {
        "description": "OHLCV stock price data",
        "tools": [
            "get_stock_data"
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_indicators"
        ]
    },
    "fundamental_data": {
        "description": "Company fundamentals",
        "tools": [
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement"
        ]
    },
    "news_data": {
        "description": "News and insider data",
        "tools": [
            "get_news",
            "get_global_news",
            "get_insider_transactions",
        ]
    },
    "options_data": {
        "description": "Options chain data (IV, volume, OI, put/call ratio)",
        "tools": [
            "get_options_chain"
        ]
    },
    "macro_data": {
        "description": "Macroeconomic indicators from FRED",
        "tools": [
            "get_macro_indicators"
        ]
    },
    "search_trends": {
        "description": "Google Trends search interest",
        "tools": [
            "get_search_trends"
        ]
    },
    "social_sentiment": {
        "description": "Social media sentiment (Reddit, Stocktwits, Fear & Greed)",
        "tools": [
            "get_reddit_sentiment",
            "get_stocktwits_sentiment",
            "get_fear_greed_index",
        ]
    },
    "sec_filings": {
        "description": "SEC EDGAR filings",
        "tools": [
            "get_sec_filings"
        ]
    },
    "crypto_data": {
        "description": "Cryptocurrency data from CoinGecko",
        "tools": [
            "get_crypto_data",
            "get_crypto_fear_greed",
        ]
    },
}

VENDOR_LIST = [
    "yfinance",
    "alpha_vantage",
    "fred",
    "google_trends",
    "reddit",
    "stocktwits",
    "cnn",
    "sec_edgar",
    "coingecko",
]

# Mapping of methods to their vendor-specific implementations
VENDOR_METHODS = {
    # core_stock_apis
    "get_stock_data": {
        "alpha_vantage": get_alpha_vantage_stock,
        "yfinance": get_YFin_data_online,
    },
    # technical_indicators
    "get_indicators": {
        "alpha_vantage": get_alpha_vantage_indicator,
        "yfinance": get_stock_stats_indicators_window,
    },
    # fundamental_data
    "get_fundamentals": {
        "alpha_vantage": get_alpha_vantage_fundamentals,
        "yfinance": get_yfinance_fundamentals,
    },
    "get_balance_sheet": {
        "alpha_vantage": get_alpha_vantage_balance_sheet,
        "yfinance": get_yfinance_balance_sheet,
    },
    "get_cashflow": {
        "alpha_vantage": get_alpha_vantage_cashflow,
        "yfinance": get_yfinance_cashflow,
    },
    "get_income_statement": {
        "alpha_vantage": get_alpha_vantage_income_statement,
        "yfinance": get_yfinance_income_statement,
    },
    # news_data
    "get_news": {
        "alpha_vantage": get_alpha_vantage_news,
        "yfinance": get_news_yfinance,
    },
    "get_global_news": {
        "yfinance": get_global_news_yfinance,
        "alpha_vantage": get_alpha_vantage_global_news,
    },
    "get_insider_transactions": {
        "alpha_vantage": get_alpha_vantage_insider_transactions,
        "yfinance": get_yfinance_insider_transactions,
    },
    # options_data (Phase 1)
    "get_options_chain": {
        "yfinance": get_options_chain_yfinance,
    },
    # macro_data (Phase 1)
    "get_macro_indicators": {
        "fred": get_macro_indicators_fred,
    },
    # search_trends (Phase 1)
    "get_search_trends": {
        "google_trends": get_search_trends_google,
    },
    # social_sentiment (Phase 2)
    "get_reddit_sentiment": {
        "reddit": get_reddit_sentiment_praw,
    },
    "get_stocktwits_sentiment": {
        "stocktwits": get_stocktwits_sentiment_api,
    },
    "get_fear_greed_index": {
        "cnn": get_fear_greed_index_cnn,
    },
    # sec_filings (Phase 3)
    "get_sec_filings": {
        "sec_edgar": get_sec_filings_edgar,
    },
    # crypto_data (Phase 3)
    "get_crypto_data": {
        "coingecko": get_crypto_data_coingecko,
    },
    "get_crypto_fear_greed": {
        "coingecko": get_crypto_fear_greed_coingecko,
    },
}

def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")

def get_vendor(category: str, method: str = None) -> str:
    """Get the configured vendor for a data category or specific tool method.
    Tool-level configuration takes precedence over category-level.
    """
    config = get_config()

    # Check tool-level configuration first (if method provided)
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Build fallback chain: primary vendors first, then remaining available vendors
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl

        try:
            return impl_func(*args, **kwargs)
        except AlphaVantageRateLimitError:
            continue  # Only rate limits trigger fallback

    raise RuntimeError(f"No available vendor for '{method}'")
