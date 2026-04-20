#!/usr/bin/env python3
"""Collect no-API TradingAgents context for a single symbol.

Examples:
  python collect_symbol_context.py --symbol NVDA --trade-date 2026-02-15
  python collect_symbol_context.py --symbol NVDA --trade-date 2026-02-15 --include-trends
  python collect_symbol_context.py --symbol EURUSD=X --trade-date 2026-02-15
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests
import yfinance as yf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect single-symbol context as JSON")
    parser.add_argument("--symbol", required=True, help="Ticker or instrument symbol")
    parser.add_argument("--trade-date", required=True, help="Requested date (YYYY-MM-DD)")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=420,
        help="History window for technical metrics",
    )
    parser.add_argument(
        "--news-lookback-days",
        type=int,
        default=10,
        help="News filtering window in days before trade date",
    )
    parser.add_argument(
        "--include-trends",
        action="store_true",
        help="Attempt Google Trends pull via pytrends",
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


def compute_technical(df: pd.DataFrame) -> dict[str, Any]:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(index=df.index, data=0)

    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    ema10 = close.ewm(span=10, adjust=False).mean()

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

    boll_mid = close.rolling(20).mean()
    boll_std = close.rolling(20).std()
    boll_ub = boll_mid + 2 * boll_std
    boll_lb = boll_mid - 2 * boll_std

    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    atr14 = tr.rolling(14).mean()

    vwma20 = (close * volume).rolling(20).sum() / volume.rolling(20).sum()

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
        "boll_mid": to_float(boll_mid.iloc[-1]),
        "boll_ub": to_float(boll_ub.iloc[-1]),
        "boll_lb": to_float(boll_lb.iloc[-1]),
        "atr14": to_float(atr14.iloc[-1]),
        "vwma20": to_float(vwma20.iloc[-1]),
        "ret_5d_pct": to_float((close.iloc[-1] / close.iloc[-6] - 1) * 100) if len(close) > 6 else None,
        "ret_20d_pct": to_float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) > 21 else None,
        "ret_60d_pct": to_float((close.iloc[-1] / close.iloc[-61] - 1) * 100) if len(close) > 61 else None,
        "ret_120d_pct": to_float((close.iloc[-1] / close.iloc[-121] - 1) * 100) if len(close) > 121 else None,
        "avg_vol_20d": to_float(volume.tail(20).mean()) if len(volume) >= 20 else None,
    }


def get_options_snapshot(ticker: yf.Ticker, expirations_limit: int = 2) -> list[dict[str, Any]] | str:
    try:
        expirations = list(ticker.options) if ticker.options else []
    except Exception as exc:
        return f"options_unavailable: {exc}"

    if not expirations:
        return "options_unavailable"

    out = []
    for exp in expirations[:expirations_limit]:
        try:
            chain = ticker.option_chain(exp)
            calls = chain.calls
            puts = chain.puts
            total_call_vol = to_float(calls["volume"].fillna(0).sum()) if "volume" in calls.columns else 0.0
            total_put_vol = to_float(puts["volume"].fillna(0).sum()) if "volume" in puts.columns else 0.0
            total_call_oi = to_float(calls["openInterest"].fillna(0).sum()) if "openInterest" in calls.columns else 0.0
            total_put_oi = to_float(puts["openInterest"].fillna(0).sum()) if "openInterest" in puts.columns else 0.0
            avg_call_iv = (
                to_float(calls["impliedVolatility"].dropna().mean())
                if "impliedVolatility" in calls.columns and len(calls) > 0
                else None
            )
            avg_put_iv = (
                to_float(puts["impliedVolatility"].dropna().mean())
                if "impliedVolatility" in puts.columns and len(puts) > 0
                else None
            )

            out.append(
                {
                    "expiration": exp,
                    "put_call_ratio_volume": (total_put_vol / total_call_vol) if total_call_vol and total_call_vol > 0 else None,
                    "put_call_ratio_oi": (total_put_oi / total_call_oi) if total_call_oi and total_call_oi > 0 else None,
                    "avg_call_iv": avg_call_iv,
                    "avg_put_iv": avg_put_iv,
                    "total_call_volume": total_call_vol,
                    "total_put_volume": total_put_vol,
                    "total_call_oi": total_call_oi,
                    "total_put_oi": total_put_oi,
                }
            )
        except Exception as exc:
            out.append({"expiration": exp, "error": str(exc)})
    return out


def get_fundamentals(ticker: yf.Ticker) -> dict[str, Any] | str:
    fields = [
        "longName",
        "sector",
        "industry",
        "marketCap",
        "trailingPE",
        "forwardPE",
        "priceToBook",
        "trailingEps",
        "forwardEps",
        "beta",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
        "fiftyDayAverage",
        "twoHundredDayAverage",
        "totalRevenue",
        "grossProfits",
        "ebitda",
        "netIncomeToCommon",
        "profitMargins",
        "operatingMargins",
        "returnOnEquity",
        "returnOnAssets",
        "debtToEquity",
        "currentRatio",
        "bookValue",
        "freeCashflow",
        "dividendYield",
    ]
    try:
        info = ticker.info
        if not isinstance(info, dict):
            return "fundamentals_unavailable"
        return {k: info.get(k) for k in fields}
    except Exception as exc:
        return f"fundamentals_unavailable: {exc}"


def parse_news_item(article: dict[str, Any]) -> dict[str, Any]:
    content = article.get("content", {}) if isinstance(article, dict) else {}
    title = content.get("title") or article.get("title")
    provider = content.get("provider", {})
    publisher = provider.get("displayName") if isinstance(provider, dict) else article.get("publisher")
    url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
    url = url_obj.get("url") if isinstance(url_obj, dict) else article.get("link")
    date_raw = content.get("pubDate") or article.get("providerPublishTime")
    dt = None
    if isinstance(date_raw, str):
        try:
            dt = datetime.fromisoformat(date_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            dt = None
    elif isinstance(date_raw, (int, float)):
        dt = datetime.utcfromtimestamp(date_raw)
    return {
        "date": dt.strftime("%Y-%m-%d %H:%M") if dt else None,
        "title": title,
        "publisher": publisher,
        "url": url,
    }


def get_news(ticker: yf.Ticker, end_dt: datetime, lookback_days: int) -> list[dict[str, Any]] | str:
    try:
        news = ticker.get_news(count=30)
    except Exception as exc:
        return f"news_unavailable: {exc}"
    if not news:
        return []
    start_dt = end_dt - timedelta(days=lookback_days)
    out = []
    for article in news:
        parsed = parse_news_item(article)
        if parsed["date"] is None:
            continue
        article_dt = datetime.strptime(parsed["date"], "%Y-%m-%d %H:%M")
        if start_dt <= article_dt <= end_dt + timedelta(days=1):
            out.append(parsed)
    return out[:20]


def get_cnn_fear_greed() -> dict[str, Any] | str:
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.cnn.com/markets/fear-and-greed",
        "Origin": "https://www.cnn.com",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        fg = resp.json().get("fear_and_greed", {})
        return {
            "score": fg.get("score"),
            "rating": fg.get("rating"),
            "timestamp": fg.get("timestamp"),
        }
    except Exception as exc:
        return f"fear_greed_unavailable: {exc}"


def get_crypto_fear_greed() -> dict[str, Any] | str:
    url = "https://api.alternative.me/fng/?limit=1"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return "crypto_fear_greed_unavailable"
        row = data[0]
        return {
            "score": row.get("value"),
            "classification": row.get("value_classification"),
            "timestamp": row.get("timestamp"),
        }
    except Exception as exc:
        return f"crypto_fear_greed_unavailable: {exc}"


def get_macro_snapshot(end_date_str: str) -> dict[str, Any]:
    series = ["FEDFUNDS", "CPIAUCSL", "UNRATE", "GDP", "DGS10", "T10Y2Y", "UMCSENT"]
    out = {}
    end_date = pd.to_datetime(end_date_str)
    for s in series:
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
            df = pd.read_csv(url)
            df.columns = ["DATE", "VALUE"]
            df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
            df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
            df = df.dropna()
            df = df[df["DATE"] <= end_date]
            if df.empty:
                out[s] = {"error": "no_data"}
                continue
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else None
            out[s] = {
                "latest_date": latest["DATE"].strftime("%Y-%m-%d"),
                "latest_value": to_float(latest["VALUE"]),
                "prev_value": to_float(prev["VALUE"]) if prev is not None else None,
                "mom_change": to_float(latest["VALUE"] - prev["VALUE"]) if prev is not None else None,
            }
        except Exception as exc:
            out[s] = {"error": str(exc)}
    return out


def get_google_trends(term: str, start_dt: datetime, end_dt: datetime) -> dict[str, Any] | str:
    try:
        from pytrends.request import TrendReq
    except Exception as exc:
        return f"google_trends_unavailable: {exc}"

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        timeframe = f"{start_dt.strftime('%Y-%m-%d')} {end_dt.strftime('%Y-%m-%d')}"
        pytrends.build_payload([term], cat=0, timeframe=timeframe, geo="", gprop="")
        iot = pytrends.interest_over_time()
        if iot.empty or term not in iot.columns:
            return "google_trends_unavailable"
        series = iot[term]
        return {
            "term": term,
            "average": to_float(series.mean()),
            "peak": to_float(series.max()),
            "latest": to_float(series.iloc[-1]),
            "trend_change_recent_vs_early_pct": to_float(
                ((series.tail(3).mean() - series.head(3).mean()) / series.head(3).mean()) * 100
            )
            if to_float(series.head(3).mean()) not in (None, 0.0)
            else None,
        }
    except Exception as exc:
        return f"google_trends_unavailable: {exc}"


def maybe_get_sec_filings(symbol: str) -> dict[str, Any] | str:
    if not re.fullmatch(r"[A-Za-z]{1,6}", symbol):
        return "sec_filings_skipped_non_equity_symbol"
    ticker = symbol.upper()
    headers = {
        "User-Agent": "TradingAgents Skill research@local.dev",
        "Accept": "application/json",
    }
    try:
        tickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=20)
        tickers.raise_for_status()
        data = tickers.json()
        cik = None
        name = None
        for _, entry in data.items():
            if entry.get("ticker", "").upper() == ticker:
                cik = str(entry["cik_str"]).zfill(10)
                name = entry.get("title")
                break
        if not cik:
            return "sec_filings_unavailable_ticker_not_found"
        sub = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers, timeout=20)
        sub.raise_for_status()
        js = sub.json().get("filings", {}).get("recent", {})
        forms = js.get("form", [])
        dates = js.get("filingDate", [])
        acc = js.get("accessionNumber", [])
        docs = js.get("primaryDocument", [])
        out = []
        for i, form in enumerate(forms[:120]):
            if form in ("10-K", "10-Q", "8-K"):
                out.append(
                    {
                        "form": form,
                        "date": dates[i],
                        "accession": acc[i],
                        "document": docs[i],
                    }
                )
            if len(out) >= 12:
                break
        return {"ticker": ticker, "cik": cik, "name": name, "recent_filings": out}
    except Exception as exc:
        return f"sec_filings_unavailable: {exc}"


def main() -> None:
    args = parse_args()
    end_dt = last_market_day(args.trade_date)
    start_dt = end_dt - timedelta(days=args.lookback_days)
    symbol = args.symbol.strip()

    out: dict[str, Any] = {
        "symbol": symbol,
        "trade_date_requested": args.trade_date,
        "last_market_date": end_dt.strftime("%Y-%m-%d"),
        "data_start": start_dt.strftime("%Y-%m-%d"),
        "warnings": [],
    }

    df = yf.download(
        symbol,
        start=start_dt.strftime("%Y-%m-%d"),
        end=(end_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
    )
    if df.empty:
        out["error"] = "no_price_data"
        print(json.dumps(out, indent=2))
        return

    out["technical"] = compute_technical(df)
    out["last_ohlcv"] = {
        "open": to_float(df["Open"].iloc[-1]),
        "high": to_float(df["High"].iloc[-1]),
        "low": to_float(df["Low"].iloc[-1]),
        "close": to_float(df["Close"].iloc[-1]),
        "volume": to_float(df["Volume"].iloc[-1]) if "Volume" in df.columns else None,
    }

    ticker = yf.Ticker(symbol)
    out["options"] = get_options_snapshot(ticker)
    out["fundamentals"] = get_fundamentals(ticker)
    out["news"] = get_news(ticker, end_dt, args.news_lookback_days)
    out["macro"] = get_macro_snapshot(out["last_market_date"])
    out["fear_greed"] = get_cnn_fear_greed()
    out["crypto_fear_greed"] = get_crypto_fear_greed()
    out["sec_filings"] = maybe_get_sec_filings(symbol)

    if args.include_trends:
        trends_start = end_dt - timedelta(days=30)
        out["google_trends"] = get_google_trends(symbol.upper(), trends_start, end_dt)

    for key in ("options", "fundamentals", "news", "fear_greed", "crypto_fear_greed", "sec_filings"):
        if isinstance(out.get(key), str) and "unavailable" in out[key]:
            out["warnings"].append(f"{key}: {out[key]}")

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
