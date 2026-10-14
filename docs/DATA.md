# Data exports and API — current references and proposed roadmap

## Existing referenced output (not independently verified in this delivery)

The supplied README links to [https://provereno-media.github.io/OSINT-for-countries-V2.0/import-report.json](https://provereno-media.github.io/OSINT-for-countries-V2.0/import-report.json), and the badges reference its `country_total` and `resource_total` properties. The repository includes `scripts/build_index.py` and a GitHub Pages site; **the current live endpoint and detailed response schema could not be verified from this environment**. Treat this as an existing **reference in the README**, not a compatibility guarantee.

### How to inspect the published output

```bash
curl -fLsS 'https://provereno-media.github.io/OSINT-for-countries-V2.0/import-report.json' | python -m json.tool
```

Always handle a non-200 response or missing keys without assuming zero resources.

## Proposed machine-readable exports (not implemented)

| Proposed file | Purpose | Status |
|---|---|---|
| `countries.json` | Country name, URL, maintainer, explicit status and review evidence | Proposed |
| `resources.json` | Normalized resource records and country/category mapping | Proposed |
| `stats.json` | Build-derived counts and timestamps | Proposed |

Example **illustrative schema, not an actual dataset**:

```json
{
  "country": "Exampleland",
  "repository_url": "https://github.com/example/example-country",
  "status": "listed",
  "last_reviewed": null,
  "review_evidence_url": null
}
```

A future stable API needs documented schemas, versioning (`schema_version`), validation, pagination for large exports, provenance, licensing/attribution, error handling and a published compatibility policy. A build timestamp is not a review timestamp. Do not advertise these proposed files as deployed until CI generates, validates and publishes them.
