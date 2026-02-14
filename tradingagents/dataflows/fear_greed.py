"""CNN Fear & Greed Index data."""

import requests
from typing import Annotated


def get_fear_greed_index_cnn(
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Get the CNN Fear & Greed Index score (0-100) and components.
    0 = Extreme Fear, 100 = Extreme Greed.

    No API key needed. Uses unofficial CNN endpoint.

    Args:
        curr_date: Current date in yyyy-mm-dd format

    Returns:
        Formatted string with Fear & Greed data
    """
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        report = f"# CNN Fear & Greed Index (as of {curr_date})\n\n"

        # Current score
        fear_greed = data.get("fear_and_greed", {})
        score = fear_greed.get("score")
        rating = fear_greed.get("rating")
        timestamp = fear_greed.get("timestamp", "")

        if score is not None:
            report += f"**Current Score:** {score:.1f} / 100\n"
            report += f"**Rating:** {rating}\n"
            report += f"**Updated:** {timestamp}\n\n"

            # Interpret the score
            if score <= 25:
                interpretation = "EXTREME FEAR - Markets are very fearful. Historically, this can be a buying opportunity (contrarian signal)."
            elif score <= 45:
                interpretation = "FEAR - Markets are nervous. Caution is warranted but opportunities may exist."
            elif score <= 55:
                interpretation = "NEUTRAL - Markets are balanced between fear and greed."
            elif score <= 75:
                interpretation = "GREED - Markets are getting greedy. Consider taking some profits or being cautious with new positions."
            else:
                interpretation = "EXTREME GREED - Markets are extremely greedy. High risk of correction. Strong contrarian sell signal."

            report += f"**Interpretation:** {interpretation}\n\n"

        # Historical comparison
        fear_greed_hist = data.get("fear_and_greed_historical", {})
        if fear_greed_hist:
            report += "## Historical Comparison\n"
            for period_key in ["previousClose", "oneWeekAgo", "oneMonthAgo", "oneYearAgo"]:
                period_data = fear_greed_hist.get(period_key, {})
                if period_data:
                    p_score = period_data.get("score")
                    p_rating = period_data.get("rating")
                    if p_score is not None:
                        label = period_key.replace("previousClose", "Previous Close").replace("oneWeekAgo", "1 Week Ago").replace("oneMonthAgo", "1 Month Ago").replace("oneYearAgo", "1 Year Ago")
                        report += f"  **{label}:** {p_score:.1f} ({p_rating})\n"
            report += "\n"

        return report

    except requests.exceptions.RequestException as e:
        return f"Error fetching Fear & Greed Index: {str(e)}"
    except Exception as e:
        return f"Error processing Fear & Greed data: {str(e)}"
