"""Tests for Semantic Scholar citation enrichment in app/citations.py."""
import sys
import os
import json
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import app.citations as citations_module
from app.citations import get_citations, enrich_row


def _make_response(data: dict):
    """Create a mock HTTP response returning JSON bytes."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(data).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_get_citations_success():
    """Returns correct dict when API responds with citation data."""
    payload = {"citationCount": 42, "referenceCount": 10, "influentialCitationCount": 5}
    resp = _make_response(payload)
    with patch("app.citations.urlopen", return_value=resp):
        result = get_citations("2406.04221")
    assert result == {"citation_count": 42, "reference_count": 10, "influential_count": 5}


def test_get_citations_not_found():
    """Returns zero-filled dict on 404 HTTPError (graceful fallback)."""
    http_error = HTTPError(url="", code=404, msg="Not Found", hdrs={}, fp=None)
    with patch("app.citations.urlopen", side_effect=http_error):
        result = get_citations("9999.99999")
    assert result == {"citation_count": 0, "reference_count": 0, "influential_count": 0}


def test_get_citations_respects_rate_limit():
    """Calls time.sleep between successive requests to respect 1 RPS limit."""
    payload = {"citationCount": 1, "referenceCount": 0, "influentialCitationCount": 0}
    resp = _make_response(payload)

    # Reset module-level _last_call so first call does NOT sleep
    citations_module._last_call = 0.0

    with patch("app.citations.urlopen", return_value=resp), \
         patch("app.citations.time") as mock_time:
        mock_time.time.return_value = 0.0  # first call: elapsed = 0 - 0 = 0, sleep 1.0
        get_citations("2406.00001")
        mock_time.time.return_value = 0.5  # second call: elapsed = 0.5 - 0 = 0.5 < 1.0
        get_citations("2406.00002")

    mock_time.sleep.assert_called()


def test_enrich_row():
    """Appends citation_count, reference_count, influential_count to a CSV row."""
    row = ["2024-06-06T16:20:07Z", 23, "2024-06-07T10:00:00Z", "2406.04221", 1, "'A Title'"]
    citations = {"citation_count": 42, "reference_count": 10, "influential_count": 5}
    result = enrich_row(row, citations)
    assert result == row + [42, 10, 5]
    assert len(result) == len(row) + 3
