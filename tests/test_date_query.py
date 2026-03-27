"""Tests for arXiv submittedDate range query building."""

import pytest

from src.utils import build_date_query


class TestBuildDateQuery:
    """Tests for build_date_query()."""

    def test_build_date_query_with_from_and_to(self):
        """Builds submittedDate range when both dates provided."""
        result = build_date_query(date_from="2024-12-09", date_to="2024-12-15")
        assert "submittedDate:" in result
        assert "202412090000" in result
        assert "202412152359" in result

    def test_build_date_query_with_from_only(self):
        """Uses today as end date when only date_from provided."""
        result = build_date_query(date_from="2024-12-09")
        assert "submittedDate:" in result
        assert "202412090000" in result

    def test_build_date_query_returns_empty_when_no_dates(self):
        """Returns empty string when no dates provided."""
        result = build_date_query()
        assert result == ""

    def test_build_date_query_rejects_invalid_date_format(self):
        """Raises ValueError for non-YYYY-MM-DD format."""
        with pytest.raises(ValueError, match="date"):
            build_date_query(date_from="12/09/2024")

    def test_build_date_query_format_is_arxiv_compatible(self):
        """Output follows arXiv submittedDate query syntax."""
        result = build_date_query(date_from="2024-12-09", date_to="2024-12-15")
        # arXiv format: +AND+submittedDate:[YYYYMMDDHHMM+TO+YYYYMMDDHHMM]
        assert "+AND+submittedDate:[" in result
        assert "+TO+" in result
        assert result.endswith("]")
