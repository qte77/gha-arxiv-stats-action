"""Semantic Scholar citation enrichment for arxiv paper IDs."""
import json
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_BASE = "https://api.semanticscholar.org/graph/v1/paper"
FIELDS = "citationCount,referenceCount,influentialCitationCount"
_last_call = 0.0


def get_citations(arxiv_id: str) -> dict:
    """Fetch citation counts from Semantic Scholar.

    Rate limited to 1 RPS. Returns zeros on error.

    Args:
        arxiv_id: Raw arxiv ID without version (e.g. '2406.04221').

    Returns:
        Dict with citation_count, reference_count, influential_count.
    """
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    url = f"{API_BASE}/ARXIV:{arxiv_id}?fields={FIELDS}"
    try:
        req = Request(url)
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            _last_call = time.time()
            return {
                "citation_count": data.get("citationCount", 0),
                "reference_count": data.get("referenceCount", 0),
                "influential_count": data.get("influentialCitationCount", 0),
            }
    except (HTTPError, URLError, json.JSONDecodeError):
        _last_call = time.time()
        return {"citation_count": 0, "reference_count": 0, "influential_count": 0}


def enrich_row(row: list, citations: dict) -> list:
    """Append citation columns to an existing CSV row.

    Args:
        row: Existing CSV row as a list.
        citations: Dict with citation_count, reference_count, influential_count.

    Returns:
        New list with three citation columns appended.
    """
    return row + [citations["citation_count"], citations["reference_count"], citations["influential_count"]]
