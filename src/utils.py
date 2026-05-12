"""Helpers for fetching and parsing arXiv API responses into CSV rows."""

import csv
import os
import time
from datetime import datetime
from os import makedirs
from os.path import dirname, exists

import requests
from feedparser import FeedParserDict, parse


def encode_feedparser_dict(d):
    """helper function to strip feedparser objects using a deep copy"""
    if isinstance(d, FeedParserDict) or isinstance(d, dict):
        return {k: encode_feedparser_dict(d[k]) for k in d.keys()}
    elif isinstance(d, list):
        return [encode_feedparser_dict(k) for k in d]
    else:
        return d


def parse_arxiv_url(url):
    """
    example is http://arxiv.org/abs/1512.08756v2
    we want to extract the raw id (1512.08756) and the version (2)
    """
    ix = url.rfind("/")
    if ix < 0:
        raise ValueError(f"bad url: {url}")
    idv = url[ix + 1 :]  # extract just the id (and the version)
    try:
        rawid, version = idv.split("v")
    except ValueError as e:
        raise ValueError(f"malformed arxiv id (expected 'rawidvN'): {idv}") from e
    return idv, rawid, int(version)


def get_api_response(api_url, max_retries=3, backoff_base=2.0):
    if not api_url.lower().startswith("https://"):
        raise ValueError(f"Only HTTPS URLs are allowed, got: {api_url[:50]}")
    for attempt in range(max_retries):
        try:
            resp = requests.get(api_url, timeout=30)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(backoff_base**attempt)
            else:
                raise RuntimeError(
                    f"arxiv API failed after {max_retries} attempts: {api_url}"
                ) from None


def build_date_query(date_from=None, date_to=None):
    """Build arXiv submittedDate range query fragment.

    Args:
        date_from: Start date as YYYY-MM-DD string, or None.
        date_to: End date as YYYY-MM-DD string, or None (defaults to today).

    Returns:
        Query fragment like '+AND+submittedDate:[YYYYMMDDHHMM+TO+YYYYMMDDHHMM]',
        or empty string if no dates provided.
    """
    if not date_from:
        return ""

    def _parse(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {d}. Expected YYYY-MM-DD.") from None

    start = _parse(date_from)
    end = _parse(date_to) if date_to else datetime.now(tz=None)

    return f"+AND+submittedDate:[{start:%Y%m%d}0000+TO+{end:%Y%m%d}2359]"


def extract_categories(tags):
    """Extract category terms from feedparser tags list.

    Args:
        tags: List of dicts with 'term' key, or None.

    Returns:
        List of category strings (e.g. ['cs.CV', 'cs.LG']).
    """
    if not tags:
        return []
    return [t["term"] for t in tags if "term" in t]


def get_parsed_output(response, allowed_categories=None, max_age_days=None):
    """Parse arXiv API response into rows grouped by (year, week).

    Args:
        response: Raw API response bytes.
        allowed_categories: Set of category strings to filter by.
            Papers must have at least one matching category. None = no filter.
        max_age_days: If set, skip papers published more than N days ago.

    Returns:
        Dict mapping (year, week) tuples to lists of CSV rows.
        Each row: [published, week, updated, rawid, version, title, categories]
    """
    out = {}
    parsed = parse(response)
    now = datetime.now(tz=None)  # UTC-naive, matches arXiv timestamps

    for e in parsed.entries:
        j = encode_feedparser_dict(e)

        # Extract and filter by categories
        try:
            tags = j["tags"]
        except (KeyError, TypeError):
            tags = []
        categories = extract_categories(tags)
        if allowed_categories and not any(c in allowed_categories for c in categories):
            continue

        idv, rawid, version = parse_arxiv_url(j["id"])

        pub_date_utc = datetime.strptime(j["published"], "%Y-%m-%dT%H:%M:%SZ")

        # Skip papers not published recently (only updated)
        if max_age_days is not None:
            age = (now - pub_date_utc).days
            if age > max_age_days:
                continue

        title = str(j["title"])
        for s in "\n\r\"'":
            title = title.translate({ord(s): None})
        title = f"'{title}'"

        iso = pub_date_utc.isocalendar()
        key = (iso.year, iso.week)
        if key not in out:
            out[key] = []

        categories_str = ";".join(categories)
        out[key].append(
            [j["published"], iso.week, j["updated"], rawid, version, title, categories_str]
        )
    return out


def get_total_results(response):
    """Read opensearch:totalResults from arXiv API response.

    Args:
        response: Raw API response bytes.

    Returns:
        Total number of matching results, or 0 if not available.
    """
    parsed = parse(response)
    try:
        return int(parsed.feed.opensearch_totalresults)
    except (AttributeError, ValueError, TypeError):
        return 0


def load_all_existing_ids(data_dir):
    """Load all (rawid, version) pairs from CSVs in data_dir/YYYY/ subdirs.

    Args:
        data_dir: Root data directory containing year subdirectories.

    Returns:
        Set of (rawid, version) string tuples.
    """
    existing = set()
    if not exists(data_dir):
        return existing
    for entry in os.listdir(data_dir):
        subdir = os.path.join(data_dir, entry)
        if not os.path.isdir(subdir) or not entry.isdigit():
            continue
        for fname in os.listdir(subdir):
            if fname.endswith(".csv"):
                existing.update(_load_existing_ids(os.path.join(subdir, fname)))
    return existing


def filter_new_rows(rows, existing_ids):
    """Filter out rows whose (rawid, version) is already known.

    Args:
        rows: List of CSV row lists (column 3=rawid, 4=version).
        existing_ids: Set of (rawid, version) string tuples.

    Returns:
        List of rows not in existing_ids.
    """
    return [row for row in rows if (row[3], str(row[4])) not in existing_ids]


def _load_existing_ids(out_file):
    """Load set of (rawid, version) from existing CSV for dedup."""
    existing = set()
    if exists(out_file):
        with open(out_file, newline="", encoding="UTF8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 5:
                    existing.add((row[3], str(row[4])))
    return existing


def write_file(
    content: list, file_name: str, out_dir: str = ".", header="", file_ext: str = "csv"
) -> None:
    """Write rows to CSV, skipping duplicates by (rawid, version)."""
    out_file = f"{out_dir}/{file_name}.{file_ext}"
    fopen_kw = {"file": out_file, "newline": "", "encoding": "UTF8"}
    if not exists(out_file):
        makedirs(dirname(out_file) if dirname(out_file) else out_dir, exist_ok=True)
        with open(mode="w+", **fopen_kw) as f:
            writer = csv.writer(f)
            writer.writerow(header)
    existing = _load_existing_ids(out_file)
    new_rows = [row for row in content if (row[3], str(row[4])) not in existing]
    if new_rows:
        with open(mode="a+", **fopen_kw) as f:
            writer = csv.writer(f)
            for row in new_rows:
                writer.writerow(row)
