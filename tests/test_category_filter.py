"""Tests for category filtering and categories column in CSV output."""

from unittest.mock import MagicMock, patch

from src.utils import extract_categories, get_parsed_output


class TestExtractCategories:
    """Tests for extract_categories()."""

    def test_extract_categories_from_tags(self):
        """Extracts category terms from feedparser tags list."""
        tags = [{"term": "cs.CV"}, {"term": "cs.LG"}, {"term": "math.OC"}]
        result = extract_categories(tags)
        assert result == ["cs.CV", "cs.LG", "math.OC"]

    def test_extract_categories_empty_tags(self):
        """Returns empty list when no tags present."""
        assert extract_categories([]) == []
        assert extract_categories(None) == []


class TestGetParsedOutputCategories:
    """Tests for category filtering and column in get_parsed_output."""

    def _make_entry(self, arxiv_id, published, tags):
        """Create a mock feedparser entry."""
        entry = MagicMock()
        entry.keys.return_value = ["id", "published", "updated", "title", "tags"]
        entry.__getitem__ = lambda self, key: {
            "id": f"http://arxiv.org/abs/{arxiv_id}v1",
            "published": published,
            "updated": published,
            "title": "Test Paper",
            "tags": tags,
        }[key]
        return entry

    def test_parsed_output_includes_categories_column(self):
        """Output rows include categories as last column."""
        entry = self._make_entry(
            "2603.00001",
            "2026-03-23T17:00:00Z",
            [{"term": "cs.CV"}, {"term": "cs.LG"}],
        )
        mock_parsed = MagicMock()
        mock_parsed.entries = [entry]

        with patch("src.utils.parse", return_value=mock_parsed):
            result = get_parsed_output(b"mock")

        key = list(result.keys())[0]
        row = result[key][0]
        # Last column should be categories string
        assert "cs.CV" in row[-1]
        assert "cs.LG" in row[-1]

    def test_parsed_output_filters_by_allowed_categories(self):
        """Papers without any matching category are excluded."""
        # Paper with matching category
        entry_match = self._make_entry(
            "2603.00001",
            "2026-03-23T17:00:00Z",
            [{"term": "cs.CV"}, {"term": "math.OC"}],
        )
        # Paper with NO matching category
        entry_no_match = self._make_entry(
            "2603.00002",
            "2026-03-23T18:00:00Z",
            [{"term": "math.OC"}, {"term": "stat.ML"}],
        )
        mock_parsed = MagicMock()
        mock_parsed.entries = [entry_match, entry_no_match]

        allowed = {"cs.CV", "cs.LG", "cs.CL", "cs.AI", "cs.NE", "cs.RO"}
        with patch("src.utils.parse", return_value=mock_parsed):
            result = get_parsed_output(b"mock", allowed_categories=allowed)

        total_rows = sum(len(rows) for rows in result.values())
        assert total_rows == 1  # Only the cs.CV paper

    def test_parsed_output_no_filter_when_none(self):
        """All papers pass when allowed_categories is None."""
        entry = self._make_entry(
            "2603.00001",
            "2026-03-23T17:00:00Z",
            [{"term": "math.OC"}],
        )
        mock_parsed = MagicMock()
        mock_parsed.entries = [entry]

        with patch("src.utils.parse", return_value=mock_parsed):
            result = get_parsed_output(b"mock", allowed_categories=None)

        total_rows = sum(len(rows) for rows in result.values())
        assert total_rows == 1
