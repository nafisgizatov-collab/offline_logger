"""Regression check: console continuation lines must append to text, not error flags."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ConsoleMultilineTest(unittest.TestCase):
    def test_fps_samples_bypass_console_filters_and_do_not_become_calls(self):
        analyzer=Path(__file__).with_name('build_background_report.py')
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            (folder/'2026-10-20_MainService-events.log').write_text('',encoding='utf-8')
            (folder/'UI-console-keys').write_text('unrelated',encoding='utf-8')
            (folder/'UI-console-ignore').write_text('fps',encoding='utf-8')
            (folder/'2026-10-20_UI-console.log').write_text(
                '12:00:00.000 [INFO] fps 60\n'
                '12:00:01.000 [INFO] fps 30.5 (resources/test.js:1)\n'
                '12:00:02.000 [INFO] fps 0\n'
                '12:00:03.000 [INFO] fps 59,5\n'
                '12:00:04.000 [INFO] fps invalid\n',encoding='utf-8')
            output=folder/'report.html'
            result=subprocess.run([sys.executable,'-X','utf8',str(analyzer),str(folder),'--output',str(output)],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            html=output.read_text(encoding='utf-8')
            meta=json.JSONDecoder().raw_decode(html.split(',meta=',1)[1])[0]
            rows=json.JSONDecoder().raw_decode(html.split('const rows=',1)[1])[0]
            self.assertEqual([x['value'] for x in meta['fps_samples']],[60,30.5,0,59.5])
            self.assertEqual([x['time'] for x in meta['fps_samples']],[0,1000,2000,3000])
            self.assertEqual(rows,[])

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

    def test_full_pass_boundaries_survive_custom_filters_and_midnight(self):
        analyzer = Path(__file__).with_name('build_background_report.py')
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / '2024-04-19_MainService-events.log').write_text('', encoding='utf-8')
            (folder / 'UI-console-keys').write_text('unrelated key', encoding='utf-8')
            (folder / 'UI-console-ignore').write_text('полного прохода', encoding='utf-8')
            (folder / '2024-04-19_UI-console.log').write_text(
                '23:59:59.900 [INFO] Начало полного прохода [RetailCycle test-a]\n'
                '00:00:00.250 [INFO] Конец полного прохода [RetailCycle test-a]\n'
                '00:00:01.000 [INFO] Начало полного прохода [RetailCycle interrupted]\n'
                '00:00:02.000 [INFO] unrelated noise\n', encoding='utf-8')
            output = folder / 'report.html'
            result = subprocess.run([sys.executable, '-X', 'utf8', str(analyzer), str(folder), '--output', str(output)],
                                    capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = output.read_text(encoding='utf-8')
            rows = json.loads(html.split('const rows=', 1)[1].split(',meta=', 1)[0])
            meta = json.JSONDecoder().raw_decode(html.split(',meta=', 1)[1])[0]
            markers = meta['console_markers']
            self.assertEqual([m['type'] for m in markers], ['full-pass-start', 'full-pass-end', 'full-pass-start'])
            self.assertEqual([m['label'] for m in markers], ['Начало', 'Конец', 'Начало'])
            self.assertEqual(markers[1]['time'] - markers[0]['time'], 350)
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(rows[m['node']]['kind'] == 'Консоль UI' for m in markers))


if __name__ == '__main__':
    unittest.main()

