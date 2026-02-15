import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config: DeepSeek (quick) + GLM-5 (deep)
config = DEFAULT_CONFIG.copy()

# Quick thinking: DeepSeek V3.2 via OpenRouter (cheap, fast, data retrieval)
config["quick_think_provider"] = "openai"  # OpenRouter is OpenAI-compatible
config["quick_think_llm"] = "deepseek/deepseek-v3.2"
config["quick_think_backend_url"] = "https://openrouter.ai/api/v1"
config["quick_think_api_key"] = os.getenv("OPENROUTER_API_KEY")

# Deep thinking: Kimi K2.5 via OpenRouter (#2 intelligence, best debates)
config["deep_think_provider"] = "openai"  # OpenRouter is OpenAI-compatible
config["deep_think_llm"] = "moonshotai/kimi-k2.5"
config["deep_think_backend_url"] = "https://openrouter.ai/api/v1"
config["deep_think_api_key"] = os.getenv("OPENROUTER_API_KEY")

# Debate settings
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# Data vendors (yfinance = free, no API key needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",
    "options_data": "yfinance",
    "macro_data": "fred",
    "search_trends": "google_trends",
    "social_sentiment": "reddit,stocktwits,cnn",
    "sec_filings": "sec_edgar",
    "crypto_data": "coingecko",
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Forward propagate — test with NVDA
_, decision = ta.propagate("NVDA", "2026-02-14")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000)  # parameter is the position returns
