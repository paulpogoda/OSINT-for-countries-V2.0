#!/usr/bin/env python3
"""Replace the manual "Last Updated" line in indexed country READMEs with a last-commit badge.

The badge shows the date of the repository's last commit: an edit date, not a content review
(see STANDARD.md). Dry run by default; --apply commits through the GitHub API and needs
GITHUB_TOKEN with contents write access to the country repositories.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import ROOT, countries_from_index

LAST_UPDATED = re.compile(r'^[ \t]*[*_]*[ \t]*last[ \t]+updated[ \t]*[*_]*[ \t]*:.*$', re.I | re.M)
HEADING = re.compile(r'^#[ \t]+.*$', re.M)
BADGE_MARK = 'img.shields.io/github/last-commit/'
COMMIT_MESSAGE = 'Replace manual Last Updated date with last-commit badge'


def badge(owner, repo):
    return f'![Last updated](https://img.shields.io/github/last-commit/{owner}/{repo}?label=Last%20updated)'


def with_badge(markdown, line, insert_missing=False):
    """Return (new markdown, action); action is replaced, inserted, present or missing."""
    if BADGE_MARK in markdown:
        return markdown, 'present'
    if LAST_UPDATED.search(markdown):
        return LAST_UPDATED.sub(lambda _: line, markdown, count=1), 'replaced'
    heading = HEADING.search(markdown)
    if insert_missing and heading:
        return markdown[:heading.end()] + '\n' + line + markdown[heading.end():], 'inserted'
    return markdown, 'missing'


def api(method, path, body=None):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'osint-countries-badge-updater'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request('https://api.github.com' + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read())


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--apply', action='store_true', help='commit changes (default: dry run)')
    parser.add_argument('--insert-missing', action='store_true', help='add the badge under the first heading when no Last Updated line exists')
    parser.add_argument('--only', help='comma-separated country names')
    args = parser.parse_args()
    if args.apply and not os.environ.get('GITHUB_TOKEN'):
        raise SystemExit('--apply requires GITHUB_TOKEN')

    only = {name.strip() for name in args.only.split(',')} if args.only else None
    countries = countries_from_index((ROOT / 'README.md').read_text(encoding='utf-8'))
    if only:
        unknown = only - {c['name'] for c in countries}
        if unknown:
            raise SystemExit('Not in README index: ' + ', '.join(sorted(unknown)))
        countries = [c for c in countries if c['name'] in only]

    results = {}
    for item in countries:
        owner, repo, name = item['owner'], item['repo'], item['name']
        try:
            readme = api('GET', f'/repos/{owner}/{repo}/readme')
            markdown = base64.b64decode(readme['content']).decode('utf-8-sig')
            updated, action = with_badge(markdown, badge(owner, repo), args.insert_missing)
            if action in ('replaced', 'inserted'):
                old = LAST_UPDATED.search(markdown)
                print(f'{name}: {action} in {owner}/{repo}/{readme["path"]}')
                if old:
                    print(f'  - {old.group(0).strip()}')
                print(f'  + {badge(owner, repo)}')
                if args.apply:
                    if not api('GET', f'/repos/{owner}/{repo}').get('permissions', {}).get('push'):
                        action = 'no_push_access'
                    else:
                        api('PUT', f'/repos/{owner}/{repo}/contents/{quote(readme["path"])}', {
                            'message': COMMIT_MESSAGE,
                            'content': base64.b64encode(updated.encode('utf-8')).decode(),
                            'sha': readme['sha'],
                        })
                        action += '_committed'
        except (OSError, ValueError, KeyError) as exc:
            action = f'error: {exc}'
        results.setdefault(action, []).append(name)

    print()
    for action, names in sorted(results.items()):
        print(f'{action} ({len(names)}): {", ".join(names)}')
    if not args.apply:
        print('\nDry run; nothing committed. Re-run with --apply to commit.')


if __name__ == '__main__':
    main()
