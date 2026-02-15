from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
import re
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_transactions, get_sec_filings
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
            get_sec_filings,
        ]

        system_message = (
            "You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, and company financial history to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            + " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements, and `get_sec_filings(ticker, filing_type, limit)` to retrieve SEC EDGAR filings (10-K, 10-Q, 8-K) with filing dates and content excerpts.",
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
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
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

        if result.tool_calls:
            # Intermediate step — don't overwrite report with empty string
            return {"messages": [result]}

        # Final step — capture report
        content = result.content or ""

        # Detect if model wrote inline tool calls instead of a real report
        if len(content) < 300 or re.search(r'get_\w+\s*\{', content):
            # Re-invoke LLM without tools to force a written analysis
            report_chain = prompt | llm
            nudge = HumanMessage(
                content="Based on all the financial data gathered above, write your "
                "comprehensive fundamentals analysis report now with a summary table at the end. "
                "Do not attempt to call any tools."
            )
            retry_msgs = state["messages"] + [result, nudge]
            retry_result = report_chain.invoke(retry_msgs)
            report = retry_result.content or content
            return {
                "messages": [result, nudge, retry_result],
                "fundamentals_report": report,
            }

        return {
            "messages": [result],
            "fundamentals_report": content,
        }

    return fundamentals_analyst_node
