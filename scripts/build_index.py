#!/usr/bin/env python3
"""Build the static resource index and an import coverage report."""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_REPOSITORY = 'Provereno-Media/OSINT-for-countries-V2.0'


def index_repository():
    """Repository whose README is the country index: INDEX_REPOSITORY, else the repo running the workflow."""
    value = os.environ.get('INDEX_REPOSITORY') or os.environ.get('GITHUB_REPOSITORY') or DEFAULT_INDEX_REPOSITORY
    owner, _, repo = value.strip().partition('/')
    if not owner or not repo or '/' in repo:
        raise ValueError(f'Invalid index repository: {value!r}')
    return owner, repo


INDEX_OWNER, INDEX_REPO = index_repository()
COUNTRY = re.compile(r'^\|[^|]*?\[([^\]]+)\]\(https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)(?:/tree/[^/\s)]+)?/?\)', re.I)
HEADING = re.compile(r'^#{2,4}\s+(.+?)\s*#*\s*$')
LINK = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', re.I)
BULLET = re.compile(r'^\s*[-*]\s+')
CATEGORIES = {
    'open data portals': 'Open Data portals',
    'legal entities': 'Legal Entities',
    'maps': 'Cadastral and other Maps',
    'cadastral and other maps': 'Cadastral and other Maps',
    'vehicles': 'Vehicles',
    'people': 'People, phones, social etc.',
    'people phones social': 'People, phones, social etc.',
    'people phones social etc': 'People, phones, social etc.',
    'public procurement': 'Public procurements',
    'public procurements': 'Public procurements',
    'whois': 'WHOIS',
}
ORDER = tuple(dict.fromkeys(CATEGORIES.values()))
# Fallback for headings that are not exact aliases, e.g. "Cadastral and Maps", "Open Data", "Courts", "Stock".
# The template scopes courts and stock exchanges under Open Data portals.
CATEGORY_KEYWORDS = (
    (re.compile(r'\bwhois\b'), 'WHOIS'),
    (re.compile(r'\bprocurements?\b|\btenders?\b'), 'Public procurements'),
    (re.compile(r'\bpeople\b'), 'People, phones, social etc.'),
    (re.compile(r'\bvehicles?\b'), 'Vehicles'),
    (re.compile(r'\bcadastr|\bmaps?\b'), 'Cadastral and other Maps'),
    (re.compile(r'\blegal entit'), 'Legal Entities'),
    (re.compile(r'\bopen data\b|\bcourts?\b|\bstocks?\b'), 'Open Data portals'),
)
# The fixed People line from the Country Template is identical in every country README.
TEMPLATE_URLS = {'https://app.osint.industries', 'https://github.com/paulpogoda/digital-profiler-s-toolkit'}
NON_RESOURCE_SECTIONS = {'table of contents', 'contributions', 'contributing', 'legal disclaimer', 'appendix', 'about', 'license'}


def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return re.sub(r'\s+', ' ', text.replace('**', '').replace('__', '').strip(' |\t—–-:.;'))


def category_key(text):
    text = clean(text).casefold()
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]+', ' ', text)).strip()


def category_for(heading_text):
    label = category_key(heading_text)
    if label in CATEGORIES:
        return CATEGORIES[label]
    if label in NON_RESOURCE_SECTIONS:
        return None
    for pattern, category in CATEGORY_KEYWORDS:
        if pattern.search(label):
            return category
    return None


def is_template_line(line):
    urls = [match.group(2).rstrip('/.,;').casefold() for match in LINK.finditer(line)]
    return bool(urls) and all(url in TEMPLATE_URLS for url in urls)


def countries_from_index(markdown):
    countries = []
    seen = set()
    for line in markdown.splitlines():
        match = COUNTRY.match(line)
        if not match:
            continue
        name, owner, repo = match.groups()
        key = (owner.lower(), repo.lower())
        if key not in seen:
            countries.append({'name': clean(name), 'owner': owner, 'repo': repo})
            seen.add(key)
    return countries


