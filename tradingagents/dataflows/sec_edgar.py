"""SEC EDGAR filings data."""

import requests
from typing import Annotated


def get_sec_filings_edgar(
    ticker: Annotated[str, "ticker symbol"],
    filing_type: Annotated[str, "filing type e.g. 10-K, 10-Q, 8-K"] = "10-K",
    limit: Annotated[int, "max number of filings to return"] = 3,
) -> str:
    """
    Fetch recent SEC filings for a ticker from EDGAR.

    No API key needed. Free public API with User-Agent header.

    Args:
        ticker: Ticker symbol (e.g. "AAPL")
        filing_type: Filing type filter (default "10-K")
        limit: Max number of filings (default 3)

    Returns:
        Formatted string with filing summaries
    """
    headers = {
        "User-Agent": "TradingAgents Research Bot research@tradingagents.dev",
        "Accept": "application/json",
    }

    try:
        # Step 1: Get CIK from ticker
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(tickers_url, headers=headers, timeout=10)
        resp.raise_for_status()
        tickers_data = resp.json()

        cik = None
        company_name = None
        ticker_upper = ticker.upper()
        for entry in tickers_data.values():
            if entry.get("ticker", "").upper() == ticker_upper:
                cik = str(entry["cik_str"]).zfill(10)
                company_name = entry.get("title", ticker_upper)
                break

        if not cik:
            return f"Ticker {ticker} not found in SEC EDGAR database"

        # Step 2: Get filings
        filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        resp = requests.get(filings_url, headers=headers, timeout=10)
        resp.raise_for_status()
        filings_data = resp.json()

        recent = filings_data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        descriptions = recent.get("primaryDocDescription", [])
        docs = recent.get("primaryDocument", [])

        report = f"# SEC EDGAR Filings: {company_name} ({ticker_upper})\n"
        report += f"**CIK:** {cik}\n\n"

        # Filter by filing type
        filtered = []
        for i in range(len(forms)):
            if filing_type.upper() in forms[i].upper():
                filtered.append(i)
            if len(filtered) >= limit:
                break

        if not filtered:
            # Fallback: show most recent filings of any type
            report += f"No {filing_type} filings found. Showing most recent filings:\n\n"
            filtered = list(range(min(limit, len(forms))))

        for idx in filtered:
            form = forms[idx] if idx < len(forms) else "N/A"
            date = dates[idx] if idx < len(dates) else "N/A"
            accession = accessions[idx] if idx < len(accessions) else "N/A"
            desc = descriptions[idx] if idx < len(descriptions) else "N/A"
            doc = docs[idx] if idx < len(docs) else ""

            accession_clean = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_clean}/{doc}"

            report += f"## {form} — Filed {date}\n"
            report += f"**Description:** {desc}\n"
            report += f"**Accession:** {accession}\n"
            report += f"**URL:** {filing_url}\n"

            # Try to fetch filing summary/header
            try:
                doc_resp = requests.get(filing_url, headers=headers, timeout=10)
                if doc_resp.status_code == 200:
                    text = doc_resp.text
                    # Extract first ~2000 chars of text content (skip HTML tags)
                    import re
                    clean_text = re.sub(r"<[^>]+>", " ", text)
                    clean_text = re.sub(r"\s+", " ", clean_text).strip()
                    if len(clean_text) > 2000:
                        clean_text = clean_text[:2000] + "..."
                    report += f"\n**Filing Excerpt:**\n{clean_text}\n"
            except Exception:
                report += "\n(Could not fetch filing content)\n"

            report += "\n---\n\n"

        # Filing frequency summary
        filing_types_count = {}
        for f in forms[:50]:
            filing_types_count[f] = filing_types_count.get(f, 0) + 1

        report += "## Recent Filing Activity (last 50)\n"
        for ftype, count in sorted(filing_types_count.items(), key=lambda x: -x[1])[:10]:
            report += f"  {ftype}: {count}\n"

        return report

    except requests.exceptions.RequestException as e:
        return f"Error fetching SEC EDGAR data for {ticker}: {str(e)}"
    except Exception as e:
        return f"Error processing SEC data for {ticker}: {str(e)}"
