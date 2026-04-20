# TradingAgents

## Purpose
Multi-agent LLM financial trading framework (TauricResearch/TradingAgents v0.2.0).
Mirrors a real trading firm: analyst team, bull/bear researchers, trader agent, risk
management, portfolio manager — orchestrated as a LangGraph. Local fork wired to
OpenRouter (DeepSeek V3.2 for quick thinking, Kimi K2.5 for deep thinking) with
yfinance + FRED + Reddit/StockTwits/CNN as free data sources.

Status: active — primary Claude-assisted project, tracked as "adding 8 free data
sources" in user's project list.

## Stack
- Python >=3.10
- LangGraph + LangChain (OpenAI, Anthropic, Google GenAI adapters)
- Backtrader, pandas, stockstats, yfinance
- Chainlit (UI), Typer (CLI), Rich, questionary
- Redis (caching), rank_bm25
- OpenRouter as primary LLM gateway (OpenAI-compatible)

## Layout
```
TradingAgents/
  main.py                      - Entrypoint wiring OpenRouter + custom config
  tradingagents/
    default_config.py          - DEFAULT_CONFIG (providers, data_vendors, rounds)
    agents/
      analysts/                - fundamentals, sentiment, news, technical
      researchers/             - bull, bear
      trader/
      risk_mgmt/
      managers/                - portfolio manager, research manager
      utils/
    graph/
      trading_graph.py         - Top-level TradingAgentsGraph
      setup.py, propagation.py, conditional_logic.py
      reflection.py, signal_processing.py
    dataflows/                 - Data vendor adapters (yfinance, fred, reddit, ...)
    llm_clients/               - Provider wrappers
  cli/                         - Typer CLI (`tradingagents` entrypoint)
  eval_results/                - Stored run outputs
  pyproject.toml, uv.lock, requirements.txt, run.bat
  list_models.py, test.py
```

## Commands
- Install: `pip install -e .` (or `uv sync`)
- `.env` must define `OPENROUTER_API_KEY` (plus any vendor keys: FRED, Reddit)
- Run main flow: `python main.py` or `run.bat`
- CLI: `tradingagents` (from `[project.scripts]` in pyproject.toml)
- List available models: `python list_models.py`
- Smoke test: `python test.py`

## Notes
- `main.py` overrides DEFAULT_CONFIG: `quick_think_llm=deepseek/deepseek-v3.2`,
  `deep_think_llm=moonshotai/kimi-k2.5`, both via OpenRouter.
- Debate rounds kept low (`max_debate_rounds=1`, `max_risk_discuss_rounds=1`) to
  save tokens during iteration.
- Data vendor map in `main.py` routes different data types to different free
  sources — extend here when adding new vendors.
- Upstream is Tauric Research; keep fork rebased if pulling upstream fixes.
- See `~/.claude/memory/trading-agents-todo.md` for the running TODO list.