def resources_from_readme(markdown, country, repo_url, candidates=None):
    resources = []
    category = None
    section = ''
    subsection = ''
    seen = set()
    in_code = False
    lines = markdown.splitlines()

    def add_resource(match, description):
        name, url = match.groups()
        name = clean(name)
        url = url.rstrip('.,;')
        # Tolerate an extra closing parenthesis after a Markdown link.
        description = re.sub(r'^\s*\)+', '', description)
        if not name or urlparse(url).scheme not in ('http', 'https') or (category, url) in seen:
            return
        seen.add((category, url))
        resources.append({
            'country': country,
            'category': category,
            'subsection': subsection,
            'name': name,
            'description': clean(description)[:500],
            'url': url,
            'source': repo_url + '/blob/HEAD/README.md',
        })

    def flag(line_number, reason, match, line):
        if candidates is not None and match:
            candidates.append({
                'country': country,
                'section': section,
                'line': line_number,
                'reason': reason,
                'url': match.group(2),
                'excerpt': line.strip()[:240],
                'source': repo_url + '/blob/HEAD/README.md',
            })

    for position, line in enumerate(lines):
        if re.match(r'^\s*(```|~~~)', line):
            in_code = not in_code
            continue
        if in_code:
            continue
        heading = HEADING.match(line)
        if heading:
            level = len(line) - len(line.lstrip('#'))
            heading_text = heading.group(1).strip()
            label = category_key(heading_text)
            if level == 2:
                section = clean(heading_text)
                category = category_for(heading_text)
                subsection = ''
            elif category == 'Vehicles' and level == 3 and not LINK.search(heading_text):
                subsection = clean(heading_text)
            if category and level in (3, 4) and re.match(r'^(?:\*\*)?\[', heading_text):
                match = LINK.search(heading_text)
                if match:
                    description = ''
                    for following in lines[position + 1:]:
                        if not following.strip():
                            continue
                        if HEADING.match(following) or BULLET.match(following) or following.startswith('|'):
                            break
                        description = following
                        break
                    add_resource(match, description)
            elif category and LINK.search(heading_text):
                flag(position + 1, 'unsupported_heading', LINK.search(heading_text), line)
            elif category is None and section and label not in NON_RESOURCE_SECTIONS and level != 2:
                flag(position + 1, 'unrecognized_section', LINK.search(line), line)
            continue
        match = LINK.search(line)
        if not match:
            continue
        if category and is_template_line(line):
            continue
        if category and (BULLET.match(line) or line.startswith('|')):
            add_resource(match, line[match.end():])
        elif category:
            flag(position + 1, 'unsupported_format', match, line)
        elif section.lower() not in NON_RESOURCE_SECTIONS and section:
            flag(position + 1, 'unrecognized_section', match, line)
    return resources


def github_get(path, accept='application/vnd.github+json'):
    request = urllib.request.Request(
        'https://api.github.com' + path,
        headers={
            'Accept': accept,
            'User-Agent': 'osint-countries-search-builder',
            **({'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN']} if os.environ.get('GITHUB_TOKEN') else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode('utf-8-sig')


def fetch_readme(owner, repo):
    return github_get(f'/repos/{owner}/{repo}/readme', 'application/vnd.github.raw+json')


def readme_updated(owner, repo):
    """Date of the last commit touching the README (an edit date, not a review date), or None."""
    try:
        path = json.loads(github_get(f'/repos/{owner}/{repo}/readme'))['path']
        commits = json.loads(github_get(f'/repos/{owner}/{repo}/commits?path={quote(path)}&per_page=1'))
        return commits[0]['commit']['committer']['date'][:10] if commits else None
    except (OSError, UnicodeError, ValueError, KeyError, IndexError, TypeError) as exc:
        print(f'WARNING: {owner}/{repo}: README date unavailable: {exc}', file=sys.stderr)
        return None


def build(output):
    index = fetch_readme(INDEX_OWNER, INDEX_REPO)
    countries = countries_from_index(index)
    if not countries:
        raise RuntimeError('No countries found in the canonical index README')
    generated_at = datetime.now(timezone.utc).isoformat()
    index_url = f'https://github.com/{INDEX_OWNER}/{INDEX_REPO}/blob/HEAD/README.md'
    records = []
    status = []
    candidates = []
    for item in countries:
        repo_url = f"https://github.com/{item['owner']}/{item['repo']}"
        country_candidates = []
        try:
            markdown = fetch_readme(item['owner'], item['repo'])
            found = resources_from_readme(markdown, item['name'], repo_url, country_candidates)
            if not found:
                raise ValueError('No resources recognized in README')
            records.extend(found)
            counts = {category: sum(r['category'] == category for r in found) for category in ORDER}
            status.append({'country': item['name'], 'repository': repo_url, 'count': len(found), 'categories': counts, 'candidates': len(country_candidates), 'readme_updated': readme_updated(item['owner'], item['repo']), 'ok': True})
            candidates.extend(country_candidates)
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"WARNING: {repo_url}: {exc}", file=sys.stderr)
            status.append({'country': item['name'], 'repository': repo_url, 'count': 0, 'categories': dict.fromkeys(ORDER, 0), 'candidates': 0, 'ok': False, 'error': str(exc)})
    if not records:
        raise RuntimeError('No resources collected; refusing to publish an empty index')
    data = {
        'generated_at': generated_at,
        'index_source': index_url,
        'countries': status,
        'resources': sorted(records, key=lambda r: (r['country'].casefold(), r['category'], r['name'].casefold())),
    }
    report = {
        'generated_at': generated_at,
        'index_source': index_url,
        'country_total': len(countries),
        'country_imported': sum(c['ok'] for c in status),
        'resource_total': len(records),
        'countries': status,
        'possible_omissions': candidates,
        'note': 'Possible omissions require manual review; zero resources in a category does not by itself prove a parsing error.',
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    output.with_name('import-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Indexed {len(records)} resources from {report['country_imported']}/{len(countries)} countries; {len(candidates)} candidate omissions -> {output}")


if __name__ == '__main__':
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'site' / 'resources.json')
