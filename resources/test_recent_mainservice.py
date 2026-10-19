"""Limit rotated MainService logs before parsing and preserve the selected time window."""
import datetime
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import unittest
import zipfile

from build_background_report import select_recent_mainservice, log_file_bounds


def record(time, message, trace='trace', context='Test.Method/1'):
    return '\t'.join((time, '[1][2]', '1', 'INFO', trace, trace, '0', '0', context, message))+'\n'


class RecentMainServiceTest(unittest.TestCase):
    def test_sql_time_literal_does_not_extend_timeline(self):
        analyzer=Path(__file__).with_name('build_background_report.py')
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            log=folder/'2026-10-19_MainService-events.log'
            log.write_text(record('14:00:25.844','[w][start]')+
                           record('14:00:25.845','[sql][start]')+
                           'args:\n12:00:23.265::time without time zone;\n'+
                           record('14:00:26.000','[w][finish] [exec_period] 156')+
                           '01:00:00.000::time without time zone;\n',encoding='utf-8')
            start,end=log_file_bounds(log)
            self.assertEqual(end-start,156)
            output=folder/'report.html'
            result=subprocess.run([sys.executable,'-X','utf8',str(analyzer),str(folder),'--output',str(output)],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            html=output.read_text(encoding='utf-8')
            meta=json.JSONDecoder().raw_decode(html.split(',meta=',1)[1])[0]
            self.assertTrue(meta['logStart'].endswith('14:00:25.844'),meta['logStart'])
            self.assertTrue(meta['logEnd'].endswith('14:00:26.000'),meta['logEnd'])
            self.assertEqual(meta['span'],156)

    def test_paired_end_marker_after_mainservice_window_is_preserved(self):
        analyzer=Path(__file__).with_name('build_background_report.py')
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            for i in range(1,5):
                (folder/f'2026-10-19_MainService-events_{i:03}.log').write_text(record(f'14:0{i}:00.000','[m][finish] Test.Method [exec_period] 0'),encoding='utf-8')
            (folder/'2026-10-19_UI-console.log').write_text(
                '14:01:00.000 [INFO] Начало полного прохода [RetailCycle old]\n'
                '14:03:00.000 [INFO] Начало полного прохода [RetailCycle current]\n'
                '14:04:03.000 [INFO] Конец полного прохода — +63.000 с от ввода ПИН-кода до закрытия смены [RetailCycle current]\n'
                '14:05:00.000 [ERROR] outside error\n'
                '14:06:00.000 [INFO] Конец полного прохода [RetailCycle old]\n',encoding='utf-8')
            output=folder/'report.html'
            result=subprocess.run([sys.executable,'-X','utf8',str(analyzer),str(folder),'--output',str(output)],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            html=output.read_text(encoding='utf-8')
            meta=json.JSONDecoder().raw_decode(html.split(',meta=',1)[1])[0]
            markers=meta['console_markers']
            self.assertEqual([m['label'] for m in markers],['Начало','Конец · 63,000 с'])
            self.assertEqual(markers[1]['time']-markers[0]['time'],63000)
            self.assertEqual(markers[1]['elapsed_seconds'],63)
            self.assertTrue(meta['logEnd'].endswith('14:04:03.000'),meta['logEnd'])

    def test_natural_rotation_order_not_mtime(self):
        paths=[PurePosixPath(f'2026-10-09_MainService-events_{i}.log') for i in range(1,21)]
        paths.reverse()
        paths += [PurePosixPath('2026-10-09_MainService-events.log'), PurePosixPath('2026-10-09_UI-events.log')]
        kept, selected, skipped=select_recent_mainservice(paths)
        self.assertEqual([p.name for p in selected], [f'2026-10-09_MainService-events_{i}.log' for i in (18,19,20)])
        self.assertEqual(len(skipped),18)
        self.assertEqual(len(kept),4)
        self.assertFalse(select_recent_mainservice(selected)[2])

    def test_bounds_midnight_and_long_continuation(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'2026-10-09_MainService-events.log'
            p.write_text('23:59:59.000 first\n00:00:01.000 last\n'+('x'*150000),encoding='utf-8')
            start,end=log_file_bounds(p)
            self.assertEqual(end-start,2000)

    def test_folder_and_zip_keep_three_and_clip_other_sources(self):
        analyzer=Path(__file__).with_name('build_background_report.py')
        zipper=Path(__file__).with_name('build_zip_log_report.py')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'logs';folder.mkdir()
            for i in range(1,21):
                (folder/f'2026-10-09_MainService-events_{i:03}.log').write_text(
                    record(f'12:{i:02}:00.000','[w][start]',str(i),f'Test.Method{i}/1')+
                    record(f'12:{i:02}:10.000','[w][finish] [exec_period] 10000',str(i),f'Test.Method{i}/1'),encoding='utf-8')
            (folder/'2026-10-09_UI-events.log').write_text(
                record('10:00:00.000','[m][finish] Old.Method [exec_period] 1')+
                record('12:18:01.000','[m][finish] Crossing.Method [exec_period] 60000')+
                record('15:00:00.000','[m][finish] Late.Method [exec_period] 1'),encoding='utf-8')
            (folder/'2026-10-09_UI-console.log').write_text(
                '10:00:00.000 [ERROR] old error\n12:19:00.000 [ERROR] selected error\n15:00:00.000 [ERROR] late error\n',encoding='utf-8')
            (folder/'2026-10-09_UI-errors.log').write_text(record('16:00:00.000','outside error'),encoding='utf-8')
            entries=[]
            for hour in (10,12,16):
                entries.append(dict(startedDateTime=datetime.datetime(2026,10,9,hour,19).astimezone().isoformat(),time=5,
                                    request={'postData':{'text':json.dumps({'method':f'Har.Hour{hour}'})}}))
            (folder/'calls.har').write_text(json.dumps({'log':{'entries':entries}}),encoding='utf-8')
            archive=root/'test.zip'
            with zipfile.ZipFile(archive,'w') as z:
                for p in folder.iterdir():z.write(p,'logs/application_logs/20261009/'+p.name)
            for script,input_path,output in ((analyzer,folder,folder/'report.html'),
                                             (zipper,archive,root/'test — SabyLogReport.html')):
                args=[sys.executable,'-X','utf8',str(script),str(input_path)]
                if script==analyzer:args+=['--output',str(output)]
                result=subprocess.run(args,capture_output=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                text=output.read_text(encoding='utf-8');decoder=json.JSONDecoder()
                rows,end=decoder.raw_decode(text,text.index('const rows=')+len('const rows='))
                meta,_=decoder.raw_decode(text,end+len(',meta='))
                self.assertEqual(meta['mainservice_selection']['skipped'],17)
                self.assertEqual(meta['logStart'],'2026-10-09 12:18:00.000')
                self.assertEqual(meta['logEnd'],'2026-10-09 12:20:10.000')
                names={r['name'] for r in rows}
                self.assertEqual({n for n in names if n.startswith('Test.Method')}, {'Test.Method18','Test.Method19','Test.Method20'})
                self.assertFalse({'Old.Method','Late.Method','old error','late error','Har.Hour10','Har.Hour16'} & names)
                self.assertIn('selected error',names)
                self.assertIn('Har.Hour12',names)
                self.assertTrue(all(0<=r['start']<=r['end']<=meta['span'] for r in rows))
                if script==zipper:
                    self.assertIn('omitted 17 before extraction',result.stdout)
                    self.assertNotIn('] logs/application_logs/20261009/2026-10-09_MainService-events_001.log',result.stdout)


if __name__=='__main__':unittest.main()
