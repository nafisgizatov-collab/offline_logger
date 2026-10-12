"""Regression check: console continuation lines must append to text, not error flags."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ConsoleMultilineTest(unittest.TestCase):
    def test_report_preserves_multiline_records(self):
        analyzer = Path(__file__).with_name('build_background_report.py')
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / '2024-04-19_MainService-events.log').write_text('', encoding='utf-8')
            (folder / 'UI-console-keys').write_text('SyncManager:', encoding='utf-8')
            (folder / '2024-04-19_UI-console.log').write_text(
                'orphan line\n'
                '12:00:00.001 [INFO] SyncManager: start\ncontinued info\n(resources/test.js:1)\n'
                '12:00:01.002 [ERROR] first error\nstack trace\n'
                '12:00:02.003 [DEBUG] ignored\ncontinued ignored\n'
                '12:00:03.004 [ERROR] final error\nfinal continuation\n', encoding='utf-8')
            output = folder / 'report.html'
            result = subprocess.run([sys.executable, '-X', 'utf8', str(analyzer), str(folder), '--output', str(output)],
                                    capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = output.read_text(encoding='utf-8')
            rows = json.loads(html.split('const rows=', 1)[1].split(',meta=', 1)[0])
            self.assertEqual(len(rows), 3)
            info = next(row for row in rows if row['name'].startswith('SyncManager:'))
            self.assertIn('continued info', info['name'])
            self.assertNotIn('resources/test', info['name'])
            errors = [row for row in rows if row.get('has_error')]
            self.assertEqual(len(errors), 2)
            self.assertTrue(any('stack trace' in row['name'] for row in errors))
            self.assertTrue(any('final continuation' in row['name'] for row in errors))


if __name__ == '__main__':
    unittest.main()

