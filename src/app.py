from os import getenv

from utils import (
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
INCLUDE_CITATIONS = getenv("INCLUDE_CITATIONS", "false").lower() == "true"

HEADER = ["Published", "ISOWeek", "Updated", "ID", "Version", "Title"]
if INCLUDE_CITATIONS:
    from citations import enrich_row, get_citations

    HEADER = HEADER + ["Citations", "References", "InfluentialCitations"]

# Load existing IDs to skip known papers before enrichment
existing_ids = load_all_existing_ids(OUT_DIR)
print(f"Loaded {len(existing_ids)} existing paper IDs from {OUT_DIR}")

# Get total results count with a probe request
probe_url = f"{BASE_URL}search_query={TOPICS}&start=0&max_results=1&sortBy=submittedDate"
probe_response = get_api_response(probe_url)
total_results = get_total_results(probe_response)
print(f"arXiv reports {total_results} total results for query")

# Paginate through all results
start = 0
total_new = 0
while start < total_results:
    page_url = (
        f"{BASE_URL}search_query={TOPICS}"
        f"&start={start}&max_results={PAGE_SIZE}&sortBy=submittedDate"
    )
    response = get_api_response(page_url)
    out = get_parsed_output(response)

    if not out:
        break

    for year, week in out.keys():
        rows = out[(year, week)]
        new_rows = filter_new_rows(rows, existing_ids)
        if new_rows:
            if INCLUDE_CITATIONS:
                new_rows = [enrich_row(row, get_citations(row[3])) for row in new_rows]
            year_dir = f"{OUT_DIR}/{year}"
            write_file(new_rows, str(week), year_dir, HEADER)
            total_new += len(new_rows)

    start += PAGE_SIZE

print(f"Done. {total_new} new papers written.")
