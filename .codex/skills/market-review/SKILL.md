---
name: market-review
description: Execute a full TradingAgents-style workflow without external LLM APIs by emulating fixed agent roles from evidence data. Use when the user asks for full mode with all agents, no-API analysis, deep single-symbol BUY/HOLD/SELL reports, or multi-symbol requests where each symbol must receive its own full deep report in the same fixed role sequence.
---

# Market Review

## Overview
Run the same role structure as TradingAgents, but ground every step in local data pulls and deterministic calculations. Use this skill when the user wants TradingAgents-style output with strict agent ordering and evidence-backed reasoning.

## Quick Start
Run single-symbol context collection:
```bash
python .codex/skills/market-review/scripts/collect_symbol_context.py --symbol NVDA --trade-date 2026-02-15 --include-trends
```

Run any-universe relative-strength scan:
```bash
python .codex/skills/market-review/scripts/scan_universe.py --symbols NVDA,SPY,NQ=F,EURUSD=X --trade-date 2026-02-15
```

Run major-FX relative-strength scan (optional convenience script):
```bash
python .codex/skills/market-review/scripts/scan_forex_majors.py --trade-date 2026-02-15
```

## Workflow
1. Normalize date to the last trading day before analysis.
2. Resolve requested symbols and map aliases to tradable tickers.
3. If multiple symbols are requested, run `scan_universe.py` first for cross-symbol ranking and relative-strength context.
4. For each requested symbol, run `collect_symbol_context.py` and build role outputs in this fixed order:
- Market Analyst
- Social Analyst
- News Analyst
- Fundamentals/Macro Analyst
- Bull Researcher
- Bear Researcher
- Research Manager
- Trader
- Aggressive Risk Analyst
- Conservative Risk Analyst
- Neutral Risk Analyst
- Risk Judge
5. Keep claims tied to specific numeric evidence from the script output.
6. Publish one full deep report per symbol with its own final `BUY|HOLD|SELL` decision.
7. Include a basket-level relative-strength summary only after all symbol-level deep reports are complete.

## Quality Rules
1. Use evidence locking: include values/dates for key claims.
2. Mark missing sources explicitly (for example, Reddit credentials missing).
3. Separate broad ranking scans from final trade decisions:
- Use `scan_universe.py` for breadth across any symbols.
- Use `scan_forex_majors.py` only when explicit major-FX decomposition is required.
- Use `collect_symbol_context.py` for each symbol when final decisions are required.
4. Avoid unsupported certainty; include confidence and invalidation levels.
5. Do not collapse a multi-symbol request into a single short summary unless the user explicitly asks for summary-only output.

## References
1. Read `references/workflow.md` for agent sequencing and decision rules.
2. Read `references/output-schema.md` for output contract and required sections.
