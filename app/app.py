from os import getenv
from utils import get_api_response, get_parsed_output, write_file

OUT_DIR = getenv("OUT_DIR", './data')
TOPICS = getenv("TOPICS", 'cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO')
BASE_URL = getenv("BASE_URL", 'https://export.arxiv.org/api/query?')
ADD_URL = getenv("ADD_URL", 'search_query=#TOPICS#&start=#STARTRES#&max_results=#MAXRES#&sortBy=submittedDate')
START_RESULT = getenv("START_RESULT", 0)
RESULT_COUNT = getenv("END_RESULT", 199)
MAX_RESULTS_PER_QUERY = getenv("MAX_RESULTS_PER_QUERY", 100)

TOPICS_REPL_STR = "#TOPICS#"
MAXRES_REPL_STR = "#MAXRES#"
STARTRES_REPL_STR = "#STARTRES#"

HEADER = ["Published", "ISOWeek", "Updated", "ID", "Version", "Title"]

# https://github.com/karpathy/arxiv-sanity-lite/blob/d7a303b410b0246fbd19087e37f1885f7ca8a9dc/aslite/arxiv.py#L15
# https://info.arxiv.org/help/api/user-manual.html
# sortOrder=descending
add_url_dyn = ADD_URL.replace(TOPICS_REPL_STR, TOPICS).replace(MAXRES_REPL_STR, str(MAX_RESULTS_PER_QUERY))
api_url = BASE_URL + add_url_dyn

for week_num in range(START_RESULT, START_RESULT + RESULT_COUNT, MAX_RESULTS_PER_QUERY):
  api_url_k = api_url.replace(STARTRES_REPL_STR, str(week_num))
  response = get_api_response(api_url_k)
  out = get_parsed_output(response)
  print(f"{len(out)=}, {out.keys()=}")
  for week_num in out.keys():
    write_file(out[week_num], week_num, OUT_DIR, HEADER)
