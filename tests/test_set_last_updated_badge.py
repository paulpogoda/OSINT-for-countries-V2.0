import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
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


if __name__ == '__main__':
    unittest.main()
