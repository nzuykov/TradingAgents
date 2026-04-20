#!/usr/bin/env python3
"""Scan major FX pairs and compute pair + currency relative strength.

Example:
  python scan_forex_majors.py --trade-date 2026-02-15
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
    parser = argparse.ArgumentParser(description="Scan major FX pairs and rank strength")
    parser.add_argument("--trade-date", required=True, help="Requested date (YYYY-MM-DD)")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=520,
        help="History window for pair calculations",
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


def compute_pair_metrics(df: pd.DataFrame) -> dict[str, Any]:
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


def main() -> None:
    args = parse_args()
    end_dt = last_market_day(args.trade_date)
    start_dt = end_dt - timedelta(days=args.lookback_days)

    pairs = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "USDCHF": "USDCHF=X",
        "AUDUSD": "AUDUSD=X",
        "NZDUSD": "NZDUSD=X",
        "USDCAD": "USDCAD=X",
    }

    pair_data: dict[str, dict[str, Any]] = {}
    closes: dict[str, pd.Series] = {}

    for pair_name, ticker in pairs.items():
        df = yf.download(
            ticker,
            start=start_dt.strftime("%Y-%m-%d"),
            end=(end_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            auto_adjust=True,
            progress=False,
            multi_level_index=False,
        )
        if df.empty:
            pair_data[pair_name] = {"ticker": ticker, "error": "no_data"}
            continue
        metrics = compute_pair_metrics(df)
        metrics["ticker"] = ticker
        metrics["last_date"] = df.index[-1].strftime("%Y-%m-%d")
        pair_data[pair_name] = metrics
        closes[pair_name] = df["Close"].copy()

    ranked_pairs = sorted(
        [{"pair": name, **vals} for name, vals in pair_data.items() if "error" not in vals],
        key=lambda x: x["composite_score"],
        reverse=True,
    )

    currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "NZD", "CAD"]
    index = {c: i for i, c in enumerate(currencies)}
    pair_defs = [
        ("EURUSD", "EUR", "USD"),
        ("GBPUSD", "GBP", "USD"),
        ("AUDUSD", "AUD", "USD"),
        ("NZDUSD", "NZD", "USD"),
        ("USDJPY", "USD", "JPY"),
        ("USDCHF", "USD", "CHF"),
        ("USDCAD", "USD", "CAD"),
    ]

    strength_scores: dict[str, dict[str, float]] = {}
    for horizon in (20, 60, 120):
        equations = []
        rhs = []
        for pair, base, quote in pair_defs:
            if pair not in closes:
                continue
            s = closes[pair].dropna()
            if len(s) <= horizon:
                continue
            ret = np.log(s.iloc[-1] / s.iloc[-(horizon + 1)])
            row = np.zeros(len(currencies))
            row[index[base]] = 1
            row[index[quote]] = -1
            equations.append(row)
            rhs.append(ret)
        if len(equations) < 5:
            continue
        a = np.array(equations)
        y = np.array(rhs)
        constraint = np.ones((1, len(currencies)))
        a2 = np.vstack([a, constraint])
        y2 = np.concatenate([y, [0.0]])
        x, _, _, _ = np.linalg.lstsq(a2, y2, rcond=None)
        strength_scores[f"{horizon}d"] = {c: float(x[index[c]]) for c in currencies}

    currency_ranking = {}
    for horizon, scores in strength_scores.items():
        currency_ranking[horizon] = sorted(
            [{"currency": c, "score": s} for c, s in scores.items()],
            key=lambda x: x["score"],
            reverse=True,
        )

    out = {
        "trade_date_requested": args.trade_date,
        "last_market_date": end_dt.strftime("%Y-%m-%d"),
        "pairs": pair_data,
        "pair_ranking_by_composite": ranked_pairs,
        "currency_strength_scores": strength_scores,
        "currency_ranking": currency_ranking,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
