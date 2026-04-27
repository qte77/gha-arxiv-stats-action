# gha-arxiv-stats-action

Logs daily stats of papers submitted to [arxiv.org](https://arxiv.org/). Inspired by [stats@arxiv-sanity-lite.com](https://arxiv-sanity-lite.com/stats).

![Version](https://img.shields.io/badge/version-0.0.1-8A2BE2)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Update arxiv.org stats](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/write-arxiv-stats.yml/badge.svg)](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/write-arxiv-stats.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/gha-arxiv-stats-action/badge)](https://www.codefactor.io/repository/github/qte77/gha-arxiv-stats-action)
[![CodeQL](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/codeql.yml/badge.svg)](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/codeql.yml)
[![Dependabot](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/dependabot/dependabot-updates)
[![Ruff](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/ruff.yml/badge.svg)](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/ruff.yml)
[![Tests](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/test.yml/badge.svg)](https://github.com/qte77/gha-arxiv-stats-action/actions/workflows/test.yml)

## What it does

1. Checks out the calling repository
2. Sets up Python via uv
3. Queries the arXiv API for papers matching the configured topic categories
4. Optionally enriches results with Semantic Scholar citation counts
5. Writes results to CSV files in the output directory
6. Opens a PR with the updated data (auto-merges via squash)

## Usage

```yaml
- uses: qte77/gha-arxiv-stats-action@v0
  with:
    OUT_DIR: './data'
    TOPICS: 'cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO'
    TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `OUT_DIR` | No | `./data` | Directory to write CSV output files |
| `TOPICS` | No | `cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO` | ArXiv category query (OR-separated) |
| `TOKEN` | No | _(empty)_ | GitHub token for pushing changes |
| `INCLUDE_CITATIONS` | No | `false` | Enrich output with Semantic Scholar citation counts |
| `SEMANTIC_SCHOLAR_API_KEY` | No | _(empty)_ | Optional Semantic Scholar API key for higher rate limits |

## Similar projects

- [monologg/nlp-arxiv-daily](https://github.com/monologg/nlp-arxiv-daily), uses [pypi/arxiv.py](https://pypi.org/project/arxiv/) and [PwC API](https://arxiv.paperswithcode.com/api/v0/papers/).

## Further reading

- [Today, arXivLabs launched a new Code tab, a shortcut linking Machine Learning articles with their associated code](https://blog.arxiv.org/2020/10/08/new-arxivlabs-feature-provides-instant-access-to-code/), 2020-10-08
- [PapersWithCode API Documentation](https://paperswithcode-client.readthedocs.io/en/latest/index.html), [pypi/paperswithcode-client](https://pypi.org/project/paperswithcode-client/)

## License

[Apache-2.0](LICENSE)
