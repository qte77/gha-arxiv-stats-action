import re
from os import getenv

from utils import (
    build_date_query,
    filter_new_rows,
    get_api_response,
    get_parsed_output,
    get_total_results,
    load_all_existing_ids,
    write_file,
)

OUT_DIR = getenv("OUT_DIR", "./data")
TOPICS = getenv(
    "TOPICS",
    "cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO",
)
BASE_URL = getenv("BASE_URL", "https://export.arxiv.org/api/query?")
PAGE_SIZE = int(getenv("PAGE_SIZE", "1000"))
MAX_PAGES = int(getenv("MAX_PAGES", "5"))
MAX_AGE_DAYS = int(getenv("MAX_AGE_DAYS", "7"))
DATE_FROM = getenv("DATE_FROM", "")
DATE_TO = getenv("DATE_TO", "")
INCLUDE_CITATIONS = getenv("INCLUDE_CITATIONS", "false").lower() == "true"

# Parse allowed categories from TOPICS query string
ALLOWED_CATEGORIES = set(re.findall(r"cat:([a-zA-Z\-]+\.[A-Z]+)", TOPICS))

# Build date range query (server-side filter)
date_query = build_date_query(date_from=DATE_FROM or None, date_to=DATE_TO or None)
# Reason: when DATE_FROM is set, server filters by submittedDate — disable client-side age filter
effective_max_age = None if date_query else MAX_AGE_DAYS

HEADER = ["Published", "ISOWeek", "Updated", "ID", "Version", "Title", "Categories"]
if INCLUDE_CITATIONS:
    from citations import enrich_row, get_citations

    HEADER = HEADER + ["Citations", "References", "InfluentialCitations"]

# Load existing IDs to skip known papers before enrichment
existing_ids = load_all_existing_ids(OUT_DIR)
print(f"Loaded {len(existing_ids)} existing paper IDs from {OUT_DIR}")
print(f"Allowed categories: {sorted(ALLOWED_CATEGORIES)}")
if date_query:
    print(f"Date range filter: {DATE_FROM} to {DATE_TO or 'today'}")
else:
    print(f"Max paper age: {MAX_AGE_DAYS} days")

# Build search query with optional date range
search_query = f"{TOPICS}{date_query}"

probe_url = f"{BASE_URL}search_query={search_query}&start=0&max_results=1&sortBy=submittedDate"
probe_response = get_api_response(probe_url)
total_results = get_total_results(probe_response)
fetch_limit = min(total_results, MAX_PAGES * PAGE_SIZE)
print(f"arXiv reports {total_results} total results. Fetching up to {fetch_limit}.")

# Paginate through recent results (sorted by submittedDate descending)
start = 0
total_new = 0
total_filtered = 0
while start < fetch_limit:
    page_url = (
        f"{BASE_URL}search_query={search_query}"
        f"&start={start}&max_results={PAGE_SIZE}&sortBy=submittedDate"
    )
    try:
        response = get_api_response(page_url)
    except RuntimeError as e:
        print(f"API error at start={start}, stopping pagination: {e}")
        break

    out = get_parsed_output(
        response,
        allowed_categories=ALLOWED_CATEGORIES,
        max_age_days=effective_max_age,
    )
    if not out:
        print(f"No matching papers on page starting at {start}. Stopping.")
        break

    page_new = 0
    for year, week in out.keys():
        rows = out[(year, week)]
        new_rows = filter_new_rows(rows, existing_ids)
        if new_rows:
            if INCLUDE_CITATIONS:
                new_rows = [enrich_row(row, get_citations(row[3])) for row in new_rows]
            year_dir = f"{OUT_DIR}/{year}"
            write_file(new_rows, str(week), year_dir, HEADER)
            total_new += len(new_rows)
            page_new += len(new_rows)

    if page_new == 0:
        print(f"No new papers on page starting at {start}. Stopping.")
        break

    start += PAGE_SIZE

print(f"Done. {total_new} new papers written.")
