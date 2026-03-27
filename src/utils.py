'''
TODO short description

arxiv API output
  'id': 'http://arxiv.org/abs/2406.04221v1',
  'guidislink': True,
  'link': 'http://arxiv.org/abs/2406.04221v1',
  'updated': '2024-06-06T16:20:07Z',
  'updated_parsed': time.struct_time(
    tm_year=2024, tm_mon=6, tm_mday=6, tm_hour=16,
    tm_min=20, tm_sec=7, tm_wday=3, tm_yday=158, tm_isdst=0
  ),
  'published': '2024-06-06T16:20:07Z',
  'published_parsed': time.struct_time(
    tm_year=2024, tm_mon=6, tm_mday=6, tm_hour=16,
    tm_min=20, tm_sec=7, tm_wday=3, tm_yday=158, tm_isdst=0
  ),
  'title': 'Matching Anything by Segmenting Anything',
  'title_detail': {
    'type': 'text/plain', 'language': None,
    'base': '', 'value': 'Matching Anything by Segmenting Anything'
    },
  'summary': 'The robust association of the same'
'''
import csv
import time
from os import makedirs
from os.path import exists, dirname
from datetime import datetime
from feedparser import FeedParserDict, parse
from urllib.request import urlopen, Request
from urllib.error import URLError

def encode_feedparser_dict(d):
  """ helper function to strip feedparser objects using a deep copy """
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
  ix = url.rfind('/')
  assert ix >= 0, 'bad url: ' + url
  idv = url[ix+1:] # extract just the id (and the version)
  rawid, version = idv.split('v')
  assert rawid is not None and version is not None, \
    f"error splitting id and version in idv string: {idv}"
  return idv, rawid, int(version)

def get_api_response(api_url, max_retries=3, backoff_base=2.0):
  if not api_url.lower().startswith('https://'):
    raise ValueError from None
  req = Request(api_url)
  for attempt in range(max_retries):
    try:
      with urlopen(req, timeout=30) as url:
        assert url.status == 200, \
          f"arxiv did not return status 200 response: {api_url}"
        return url.read()
    except (URLError, AssertionError):
      if attempt < max_retries - 1:
        time.sleep(backoff_base ** attempt)
      else:
        raise RuntimeError(
          f"arxiv API failed after {max_retries} attempts: {api_url}"
        ) from None

def get_parsed_output(response):
  '''
  Expects API response for feedparser.parse().
  Returns dict(list) of parsed API responses
  '''
  out = {}
  parsed = parse(response)
  for e in parsed.entries:
      j = encode_feedparser_dict(e)
      idv, rawid, version = parse_arxiv_url(j['id'])
      # TODO simplify title prep
      title = str(j['title'])
      for s in '\n\r\"\'':
          title = title.translate({ ord(s): None })
      title = f"'{title}'" 
      pub_date_utc = datetime.strptime(j['published'], '%Y-%m-%dT%H:%M:%SZ')
      pub_weekday = pub_date_utc.isocalendar().week # .strftime('%V')
      if out.get(pub_weekday) is None:
        out[pub_weekday] = []
      out[pub_weekday].append([
        j['published'], pub_weekday, j['updated'],
        rawid, version, title                  
      ])
  return out

def write_file(
  content: list, file_name: str,
  out_dir: str = ".", header = '', file_ext: str = "csv"
) -> None:
  '''TODO'''
  out_file = f"{out_dir}/{file_name}.{file_ext}"
  fopen_kw = { 'file': out_file, 'newline': '', 'encoding': 'UTF8' }
  if not exists(out_file):
    # folder needs to exist before open() context
    makedirs(dirname(out_file), exist_ok=True)
    with open(mode='w+', **fopen_kw) as f:
      writer = csv.writer(f)
      writer.writerow(header)
  with open(mode='a+', **fopen_kw) as f:
    writer = csv.writer(f)
    for o in content:
      writer.writerow(o)
