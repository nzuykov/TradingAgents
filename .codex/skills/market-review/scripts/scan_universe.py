#!/usr/bin/env python3
"""Scan any symbol universe and rank relative strength.

Examples:
  python scan_universe.py --symbols NVDA,SPY,NQ=F,EURUSD=X --trade-date 2026-02-15
  python scan_universe.py --symbols AAPL,MSFT,QQQ,SPY --trade-date 2026-02-15 --benchmark SPY
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a symbol universe and rank strength")
    parser.add_argument(
        "--symbols",
        required=True,
        help="Comma-separated symbols (for example: NVDA,SPY,NQ=F,EURUSD=X)",
    )
    parser.add_argument("--trade-date", required=True, help="Requested date (YYYY-MM-DD)")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=520,
        help="History window for metric calculations",
    )
    parser.add_argument(
        "--benchmark",
        default="",
        help="Optional benchmark symbol for relative return columns",
    )
    return parser.parse_args()


def to_float(value: Any) -> float | None:
    try:
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def last_market_day(date_str: str) -> datetime:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    while dt.weekday() >= 5:
        dt -= timedelta(days=1)
    return dt


def compute_metrics(df: pd.DataFrame) -> dict[str, Any]:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(index=df.index, data=0)

    ema10 = close.ewm(span=10, adjust=False).mean()
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macds = macd.ewm(span=9, adjust=False).mean()
    macdh = macd - macds

    chg = close.diff()
    gain = chg.clip(lower=0)
    loss = -chg.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    rsi14 = 100 - (100 / (1 + rs))

    tr = pd.concat([(high - low).abs(), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()

    ret20 = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) > 21 else np.nan
    ret60 = (close.iloc[-1] / close.iloc[-61] - 1) * 100 if len(close) > 61 else np.nan
    ret120 = (close.iloc[-1] / close.iloc[-121] - 1) * 100 if len(close) > 121 else np.nan

    trend_score = (
        (1 if close.iloc[-1] > sma50.iloc[-1] else -1)
        + (1 if sma50.iloc[-1] > sma200.iloc[-1] else -1)
        + (1 if macd.iloc[-1] > macds.iloc[-1] else -1)
        + (1 if rsi14.iloc[-1] > 50 else -1)
    )
    momentum_score = (0.5 * ret20) + (0.3 * ret60) + (0.2 * ret120)
    composite = trend_score + momentum_score

    return {
        "close": to_float(close.iloc[-1]),
        "ema10": to_float(ema10.iloc[-1]),
        "sma20": to_float(sma20.iloc[-1]),
        "sma50": to_float(sma50.iloc[-1]),
        "sma200": to_float(sma200.iloc[-1]),
        "macd": to_float(macd.iloc[-1]),
        "macds": to_float(macds.iloc[-1]),
        "macdh": to_float(macdh.iloc[-1]),
        "rsi14": to_float(rsi14.iloc[-1]),
        "atr14": to_float(atr14.iloc[-1]),
        "ret_5d_pct": to_float((close.iloc[-1] / close.iloc[-6] - 1) * 100) if len(close) > 6 else None,
        "ret_20d_pct": to_float(ret20),
        "ret_60d_pct": to_float(ret60),
        "ret_120d_pct": to_float(ret120),
        "avg_vol_20d": to_float(volume.tail(20).mean()) if len(volume) >= 20 else None,
        "distance_to_sma50_pct": to_float((close.iloc[-1] / sma50.iloc[-1] - 1) * 100),
        "distance_to_sma200_pct": to_float((close.iloc[-1] / sma200.iloc[-1] - 1) * 100),
        "trend_score": to_float(trend_score),
        "momentum_score": to_float(momentum_score),
        "composite_score": to_float(composite),
    }


def rank_by_key(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    clean = [r for r in rows if r.get(key) is not None]
    return sorted(clean, key=lambda x: x[key], reverse=True)


def main() -> None:
    args = parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    if len(symbols) < 2:
        raise SystemExit("Provide at least two symbols in --symbols")

    end_dt = last_market_day(args.trade_date)
    start_dt = end_dt - timedelta(days=args.lookback_days)

    out: dict[str, Any] = {
        "trade_date_requested": args.trade_date,
        "last_market_date": end_dt.strftime("%Y-%m-%d"),
        "symbols_requested": symbols,
        "symbols": {},
        "warnings": [],
    }

    closes: dict[str, pd.Series] = {}
    for symbol in symbols:
        try:
            df = yf.download(
                symbol,
                start=start_dt.strftime("%Y-%m-%d"),
                end=(end_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
                auto_adjust=True,
                progress=False,
                multi_level_index=False,
            )
        except Exception as exc:
            out["symbols"][symbol] = {"error": f"download_failed: {exc}"}
            continue

        if df.empty:
            out["symbols"][symbol] = {"error": "no_data"}
            continue

        metrics = compute_metrics(df)
        metrics["last_date"] = df.index[-1].strftime("%Y-%m-%d")
        out["symbols"][symbol] = metrics
        closes[symbol] = df["Close"].dropna()

    rows = [{"symbol": s, **v} for s, v in out["symbols"].items() if "error" not in v]
    out["ranking_by_composite"] = rank_by_key(rows, "composite_score")
    out["ranking_by_ret_20d"] = rank_by_key(rows, "ret_20d_pct")
    out["ranking_by_ret_60d"] = rank_by_key(rows, "ret_60d_pct")
    out["ranking_by_ret_120d"] = rank_by_key(rows, "ret_120d_pct")

    benchmark = args.benchmark.strip()
    if benchmark:
        if benchmark not in closes:
            out["warnings"].append(f"benchmark_not_in_symbols: {benchmark}")
        else:
            bench = closes[benchmark]
            rel = {}
            for symbol, series in closes.items():
                if symbol == benchmark:
                    continue
                joined = pd.concat([series, bench], axis=1, join="inner").dropna()
                if joined.empty:
                    continue
                joined.columns = ["asset", "bench"]
                ratio = joined["asset"] / joined["bench"]
                rel[symbol] = {
                    "ratio_last": to_float(ratio.iloc[-1]),
                    "ratio_ret_20d_pct": to_float((ratio.iloc[-1] / ratio.iloc[-21] - 1) * 100) if len(ratio) > 21 else None,
                    "ratio_ret_60d_pct": to_float((ratio.iloc[-1] / ratio.iloc[-61] - 1) * 100) if len(ratio) > 61 else None,
                    "ratio_ret_120d_pct": to_float((ratio.iloc[-1] / ratio.iloc[-121] - 1) * 100) if len(ratio) > 121 else None,
                    "ratio_above_sma50": bool(
                        len(ratio) >= 50 and ratio.iloc[-1] > ratio.rolling(50).mean().iloc[-1]
                    ),
                }
            out["relative_to_benchmark"] = {
                "benchmark": benchmark,
                "symbols": rel,
                "ranking_by_ratio_ret_20d": sorted(
                    [
                        {"symbol": s, "ratio_ret_20d_pct": v.get("ratio_ret_20d_pct")}
                        for s, v in rel.items()
                        if v.get("ratio_ret_20d_pct") is not None
                    ],
                    key=lambda x: x["ratio_ret_20d_pct"],
                    reverse=True,
                ),
            }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
