"""Tests for write_file dedup and year-directory structure."""

import csv

from src.utils import write_file

HEADER = ["Published", "ISOWeek", "Updated", "ID", "Version", "Title"]


def test_write_file_creates_year_dir(tmp_path):
    """write_file creates data/YYYY/WW.csv structure."""
    rows = [["2026-03-23T00:00:00Z", 13, "2026-03-23T00:00:00Z", "2603.00001", 1, "'Title'"]]
    write_file(rows, "13", str(tmp_path / "2026"), HEADER)
    assert (tmp_path / "2026" / "13.csv").exists()


def test_write_file_skips_duplicate_rows(tmp_path):
    """write_file does not append rows with same (rawid, version)."""
    out_dir = str(tmp_path / "2026")
    rows = [["2026-03-23T00:00:00Z", 13, "2026-03-23T00:00:00Z", "2603.00001", 1, "'Title A'"]]
    write_file(rows, "13", out_dir, HEADER)
    # Write same row again
    write_file(rows, "13", out_dir, HEADER)
    with open(tmp_path / "2026" / "13.csv") as f:
        lines = f.readlines()
    # Header + 1 data row, NOT header + 2 data rows
    assert len(lines) == 2


def test_write_file_allows_new_version(tmp_path):
    """write_file appends row if same rawid but different version."""
    out_dir = str(tmp_path / "2026")
    row_v1 = [["2026-03-23T00:00:00Z", 13, "2026-03-23T00:00:00Z", "2603.00001", 1, "'Title A'"]]
    row_v2 = [["2026-03-24T00:00:00Z", 13, "2026-03-24T00:00:00Z", "2603.00001", 2, "'Title A v2'"]]
    write_file(row_v1, "13", out_dir, HEADER)
    write_file(row_v2, "13", out_dir, HEADER)
    with open(tmp_path / "2026" / "13.csv") as f:
        reader = csv.reader(f)
        rows = list(reader)
    # Header + v1 + v2
    assert len(rows) == 3
    assert rows[1][4] == "1"
    assert rows[2][4] == "2"


def test_get_parsed_output_keys_include_year():
    """get_parsed_output returns (year, week) tuple keys."""
    from unittest.mock import MagicMock, patch

    mock_entry = MagicMock()
    mock_entry.keys.return_value = [
        "id", "published", "updated", "title",
    ]
    mock_entry.__getitem__ = lambda self, key: {
        "id": "http://arxiv.org/abs/2603.00001v1",
        "published": "2026-03-23T17:00:00Z",
        "updated": "2026-03-23T17:00:00Z",
        "title": "Test Paper",
    }[key]

    mock_parsed = MagicMock()
    mock_parsed.entries = [mock_entry]

    with patch("src.utils.parse", return_value=mock_parsed):
        from src.utils import get_parsed_output
        result = get_parsed_output(b"mock")

    # Keys should be (year, week) tuples
    key = list(result.keys())[0]
    assert isinstance(key, tuple), f"Expected tuple key, got {type(key)}: {key}"
    assert key[0] == 2026
