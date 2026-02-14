from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    get_news,
    get_reddit_sentiment,
    get_stocktwits_sentiment,
    get_search_trends,
    get_fear_greed_index,
)
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_reddit_sentiment,
            get_stocktwits_sentiment,
            get_search_trends,
            get_fear_greed_index,
            get_news,
        ]

        system_message = (
            "You are a social media sentiment analyst tasked with gauging public opinion and retail investor sentiment for a specific company. You have access to multiple real data sources:\n\n"
            "1. **get_reddit_sentiment(ticker, curr_date, look_back_days)** — Analyzes posts from r/wallstreetbets, r/stocks, r/investing for bull/bear sentiment\n"
            "2. **get_stocktwits_sentiment(ticker)** — Gets bull/bear ratio and recent messages from the Stocktwits community\n"
            "3. **get_search_trends(ticker, curr_date, look_back_days)** — Google Trends search interest showing public attention over time\n"
            "4. **get_fear_greed_index(curr_date)** — CNN Fear & Greed Index (0-100) showing overall market sentiment\n"
            "5. **get_news(ticker, start_date, end_date)** — Company-specific news for context\n\n"
            "Use ALL available tools to build a comprehensive sentiment picture. Cross-reference signals across sources — if Reddit is bullish but Fear & Greed shows extreme greed, that's a different signal than if both are moderate. "
            "Look for divergences between social sentiment and market sentiment indicators. Rising Google Trends interest combined with strong Reddit sentiment can signal incoming retail momentum. "
            "Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The current company we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
