# Contributing to OSINT for Countries

Thank you for helping maintain country-specific OSINT resources. The country index is a directory of separately maintained repositories: changes to an existing country list should usually be proposed in that country's repository, not this index.

## Ways to contribute

1. **Report a broken resource:** use the [broken-link issue form](.github/ISSUE_TEMPLATE/broken-link.yml). Include country, resource URL, observed problem and check date. Do not disclose credentials or personal information.
2. **Suggest a resource:** use the [resource suggestion form](.github/ISSUE_TEMPLATE/resource-suggestion.yml). Identify the primary publisher, jurisdiction, scope and access requirements.
3. **Add a country:** start from the existing [Country Template](Country%20Template), create a public repository using the seven categories, then open a PR to this index adding the country and maintainer.
4. **Correct an existing country:** open a PR against the country repository; if it is no longer maintained, open a discussion or issue here.
5. **Improve the site or docs:** open a focused PR explaining the change and how you checked it.

## Contribution checklist

- Keep country-specific resources in the relevant country repository.
- Follow the seven categories and inclusion rules in [STANDARD.md](STANDARD.md).
- Prefer official or first-party sources where available; label third-party data clearly.
- Write neutral descriptions of what the source **actually** contains.
- State whether registration, payment, geographic access or special credentials are needed.
- Do not add leaked credential collections, doxxing dumps, or unlawful access instructions.
- Check links manually before submitting. Include the date of that check in the PR description; do not equate URL reachability with data accuracy.
- Avoid duplicates; if a resource spans categories, choose one primary category and cross-reference only when justified.
- Explain country, category, resource and reason for the change in the PR.

## Review and freshness

A repository is **Listed** when it is indexed. It is not automatically **Reviewed** or **Maintained**. See the precise definitions and ageing thresholds in [STANDARD.md](STANDARD.md). A reviewed date must refer to an explicitly documented audit; a commit, merge or automated HTTP check does not qualify.

To register a documented audit, update `data/country_reviews.csv` with the country, ISO-formatted review date and evidence URL. Run `python scripts/update_country_freshness.py` to refresh the README table. Changes to evidence and claims should be reviewed in the PR.

## Pull requests

Use a descriptive title (e.g. `Kazakhstan: add public procurement portal`), link related issues, and specify any access restrictions. Contributors remain responsible for ensuring submitted material is legally and ethically sourced. The maintainers may request changes or reject submissions that cannot be verified.

## Credit

The project acknowledges the original [OSINT for Countries](https://github.com/wddadk/OSINT-for-countries), [Pogoda](https://github.com/paulpogoda) and the wider contributor community. Please preserve provenance and original authorship when migrating materials.
