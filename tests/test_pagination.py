"""Tests for dynamic pagination and ID pre-filtering."""

from unittest.mock import MagicMock, patch

from src.utils import filter_new_rows, get_total_results, load_all_existing_ids


class TestGetTotalResults:
    """Tests for get_total_results()."""

    def test_get_total_results_reads_opensearch_field(self):
        """Extracts totalResults from feedparser feed metadata."""
        # ARRANGE
        mock_parsed = MagicMock()
        mock_parsed.feed.opensearch_totalresults = "1500"

        # ACT
        with patch("src.utils.parse", return_value=mock_parsed):
            total = get_total_results(b"<feed>mock</feed>")

        # ASSERT
        assert total == 1500

    def test_get_total_results_returns_zero_on_missing_field(self):
        """Returns 0 when opensearch:totalResults is not present."""
        # ARRANGE
        mock_parsed = MagicMock(spec=[])
        mock_parsed.feed = MagicMock(spec=[])

        # ACT
        with patch("src.utils.parse", return_value=mock_parsed):
            total = get_total_results(b"<feed>empty</feed>")

        # ASSERT
        assert total == 0


class TestLoadAllExistingIds:
    """Tests for load_all_existing_ids()."""

    def test_load_all_existing_ids_from_year_dirs(self, tmp_path):
        """Loads (rawid, version) pairs from all CSVs in data/YYYY/ dirs."""
        # ARRANGE
        year_dir = tmp_path / "2026"
        year_dir.mkdir()
        csv_file = year_dir / "13.csv"
        csv_file.write_text(
            "Published,ISOWeek,Updated,ID,Version,Title\n"
            "2026-03-23T00:00:00Z,13,2026-03-23T00:00:00Z,2603.00001,1,'Title A'\n"
            "2026-03-24T00:00:00Z,13,2026-03-24T00:00:00Z,2603.00002,1,'Title B'\n"
        )

        # ACT
        ids = load_all_existing_ids(str(tmp_path))

        # ASSERT
        assert ("2603.00001", "1") in ids
        assert ("2603.00002", "1") in ids
        assert len(ids) == 2

    def test_load_all_existing_ids_empty_dir(self, tmp_path):
        """Returns empty set for directory with no CSVs."""
        # ACT
        ids = load_all_existing_ids(str(tmp_path))

        # ASSERT
        assert ids == set()


class TestFilterNewRows:
    """Tests for filter_new_rows()."""

    def test_filter_new_rows_removes_known_ids(self):
        """Rows with (rawid, version) in existing set are filtered out."""
        # ARRANGE
        existing = {("2603.00001", "1")}
        rows = [
            ["2026-03-23T00:00:00Z", 13, "2026-03-23T00:00:00Z", "2603.00001", 1, "'Known'"],
            ["2026-03-24T00:00:00Z", 13, "2026-03-24T00:00:00Z", "2603.00099", 1, "'New'"],
        ]

        # ACT
        new = filter_new_rows(rows, existing)

        # ASSERT
        assert len(new) == 1
        assert new[0][3] == "2603.00099"

    def test_filter_new_rows_keeps_all_when_no_existing(self):
        """All rows pass through when existing set is empty."""
        # ARRANGE
        rows = [
            ["2026-03-23T00:00:00Z", 13, "2026-03-23T00:00:00Z", "2603.00001", 1, "'A'"],
            ["2026-03-24T00:00:00Z", 13, "2026-03-24T00:00:00Z", "2603.00002", 1, "'B'"],
        ]

        # ACT
        new = filter_new_rows(rows, set())

        # ASSERT
        assert len(new) == 2
