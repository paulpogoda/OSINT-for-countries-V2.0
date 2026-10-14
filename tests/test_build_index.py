import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_index
from build_index import countries_from_index, resources_from_readme


class ParserTests(unittest.TestCase):
    def test_country_table_uses_first_cell_only(self):
        markdown = '| 🇰🇿 [Kazakhstan](https://github.com/paulpogoda/OSINT-Tools-Kazakhstan) | [Fork](https://github.com/other/fork) | ✅ Active |\n'
        self.assertEqual(countries_from_index(markdown), [{'name': 'Kazakhstan', 'owner': 'paulpogoda', 'repo': 'OSINT-Tools-Kazakhstan'}])

    def test_cuba_and_bulgaria_tree_links(self):
        markdown = '''| 🇧🇬 [Bulgaria](https://github.com/paulpogoda/OSINT-Tools-Bulgaria/tree/main) | @paulpogoda | Active |
| 🇨🇺 [Cuba](https://github.com/paulpogoda/osint-tools-cuba/tree/main) | @paulpogoda | Active |
'''
        self.assertEqual(
            [(item['name'], item['repo']) for item in countries_from_index(markdown)],
            [('Bulgaria', 'OSINT-Tools-Bulgaria'), ('Cuba', 'osint-tools-cuba')],
        )

    def test_categories_and_vehicle_subsection(self):
        markdown = '''## Table of contents
- [Registry](https://example.org/navigation)
## Legal Entities
- **[Company Registry](https://example.org/companies)** — Official registry
## Vehicles
### Land Vehicles
- [VIN Decoder](https://example.org/vin) - Search by VIN
## Legal Disclaimer
- [Policy](https://example.org/policy)
'''
        rows = resources_from_readme(markdown, 'Kazakhstan', 'https://github.com/example/repo')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['category'], 'Legal Entities')
        self.assertEqual(rows[1]['subsection'], 'Land Vehicles')

    def test_cuba_category_punctuation_and_icon(self):
        markdown = '''## People, Phones, Social etc.
- [Directory](https://example.org/people) - People search
## 🌐 WHOIS
- [NIC.cu](https://example.org/whois) - Domain information
'''
        rows = resources_from_readme(markdown, 'Cuba', 'https://github.com/paulpogoda/osint-tools-cuba')
        self.assertEqual([row['category'] for row in rows], ['People, phones, social etc.', 'WHOIS'])

    def test_switzerland_people_heading_without_etc(self):
        markdown = '''## People, Phones, Social
### Professional Registries
- **[MedReg — Register of Medical Professions](https://healthreg-public.admin.ch)**: Official medical professions register
### Phone & Contact Directories
- **[Tel.Search](https://tel.search.ch/index.en.html)**: Swiss phone numbers and addresses
## Public Procurements
- **[SIMAP](https://www.simap.ch)**: Official Swiss public procurement
'''
        candidates = []
        rows = resources_from_readme(markdown, 'Switzerland', 'https://github.com/Provereno-Media/OSINT-Tools-Switzerland', candidates)
        self.assertEqual([row['name'] for row in rows], ['MedReg — Register of Medical Professions', 'Tel.Search', 'SIMAP'])
        self.assertEqual([row['category'] for row in rows], ['People, phones, social etc.', 'People, phones, social etc.', 'Public procurements'])
        self.assertEqual(candidates, [])

    def test_kazakhstan_procurement_linked_heading(self):
        markdown = '''## Public procurement
### [Public procurement portal](https://goszakup.gov.kz/)
The public procurement portal is a state information system.
## WHOIS
- [Domain lookup](https://example.org/whois) - Lookup
'''
        rows = resources_from_readme(markdown, 'Kazakhstan', 'https://github.com/example/repo')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['category'], 'Public procurements')
        self.assertEqual(rows[0]['url'], 'https://goszakup.gov.kz/')
        self.assertIn('state information system', rows[0]['description'])

    def test_descriptions_start_after_closing_link_parenthesis(self):
        markdown = '''## Open Data portals
- [Portal](https://example.org/portal) — Official open data
- [Unannotated](https://example.org/empty)
| [Statistics](https://example.org/stats) | National statistics |
- [Cadastral Map](https://example.org/map)). Paid (Bulgarian & English)
## Public procurements
### [Tenders](https://example.org/tenders)
Government tenders and awards.
'''
        rows = resources_from_readme(markdown, 'Example', 'https://github.com/example/repo')
        self.assertEqual(
            [row['description'] for row in rows],
            ['Official open data', '', 'National statistics', 'Paid (Bulgarian & English)', 'Government tenders and awards'],
        )

    def test_unrecognized_resource_link_is_reported(self):
        markdown = '''## Maps
Official resource: [Map](https://example.org/map)
## Other registries
- [Registry](https://example.org/registry)
'''
        candidates = []
        rows = resources_from_readme(markdown, 'Example', 'https://github.com/example/repo', candidates)
        self.assertEqual(rows, [])
        self.assertEqual([c['reason'] for c in candidates], ['unsupported_format', 'unrecognized_section'])
        self.assertEqual([c['line'] for c in candidates], [2, 4])

    def test_variant_headings_map_by_keyword(self):
        markdown = '''## Cadastral and Maps
- [County GIS](https://example.org/gis) - Parcels
## Open Data
- [Portal](https://example.org/data) - Datasets
## Courts
- [Court portal](https://example.org/courts) - Decisions
## Stock
- [Exchange](https://example.org/exchange) - Listings
## Appendox
- [Sanctions](https://example.org/sanctions) - Lists
## Related Resources
- [Other list](https://example.org/other) - Links
'''
        candidates = []
        rows = resources_from_readme(markdown, 'Example', 'https://github.com/example/repo', candidates)
        self.assertEqual(
            [(row['name'], row['category']) for row in rows],
            [('County GIS', 'Cadastral and other Maps'), ('Portal', 'Open Data portals'),
             ('Court portal', 'Open Data portals'), ('Exchange', 'Open Data portals')],
        )
        self.assertEqual([c['section'] for c in candidates], ['Appendox', 'Related Resources'])

    def test_non_resource_sections_are_not_matched_by_keyword(self):
        for heading in ('Table of contents', 'Contributing', 'Legal Disclaimer', 'Appendix', '🔍 Search Tips & Best Practices'):
            self.assertIsNone(build_index.category_for(heading), heading)

    def test_template_people_line_is_skipped(self):
        markdown = '''## People
- [Phone directory](https://example.org/phones) - Phone numbers
- Try [OSINT Industries](https://app.osint.industries) and don't forget about the [Digital Profiler's Toolkit](https://github.com/paulpogoda/Digital-Profiler-s-Toolkit)
- [OSINT Industries](https://app.osint.industries) with [local guide](https://example.org/guide)
'''
        rows = resources_from_readme(markdown, 'Example', 'https://github.com/example/repo')
        self.assertEqual([row['name'] for row in rows], ['Phone directory', 'OSINT Industries'])

    def test_index_repository_from_environment(self):
        with patch.dict(build_index.os.environ, {'INDEX_REPOSITORY': '', 'GITHUB_REPOSITORY': 'pogoda-provereno/OSINT-for-countries-V2.0'}):
            self.assertEqual(build_index.index_repository(), ('pogoda-provereno', 'OSINT-for-countries-V2.0'))
        with patch.dict(build_index.os.environ, {'INDEX_REPOSITORY': 'Provereno-Media/OSINT-for-countries-V2.0', 'GITHUB_REPOSITORY': 'fork/x'}):
            self.assertEqual(build_index.index_repository(), ('Provereno-Media', 'OSINT-for-countries-V2.0'))
        with patch.dict(build_index.os.environ, {'INDEX_REPOSITORY': '', 'GITHUB_REPOSITORY': ''}):
            self.assertEqual(build_index.index_repository(), ('Provereno-Media', 'OSINT-for-countries-V2.0'))
        with patch.dict(build_index.os.environ, {'INDEX_REPOSITORY': 'not-a-repo'}):
            with self.assertRaises(ValueError):
                build_index.index_repository()

    def test_build_reads_canonical_repo_and_writes_report(self):
        index = '| [Example](https://github.com/example/OSINT-Tools-Example) | author | Active |\n'
        country = '## Maps\n- [Map](https://example.org/map) - Official map\n'
        def fake_readme(owner, repo):
            if (owner, repo) == (build_index.INDEX_OWNER, build_index.INDEX_REPO):
                return index
            self.assertEqual((owner, repo), ('example', 'OSINT-Tools-Example'))
            return country
        with tempfile.TemporaryDirectory() as folder, patch.object(build_index, 'fetch_readme', side_effect=fake_readme), \
                patch.object(build_index, 'last_commit', return_value='2026-01-31'):
            output = Path(folder) / 'site' / 'resources.json'
            build_index.build(output)
            data = json.loads(output.read_text(encoding='utf-8'))
            report = json.loads(output.with_name('import-report.json').read_text(encoding='utf-8'))
        self.assertEqual(data['countries'][0]['categories']['Cadastral and other Maps'], 1)
        self.assertEqual(data['countries'][0]['last_commit'], '2026-01-31')
        self.assertEqual(report['country_imported'], 1)
        self.assertEqual(report['resource_total'], 1)
        self.assertEqual(report['possible_omissions'], [])

    def test_last_commit_date(self):
        response = '[{"commit": {"committer": {"date": "2025-04-03T10:00:00Z"}}}]'
        with patch.object(build_index, 'github_get', return_value=response) as get:
            self.assertEqual(build_index.last_commit('o', 'r'), '2025-04-03')
        get.assert_called_once_with('/repos/o/r/commits?per_page=1')

    def test_last_commit_empty_or_failure_is_none(self):
        with patch.object(build_index, 'github_get', return_value='[]'):
            self.assertIsNone(build_index.last_commit('o', 'r'))
        with patch.object(build_index, 'github_get', side_effect=OSError('HTTP 404')):
            self.assertIsNone(build_index.last_commit('o', 'r'))


if __name__ == '__main__':
    unittest.main()
