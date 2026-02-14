"""FRED (Federal Reserve Economic Data) macro indicators."""

import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated


def get_macro_indicators_fred(
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Fetch key macroeconomic indicators from FRED in one call:
    Fed Funds Rate, CPI, Unemployment, GDP, 10Y Treasury.

    Requires FRED_API_KEY environment variable.

    Args:
        curr_date: Current date in yyyy-mm-dd format

    Returns:
        Formatted string with macro indicator data
    """
    try:
        from fredapi import Fred
    except ImportError:
        return "Error: fredapi package not installed. Run: pip install fredapi"

    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        return "Error: FRED_API_KEY environment variable not set. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"

    try:
        fred = Fred(api_key=api_key)

        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        # Look back 2 years for context
        start_dt = curr_dt - relativedelta(years=2)
        start_date = start_dt.strftime("%Y-%m-%d")

        series_map = {
            "FEDFUNDS": ("Federal Funds Rate (%)", "monthly"),
            "CPIAUCSL": ("CPI (All Urban Consumers)", "monthly"),
            "UNRATE": ("Unemployment Rate (%)", "monthly"),
            "GDP": ("GDP (Billions $)", "quarterly"),
            "DGS10": ("10-Year Treasury Yield (%)", "daily"),
            "T10Y2Y": ("10Y-2Y Treasury Spread (%)", "daily"),
            "UMCSENT": ("U. of Michigan Consumer Sentiment", "monthly"),
        }

        report = f"# Macroeconomic Indicators (as of {curr_date})\n\n"

        for series_id, (description, freq) in series_map.items():
            try:
                data = fred.get_series(
                    series_id,
                    observation_start=start_date,
                    observation_end=curr_date,
                )

                if data.empty:
                    report += f"## {description} ({series_id})\nNo data available\n\n"
                    continue

                # Drop NaN values
                data = data.dropna()
                if data.empty:
                    report += f"## {description} ({series_id})\nNo data available\n\n"
                    continue

                latest_value = data.iloc[-1]
                latest_date = data.index[-1].strftime("%Y-%m-%d")

                report += f"## {description} ({series_id})\n"
                report += f"**Latest:** {latest_value:.2f} (as of {latest_date})\n"

                # Show recent trend (last few data points)
                recent = data.tail(6)
                report += "**Recent Trend:**\n"
                for date_idx, value in recent.items():
                    report += f"  {date_idx.strftime('%Y-%m-%d')}: {value:.2f}\n"

                # Calculate change
                if len(data) >= 2:
                    prev_value = data.iloc[-2]
                    change = latest_value - prev_value
                    pct_change = (change / abs(prev_value) * 100) if prev_value != 0 else 0
                    direction = "up" if change > 0 else "down"
                    report += f"**Change:** {change:+.2f} ({pct_change:+.2f}%, {direction})\n"

                # Year-over-year if enough data
                one_year_ago = curr_dt - relativedelta(years=1)
                yoy_data = data[data.index <= one_year_ago]
                if not yoy_data.empty:
                    yoy_value = yoy_data.iloc[-1]
                    yoy_change = latest_value - yoy_value
                    yoy_pct = (yoy_change / abs(yoy_value) * 100) if yoy_value != 0 else 0
                    report += f"**YoY Change:** {yoy_change:+.2f} ({yoy_pct:+.2f}%)\n"

                report += "\n"

            except Exception as e:
                report += f"## {description} ({series_id})\nError: {str(e)}\n\n"

        return report

    except Exception as e:
        return f"Error connecting to FRED API: {str(e)}"
