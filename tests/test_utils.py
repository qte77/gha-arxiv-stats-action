"""Tests for get_api_response() retry behavior and parse_arxiv_url() in src/utils.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.utils import get_api_response, parse_arxiv_url


def _make_response(data=b"ok"):
    """Create a mock requests.Response with successful raise_for_status."""
    resp = MagicMock()
    resp.content = data
    resp.raise_for_status = MagicMock()
    return resp


def test_retries_on_http_error():
    """Fails 2x with ConnectionError then succeeds — should return data."""
    resp = _make_response(b"arxiv data")
    side_effects = [
        requests.ConnectionError("transient"),
        requests.ConnectionError("transient"),
        resp,
    ]
    with patch("src.utils.requests.get", side_effect=side_effects) as mock_get:
        result = get_api_response("https://export.arxiv.org/api/query?id_list=1234")
    assert result == b"arxiv data"
    assert mock_get.call_count == 3


def test_raises_after_max_retries():
    """Always fails with ConnectionError — should raise RuntimeError after exhaustion."""
    with patch("src.utils.requests.get", side_effect=requests.ConnectionError("persistent")):
        with pytest.raises(RuntimeError):
            get_api_response("https://export.arxiv.org/api/query?id_list=1234")


def test_rejects_non_https():
    """http:// URL should raise ValueError immediately, never calling requests.get."""
    with patch("src.utils.requests.get") as mock_get:
        with pytest.raises(ValueError):
            get_api_response("http://export.arxiv.org/api/query?id_list=1234")
    assert mock_get.call_count == 0


def test_success_no_retry():
    """Single 200 response — requests.get called exactly once."""
    resp = _make_response(b"success")
    with patch("src.utils.requests.get", return_value=resp) as mock_get:
        result = get_api_response("https://export.arxiv.org/api/query?id_list=1234")
    assert result == b"success"
    assert mock_get.call_count == 1


def test_parse_arxiv_url_happy_path():
    """Standard arxiv URL parses into (idv, rawid, version)."""
    idv, rawid, version = parse_arxiv_url("http://arxiv.org/abs/1512.08756v2")
    assert idv == "1512.08756v2"
    assert rawid == "1512.08756"
    assert version == 2


def test_parse_arxiv_url_rejects_missing_v():
    """ID without version separator raises ValueError naming the malformed input."""
    with pytest.raises(ValueError, match="malformed arxiv id"):
        parse_arxiv_url("http://arxiv.org/abs/1512.08756")


def test_parse_arxiv_url_rejects_no_slash():
    """URL without / raises ValueError with 'bad url' message."""
    with pytest.raises(ValueError, match="bad url"):
        parse_arxiv_url("not-a-url")


def test_parse_arxiv_url_rejects_non_numeric_version():
    """Non-numeric version raises ValueError with helpful message, not bare int() error."""
    with pytest.raises(ValueError, match="malformed arxiv id"):
        parse_arxiv_url("http://arxiv.org/abs/1512.08756vabc")


def test_parse_arxiv_url_rejects_multiple_v():
    """ID with multiple 'v' separators raises ValueError with helpful message."""
    with pytest.raises(ValueError, match="malformed arxiv id"):
        parse_arxiv_url("http://arxiv.org/abs/1512.08756v2v3")
