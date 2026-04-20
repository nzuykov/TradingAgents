# Workflow Reference

## Scope
Use this skill for no-API TradingAgents-style analysis across any tradable symbol set where role sequencing matters more than direct multi-model orchestration.
For multi-symbol requests, run the full role sequence independently for each symbol.

## Multi-Symbol Default
1. Treat a basket request as N independent deep reports plus one optional cross-asset ranking section.
2. Do not replace per-symbol deep reports with a single aggregate summary unless the user asks for summary-only.
3. Keep role order and output depth identical across all symbols.

## Role Sequence
Run the following sequence without skipping roles unless the user explicitly requests fewer analysts.
Use the same sequence for equities, indexes, futures, forex, and mixed universes.

1. Market Analyst
2. Social Analyst
3. News Analyst
4. Fundamentals or Macro Analyst
5. Bull Researcher
6. Bear Researcher
7. Research Manager
8. Trader
9. Aggressive Risk Analyst
10. Conservative Risk Analyst
11. Neutral Risk Analyst
12. Risk Judge

## Role Expectations
1. Market Analyst: summarize trend, momentum, volatility, and options positioning.
2. Social Analyst: summarize interest/sentiment proxies and data gaps.
3. News Analyst: summarize event flow and policy/regulatory implications.
4. Fundamentals/Macro Analyst: summarize financial quality for equities or macro context for FX.
5. Bull and Bear Researchers: produce opposing theses with explicit counters.
6. Research Manager: produce an actionable investment plan and rationale.
7. Trader: convert plan into concrete entry/risk/target logic.
8. Risk Analysts: challenge sizing, tail risk, and scenario asymmetry.
9. Risk Judge: publish final BUY/HOLD/SELL and confidence.

## Debate Depth
Use user-selected depth as rounds:
1. Shallow: 1 round
2. Medium: 3 rounds
3. Full/Deep: 5 rounds

## Evidence Locking
1. Attach date and value to each critical claim.
2. Mark unavailable data explicitly.
3. Avoid conclusions without at least two independent signals.
