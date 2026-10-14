# Repository setup checklist for maintainers

These steps require GitHub administration or an approved pull request. Files alone cannot change GitHub repository topics or social preview settings.

## GitHub Topics

In the repository's **About** settings, add relevant GitHub topics (up to GitHub's platform limit):

`osint`, `open-source-intelligence`, `osint-tools`, `osint-resources`, `investigative-journalism`, `fact-checking`, `open-data`, `public-records`, `research`, `investigations`, `country-data`, `verification`.

Do not claim topics have been applied until they appear on the actual repository.

## Description

Suggested description: *Country-specific OSINT resources, public databases, registries and investigative tools for journalists, researchers and fact-checkers.*

Keep the repository website pointing to the interactive directory.

## Social preview

Upload `assets/social-preview.png` using **Settings → General → Social preview → Edit** (or equivalent current GitHub controls). Verify readability in a link unfurl after saving. It is a designed project graphic, **not** a screenshot of the website.

## Real website screenshot

A real screenshot **was not created**, because the live Pages site could not be reached from the build environment. On a computer where the site opens, install Playwright and its Chromium browser, then run:

```bash
python -m pip install playwright
python -m playwright install chromium
python scripts/capture_screenshot.py
```

The script captures the actual published site as `assets/interactive-directory.png`; review for personal data, broken layout, and accidental login/consent overlays. After verifying, uncomment the screenshot link in `README.md` and commit the PNG. Do **not** present the social-preview illustration as a screenshot.

## Review/freshness metadata

All country review dates initially remain unrecorded. Document an actual review in `data/country_reviews.csv`, linking evidence, then run `python scripts/update_country_freshness.py`. Review diffs before merging. Do not automate a 'reviewed today' date on builds or commits.

## Last Updated badge in country READMEs

The Country Template shows the repository's last commit date through a shields.io badge instead of a hand-written date. To convert existing country READMEs, run from the repository root:

```bash
python scripts/set_last_updated_badge.py                    # dry run: lists what would change
GITHUB_TOKEN=... python scripts/set_last_updated_badge.py --apply
```

The script replaces the first `Last Updated: …` line in each indexed README; `--insert-missing` adds the badge after the introduction (before the first `##` section, as in the Country Template) where no such line exists, and `--only "Estonia,Latvia"` limits the run. With `--apply` it commits only to repositories the token can push to and lists the rest under `no_push_access`; propose the change to those maintainers by PR. The badge is an edit date, not a review date (see STANDARD.md).

### Running it from GitHub Actions

The **Set Last Updated badge in country READMEs** workflow runs the same script without a local setup.

1. Create a token from an account with write access to the country repositories: a classic token with the `public_repo` scope covers both `paulpogoda/*` and `Provereno-Media/*` (a fine-grained token covers only one owner). Give it a short expiry.
2. Save it as the repository secret `BADGE_TOKEN` (Settings → Secrets and variables → Actions → New repository secret).
3. Actions → *Set Last Updated badge in country READMEs* → **Run workflow**. Leave **apply** unchecked for a dry run; the result appears in the run summary. Try one country with **only** = `Estonia` and **apply** checked before running all.
4. Delete the secret and revoke the token when done.

The run fails if any README could not be read, so errors are not hidden behind a green check.

## Issue templates

Files in `.github/ISSUE_TEMPLATE/` become available after merge. Check that their labels, required fields and links match the repository's moderation process. No labels are assumed to exist.

## Data exports

`scripts/build_index.py` publishes `resources.json` and `import-report.json` on each Pages build; see `docs/DATA.md`. Any new export must be added to the builder with tests in `tests/test_build_index.py`.
