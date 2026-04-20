# Output Schema

Use this structure in final responses.

## Single Symbol
1. Run Setup
- symbol
- requested date
- last market date used

2. Analyst Team
- market_report
- sentiment_report
- news_report
- fundamentals_report

3. Research Team
- investment_debate_state
- investment_plan

4. Trader
- trader_investment_plan

5. Risk Team
- risk_debate_state
- final_trade_decision

6. Signal
- decision: BUY|HOLD|SELL
- confidence (0-100)
- invalidation levels

## Multi Symbol (Default for Basket Requests)
1. Basket Setup
- symbols requested
- ticker mappings used
- requested date
- last market date used

2. Optional Broad Scan
- composite ranking
- horizon rankings (20d, 60d, 120d)
- relative-strength vs chosen benchmark

3. Per-Symbol Deep Report (repeat for each symbol)
- Run Setup
- Analyst Team
- Research Team
- Trader
- Risk Team
- Signal

## Broad Scan (Any Universe)
1. Symbol ranking by composite score
2. Horizon return rankings (20d, 60d, 120d)
3. Directional interpretation
4. Missing-data warnings

## Broad Scan (FX Majors Optional)
1. Pair ranking by composite score
2. Currency strength ranking (20d, 60d, 120d)

## Minimum Required Fields
1. Last market date used.
2. At least one trend metric and one momentum metric.
3. Explicit confidence and key risks.
4. For multi-symbol requests, include one full deep report per symbol.
