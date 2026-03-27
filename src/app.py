from os import getenv

from utils import get_api_response, get_parsed_output, write_file

OUT_DIR = getenv("OUT_DIR", "./data")
TOPICS = getenv(
    "TOPICS",
    "cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO",
)
BASE_URL = getenv("BASE_URL", "https://export.arxiv.org/api/query?")
ADD_URL = getenv(
    "ADD_URL",
    "search_query=#TOPICS#&start=#STARTRES#&max_results=#MAXRES#&sortBy=submittedDate",
)
START_RESULT = getenv("START_RESULT", 0)
RESULT_COUNT = getenv("END_RESULT", 199)
MAX_RESULTS_PER_QUERY = getenv("MAX_RESULTS_PER_QUERY", 100)
INCLUDE_CITATIONS = getenv("INCLUDE_CITATIONS", "false").lower() == "true"

TOPICS_REPL_STR = "#TOPICS#"
MAXRES_REPL_STR = "#MAXRES#"
STARTRES_REPL_STR = "#STARTRES#"

HEADER = ["Published", "ISOWeek", "Updated", "ID", "Version", "Title"]
if INCLUDE_CITATIONS:
    from citations import enrich_row, get_citations

    HEADER = HEADER + ["Citations", "References", "InfluentialCitations"]

# https://github.com/karpathy/arxiv-sanity-lite/blob/d7a303b410b0246fbd19087e37f1885f7ca8a9dc/aslite/arxiv.py#L15
# https://info.arxiv.org/help/api/user-manual.html
# sortOrder=descending
add_url_dyn = ADD_URL.replace(TOPICS_REPL_STR, TOPICS).replace(
    MAXRES_REPL_STR, str(MAX_RESULTS_PER_QUERY)
)
api_url = BASE_URL + add_url_dyn

for week_num in range(START_RESULT, START_RESULT + RESULT_COUNT, MAX_RESULTS_PER_QUERY):
    api_url_k = api_url.replace(STARTRES_REPL_STR, str(week_num))
    response = get_api_response(api_url_k)
    out = get_parsed_output(response)
    print(f"{len(out)=}, {out.keys()=}")
    for year, week in out.keys():
        rows = out[(year, week)]
        if INCLUDE_CITATIONS:
            rows = [enrich_row(row, get_citations(row[3])) for row in rows]
        year_dir = f"{OUT_DIR}/{year}"
        write_file(rows, str(week), year_dir, HEADER)
