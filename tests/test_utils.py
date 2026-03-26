"""Tests for get_api_response() retry behavior in app/utils.py."""
import sys
import os
from unittest.mock import patch, MagicMock
from urllib.error import URLError
import pytest

# Mock feedparser before importing app.utils (feedparser may not be installed in test env)
_feedparser_mock = MagicMock()
sys.modules.setdefault("feedparser", _feedparser_mock)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.utils import get_api_response


def _make_response(data=b"ok"):
    """Create a mock HTTP response with status 200."""
    resp = MagicMock()
    resp.status = 200
    resp.read.return_value = data
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_retries_on_http_error():
    """Fails 2x with URLError then succeeds — should return data."""
    resp = _make_response(b"arxiv data")
    side_effects = [URLError("transient"), URLError("transient"), resp]
    with patch("app.utils.urlopen", side_effect=side_effects) as mock_urlopen:
        result = get_api_response("https://export.arxiv.org/api/query?id_list=1234")
    assert result == b"arxiv data"
    assert mock_urlopen.call_count == 3


def test_raises_after_max_retries():
    """Always fails with URLError — should raise RuntimeError after exhaustion."""
    with patch("app.utils.urlopen", side_effect=URLError("persistent")):
        with pytest.raises(RuntimeError):
            get_api_response("https://export.arxiv.org/api/query?id_list=1234")


def test_rejects_non_https():
    """http:// URL should raise ValueError immediately (no retry)."""
    with pytest.raises(ValueError):
        get_api_response("http://export.arxiv.org/api/query?id_list=1234")


def test_success_no_retry():
    """Single 200 response — urlopen called exactly once."""
    resp = _make_response(b"success")
    with patch("app.utils.urlopen", return_value=resp) as mock_urlopen:
        result = get_api_response("https://export.arxiv.org/api/query?id_list=1234")
    assert result == b"success"
    assert mock_urlopen.call_count == 1
