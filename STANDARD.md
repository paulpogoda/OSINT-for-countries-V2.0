# OSINT for Countries — Editorial and Data Standard

This document specifies the proposed shared rules for country repositories indexed by the project. It does **not** certify retrospectively that all existing country lists pass these checks.

## Categories

A country collection must preserve these seven primary categories (equivalent headings in legacy repositories are acceptable):

1. **Open databases & statistics:** official portals, statistics, public datasets, courts' open datasets when appropriately placed.
2. **Legal entities, tax information & registries:** corporate registries, business ownership, tax lookup and filings available to the public.
3. **Maps, land records & cadastres:** GIS, cadastral records, addresses, satellite and administrative maps.
4. **Vehicles:** road vehicles, maritime vessels, aircraft and registries where lawful/public.
5. **People & public identifiers:** public directories, court documents and identity-related search tools; never republish unnecessary sensitive personal data.
6. **Public procurement:** contracts, tenders, awards and related public spending registries.
7. **WHOIS & domain records:** registry data, RDAP, WHOIS and local domain lookup services.

Cross-border resources may be placed in a relevant country if clearly applicable, or in the main project's multi-country resources directory.

## Resource inclusion criteria

Document the resource title, canonical URL, publisher/operator, category, country relevance, content scope, restrictions (free/paid, registration, geography), and when a contributor last checked it. Prefer official/primary sources; third-party aggregators can be useful if labelled. Exclude obviously broken, malicious, misrepresented, unlawfully obtained or unsubstantiated services. A working HTTP response is not proof that underlying data is correct.

## Country status and freshness

**Status and freshness are separate dimensions.**

- **Draft:** country collection is explicitly marked incomplete.
- **Listed:** repository is indexed, but no verified content-review claim is implied.
- **Maintained:** an editor has recorded a content review in the last **180 days**, with evidence.
- **Review needed:** most recent documented review is **181–365 days** old.
- **Stale:** last documented review is **more than 365 days** old.

When there is **no documented review date**, the README must say **Not recorded** and status is **Listed**, not **Maintained**. `Maintained`, `Review needed`, and `Stale` are derived from elapsed days since `last_reviewed` and require an evidence reference. Draft overrides those states until declared complete. These thresholds are proposed editorial policy, not measurements of real link health. A commit date, GitHub activity, CI link check or page import date must **not** be substituted for a manual content review.

## Evidence and audit trail

Record `last_reviewed` as `YYYY-MM-DD` and a public review evidence URL in `data/country_reviews.csv` (for example, the PR or commit containing an audit checklist). Do not enter speculative dates. A record of the audit should say which sections were inspected and whether links, descriptions and access restrictions were sampled or fully checked. If only a subset was checked, describe the scope; do not claim a full audit.

## Change management

Contributions should preserve attribution and original URLs, explain redirects/removals, and avoid exposing confidential or sensitive information in issues. The dataset and UI must not imply endorsement of third-party providers. Revisit this standard through an explicit PR before applying new mandatory rules retroactively.
