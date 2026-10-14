import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import io
import urllib.error
from unittest.mock import patch

import set_last_updated_badge
from set_last_updated_badge import badge, with_badge

LINE = badge('paulpogoda', 'OSINT-Tools-Estonia')


class BadgeTests(unittest.TestCase):
    def test_badge_url(self):
        self.assertEqual(LINE, '![Last updated](https://img.shields.io/github/last-commit/paulpogoda/OSINT-Tools-Estonia?label=Last%20updated)')

    def test_replaces_template_line_variants(self):
        for line in ('**Last Updated:** DATE ', '**Last updated:** March 2025', 'Last Updated: 2024-01-05', '__Last Updated__: 05.01.2024'):
            markdown = f'# OSINT-Tools-Estonia\nIntro\n\n{line}\n\n## Legal Entities\n'
            updated, action = with_badge(markdown, LINE)
            self.assertEqual(action, 'replaced', line)
            self.assertEqual(updated, f'# OSINT-Tools-Estonia\nIntro\n\n{LINE}\n\n## Legal Entities\n')

    def test_only_first_line_replaced_and_prose_untouched(self):
        markdown = '**Last Updated:** May 2024\nThe registry was last updated in 2020.\n**Last Updated:** June\n'
        updated, _ = with_badge(markdown, LINE)
        self.assertEqual(updated, f'{LINE}\nThe registry was last updated in 2020.\n**Last Updated:** June\n')

    def test_existing_badge_is_left_alone(self):
        markdown = f'# X\n{LINE}\n**Last Updated:** May 2024\n'
        self.assertEqual(with_badge(markdown, LINE), (markdown, 'present'))

    def test_missing_line(self):
        markdown = '# OSINT-Tools-Estonia\nIntro\n'
        self.assertEqual(with_badge(markdown, LINE), (markdown, 'missing'))
        self.assertEqual(with_badge(markdown, LINE, insert_missing=True), (f'# OSINT-Tools-Estonia\n{LINE}\nIntro\n', 'inserted'))

    def test_insert_after_introduction_before_first_section(self):
        markdown = ('# OSINT-Tools-Estonia\n<img src="flag.png" alt="Estonia_FLAG"/>\n'
                    'A list of OSINT resources. \n\n## Contributions\nJoin\n## Legal Entities\n')
        updated, action = with_badge(markdown, LINE, insert_missing=True)
        self.assertEqual(action, 'inserted')
        self.assertEqual(updated, ('# OSINT-Tools-Estonia\n<img src="flag.png" alt="Estonia_FLAG"/>\n'
                                   f'A list of OSINT resources.\n\n{LINE}\n\n## Contributions\nJoin\n## Legal Entities\n'))

    def test_api_error_includes_github_message(self):
        error = urllib.error.HTTPError('https://api.github.com/x', 403, 'Forbidden', {},
                                       io.BytesIO(b'{"message": "Resource not accessible by personal access token"}'))
        with patch.object(set_last_updated_badge.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaises(OSError) as ctx:
                set_last_updated_badge.api('PUT', '/repos/o/r/contents/README.md', {})
        self.assertEqual(str(ctx.exception), 'PUT /repos/o/r/contents/README.md: HTTP 403: Resource not accessible by personal access token')


if __name__ == '__main__':
    unittest.main()
