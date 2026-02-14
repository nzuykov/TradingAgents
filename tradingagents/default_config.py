import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings (global fallback)
    "llm_provider": "openai",
    "backend_url": "https://api.openai.com/v1",
    # Per-LLM provider overrides (if set, take precedence over llm_provider/backend_url)
    "deep_think_provider": None,        # e.g. "openai" (for OpenAI-compatible APIs)
    "deep_think_llm": "gpt-5.2",
    "deep_think_backend_url": None,     # e.g. "https://open.bigmodel.cn/api/paas/v4"
    "deep_think_api_key": None,         # e.g. os.getenv("GLM_API_KEY")
    "quick_think_provider": None,       # e.g. "openai"
    "quick_think_llm": "gpt-5-mini",
    "quick_think_backend_url": None,    # e.g. "https://api.deepseek.com"
    "quick_think_api_key": None,        # e.g. os.getenv("DEEPSEEK_API_KEY")
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: alpha_vantage, yfinance
        "technical_indicators": "yfinance",  # Options: alpha_vantage, yfinance
        "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance
        "news_data": "yfinance",             # Options: alpha_vantage, yfinance
        "options_data": "yfinance",          # Options: yfinance
        "macro_data": "fred",                # Options: fred (requires FRED_API_KEY)
        "search_trends": "google_trends",    # Options: google_trends
        "social_sentiment": "reddit,stocktwits,cnn",  # Multi-vendor category
        "sec_filings": "sec_edgar",          # Options: sec_edgar
        "crypto_data": "coingecko",          # Options: coingecko
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
}
