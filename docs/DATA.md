# Data exports

The GitHub Pages workflow (`.github/workflows/pages.yml`) runs `scripts/build_index.py` on every push to `main` that touches the index, and weekly on Mondays. The script reads the country table in this repository's `README.md`, fetches each country repository's README through the GitHub API and publishes two JSON files next to the site:

| File | Used by | Contents |
|---|---|---|
| [`resources.json`](https://provereno-media.github.io/OSINT-for-countries-V2.0/resources.json) | Interactive directory | Per-country import status and all parsed resource records |
| [`import-report.json`](https://provereno-media.github.io/OSINT-for-countries-V2.0/import-report.json) | README badges, coverage review | Totals, per-country status and possible parsing omissions |

Both files are build output, not a stable API: field names may change with the builder. No versioning or compatibility guarantee is offered.

## `resources.json`

```json
{
  "generated_at": "ISO 8601 UTC timestamp of the build",
  "index_source": "https://github.com/Provereno-Media/OSINT-for-countries-V2.0/blob/HEAD/README.md",
  "countries": [
    {"country": "…", "repository": "…", "count": 0, "categories": {"…": 0}, "candidates": 0, "readme_updated": "YYYY-MM-DD", "ok": true}
  ],
  "resources": [
    {"country": "…", "category": "…", "subsection": "…", "name": "…", "description": "…", "url": "…", "source": "…/blob/HEAD/README.md"}
  ]
}
```

`readme_updated` is the date of the last commit to the country README, or `null` if it could not be read. The site shows it as "list edited" on each card.

A country whose README could not be fetched or parsed has `"ok": false` and an `"error"` message; its resources are absent from the search.

## `import-report.json`

Contains `generated_at`, `index_source`, `country_total`, `country_imported`, `resource_total`, the same `countries` list, and `possible_omissions` — links the parser saw but did not index (unsupported line format or unrecognized section). Omissions need manual review; a zero count in a category does not by itself prove a parsing error.

## What the data does not mean

`generated_at` is the build time and `readme_updated` the last README edit; neither is a review date. Inclusion means a link was found in a country README; it does not mean the link is reachable or its data accurate. Review dates are recorded separately in `data/country_reviews.csv` (see [STANDARD.md](../STANDARD.md#evidence-and-audit-trail)).

```bash
curl -fLsS 'https://provereno-media.github.io/OSINT-for-countries-V2.0/import-report.json' | python -m json.tool
```
