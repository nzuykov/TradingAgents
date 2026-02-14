from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)

# Phase 1: Options, FRED, Google Trends
from tradingagents.agents.utils.options_tools import (
    get_options_chain
)
from tradingagents.agents.utils.macro_tools import (
    get_macro_indicators
)
from tradingagents.agents.utils.trends_tools import (
    get_search_trends
)

# Phase 2: Reddit, Stocktwits, Fear & Greed
from tradingagents.agents.utils.social_media_tools import (
    get_reddit_sentiment,
    get_stocktwits_sentiment,
    get_fear_greed_index
)

# Phase 3: SEC EDGAR, CoinGecko
from tradingagents.agents.utils.sec_tools import (
    get_sec_filings
)
from tradingagents.agents.utils.crypto_tools import (
    get_crypto_data,
    get_crypto_fear_greed
)

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages
