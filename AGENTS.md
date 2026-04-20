# TradingAgents Project Charter

- Canonical local root: `C:\Users\zouik\Desktop\NZ_Code\TradingAgents`.
- Purpose: local fork of the multi-agent trading framework that orchestrates analysts, researchers, trader, risk, and portfolio-manager roles.
- Start here before non-trivial edits: `README.md`, `CLAUDE.md`, `main.py`, `tradingagents/default_config.py`, `tradingagents/graph/`, `tradingagents/dataflows/`, `cli/`.
- Local fork specifics matter: this repo is wired around OpenRouter plus free data sources. Check `main.py` before assuming upstream defaults.
- Common commands:
  - `pip install -e .`
  - `uv sync`
  - `python main.py`
  - `tradingagents`
  - `python list_models.py`
  - `python test.py`
- Preserve local provider/data-vendor wiring in `main.py` unless the task explicitly changes the fork's operating model.
- Keep debate-round and token-budget choices intentional; they are tuned for iteration cost, not just model quality.
- When changing dataflows, maintain compatibility between vendor outputs and downstream graph/agent expectations.
- Treat `eval_results/` and local `.env` secrets as runtime state. Do not hardcode keys or provider credentials.
