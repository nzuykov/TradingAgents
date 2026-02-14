"""YFinance options chain data."""

import yfinance as yf
from datetime import datetime
from typing import Annotated


def get_options_chain_yfinance(
    symbol: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve options chain data for a ticker: calls, puts, IV, volume,
    open interest, and put/call ratio.

    Args:
        symbol: Ticker symbol (e.g. "AAPL")
        curr_date: Current date in yyyy-mm-dd format

    Returns:
        Formatted string with options chain summary
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        expirations = ticker.options

        if not expirations:
            return f"No options data available for {symbol}"

        # Pick nearest expiration
        nearest_exp = expirations[0]
        # Also get a further-out expiration if available
        further_exp = expirations[min(2, len(expirations) - 1)]

        report = f"# Options Chain for {symbol.upper()} (as of {curr_date})\n\n"

        for exp_date in [nearest_exp, further_exp]:
            if exp_date == further_exp and further_exp == nearest_exp:
                continue

            chain = ticker.option_chain(exp_date)
            calls = chain.calls
            puts = chain.puts

            report += f"## Expiration: {exp_date}\n\n"

            # Summary stats
            total_call_vol = calls["volume"].sum() if "volume" in calls.columns else 0
            total_put_vol = puts["volume"].sum() if "volume" in puts.columns else 0
            total_call_oi = calls["openInterest"].sum() if "openInterest" in calls.columns else 0
            total_put_oi = puts["openInterest"].sum() if "openInterest" in puts.columns else 0

            pc_ratio_vol = (total_put_vol / total_call_vol) if total_call_vol > 0 else float("inf")
            pc_ratio_oi = (total_put_oi / total_call_oi) if total_call_oi > 0 else float("inf")

            report += f"**Put/Call Ratio (Volume):** {pc_ratio_vol:.2f}\n"
            report += f"**Put/Call Ratio (Open Interest):** {pc_ratio_oi:.2f}\n"
            report += f"**Total Call Volume:** {total_call_vol:,.0f} | **Total Put Volume:** {total_put_vol:,.0f}\n"
            report += f"**Total Call OI:** {total_call_oi:,.0f} | **Total Put OI:** {total_put_oi:,.0f}\n\n"

            # Top calls by volume
            report += "### Top 5 Calls by Volume\n"
            report += "| Strike | Last | Bid | Ask | IV | Volume | OI |\n"
            report += "|--------|------|-----|-----|----|--------|----|\n"
            top_calls = calls.nlargest(5, "volume") if "volume" in calls.columns else calls.head(5)
            for _, row in top_calls.iterrows():
                iv = f"{row.get('impliedVolatility', 0):.2%}" if row.get("impliedVolatility") else "N/A"
                report += (
                    f"| {row.get('strike', 'N/A')} "
                    f"| {row.get('lastPrice', 'N/A')} "
                    f"| {row.get('bid', 'N/A')} "
                    f"| {row.get('ask', 'N/A')} "
                    f"| {iv} "
                    f"| {row.get('volume', 'N/A')} "
                    f"| {row.get('openInterest', 'N/A')} |\n"
                )

            # Top puts by volume
            report += "\n### Top 5 Puts by Volume\n"
            report += "| Strike | Last | Bid | Ask | IV | Volume | OI |\n"
            report += "|--------|------|-----|-----|----|--------|----|\n"
            top_puts = puts.nlargest(5, "volume") if "volume" in puts.columns else puts.head(5)
            for _, row in top_puts.iterrows():
                iv = f"{row.get('impliedVolatility', 0):.2%}" if row.get("impliedVolatility") else "N/A"
                report += (
                    f"| {row.get('strike', 'N/A')} "
                    f"| {row.get('lastPrice', 'N/A')} "
                    f"| {row.get('bid', 'N/A')} "
                    f"| {row.get('ask', 'N/A')} "
                    f"| {iv} "
                    f"| {row.get('volume', 'N/A')} "
                    f"| {row.get('openInterest', 'N/A')} |\n"
                )

            # IV summary
            if "impliedVolatility" in calls.columns:
                avg_call_iv = calls["impliedVolatility"].mean()
                avg_put_iv = puts["impliedVolatility"].mean()
                report += f"\n**Avg Call IV:** {avg_call_iv:.2%} | **Avg Put IV:** {avg_put_iv:.2%}\n"
                iv_skew = avg_put_iv - avg_call_iv
                report += f"**IV Skew (Put - Call):** {iv_skew:.2%}\n"

            report += "\n---\n\n"

        # Available expirations summary
        report += f"**All Available Expirations ({len(expirations)}):** {', '.join(expirations[:8])}"
        if len(expirations) > 8:
            report += f" ... (+{len(expirations) - 8} more)"
        report += "\n"

        return report

    except Exception as e:
        return f"Error fetching options data for {symbol}: {str(e)}"
