"""Portable checks for macOS package contents, Finder plist and shell argument quoting."""
from pathlib import Path
import plistlib
import shlex
import shutil
import sys
import tempfile
import unittest
import subprocess
import zipfile

from install_macos import install, workflow_documents, FILES, TITLE
from run_macos import report_command, terminal_job


class MacInstallerTest(unittest.TestCase):
    def test_install_update_and_preserve_local_filters(self):
        source = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "User's home with spaces"
            destination, workflow = install(source, home, Path(sys.executable))
            for name in FILES:
                self.assertTrue((destination / 'resources' / name).is_file())
            document = plistlib.loads((workflow / 'Contents/document.wflow').read_bytes())
            info = plistlib.loads((workflow / 'Contents/Info.plist').read_bytes())
            self.assertEqual(info['NSServices'][0]['NSMenuItem']['default'], TITLE)
            self.assertEqual(info['NSServices'][0]['NSRequiredContext']['NSApplicationIdentifier'], 'com.apple.finder')
            action = document['actions'][0]['action']['ActionParameters']
            self.assertEqual(action['inputMethod'], 1)
            args = shlex.split(action['COMMAND_STRING'])
            self.assertEqual(args[0], str(Path(sys.executable)))
            self.assertEqual(args[1], str(destination / 'resources/run_macos.py'))
            self.assertEqual(args[2:], ['--terminal', '$@'])
            filters = destination / 'resources/UI-console-ignore'
            filters.write_text('my custom filter', encoding='utf-8')
            install(source, home, Path(sys.executable))
            self.assertEqual(filters.read_text(encoding='utf-8'), 'my custom filter')
            # Re-running the installed local package must not copy a file onto itself.
            install(destination, home, Path(sys.executable))
            self.assertEqual(filters.read_text(encoding='utf-8'), 'my custom filter')
            update = (destination / 'Обновить анализатор.command').read_text(encoding='utf-8')
            self.assertEqual(shlex.split(update.splitlines()[1]),
                             ['exec', str(destination / 'installSabyLogContextMenu-macOS.command'), '--update'])

    def test_corrupt_python_payload_does_not_replace_installed_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'package'
            (source / 'resources').mkdir(parents=True)
            original = Path(__file__).resolve().parent.parent
            installer = 'installSabyLogContextMenu-macOS.command'
            shutil.copy2(original / installer, source / installer)
            for name in FILES:
                shutil.copy2(original / 'resources' / name, source / 'resources' / name)
            home = root / 'home'
            destination, _ = install(source, home, Path(sys.executable))
            target = destination / 'resources/build_background_report.py'
            before = target.read_bytes()
            (source / 'resources/build_background_report.py').write_bytes(b'# broken\ntext = "\xd0"\n')
            with self.assertRaisesRegex(RuntimeError, '--update'):
                install(source, home, Path(sys.executable))
            self.assertEqual(target.read_bytes(), before)

    def test_terminal_job_quotes_file_names_without_evaluating_them(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "folder 'quote' $(not_a_command); & name.zip"
            runner = root / 'app resources/run_macos.py'
            job = terminal_job([target], runner, Path(sys.executable), root / 'jobs')
            command = shlex.split(job.read_text(encoding='utf-8').splitlines()[1])
            self.assertEqual(command, [sys.executable, '-u', str(runner), '--run', str(target)])

    def test_folder_archive_and_unsupported_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); resources = root / 'resources'; downloads = root / 'Downloads'
            folder = root / 'Logs with spaces'; folder.mkdir()
            command = report_command(folder, resources, downloads, Path(sys.executable))
            self.assertIn('--recursive', command)
            self.assertEqual(command[command.index('--output') + 1], str(downloads / 'Logs with spaces — SabyLogReport.html'))
            for suffix in ('.zip', '.7z'):
                archive = root / ('Archive' + suffix); archive.touch()
                command = report_command(archive, resources, downloads, Path(sys.executable))
                self.assertIn(str(resources / 'build_zip_log_report.py'), command)
                self.assertIn('--serve', command)
                self.assertEqual(command[command.index('--output') + 1], str(downloads / 'Archive — SabyLogReport.html'))
            unsupported = root / 'other.txt'; unsupported.touch()
            with self.assertRaises(ValueError):
                report_command(unsupported, resources, downloads, Path(sys.executable))

    def test_archive_report_uses_downloads_output(self):
        resources = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); downloads = root / 'Downloads with spaces'; downloads.mkdir()
            archive = root / 'Logs archive.zip'
            row = '\t'.join(('12:00:00.001', '[1][2]', '1', 'INFO', 'trace', 'trace', '0', '0',
                             'Test.Method/1', '[m][finish] Test.Method [exec_period] 1'))+'\n'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('application_logs/20261009/2026-10-09_MainService-events.log', row)
            command = report_command(archive, resources, downloads, Path(sys.executable))
            # Do not start a browser/server from the portable regression check.
            self.assertEqual(command.pop(), '--serve')
            result = subprocess.run(command, capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertTrue((downloads / 'Logs archive — SabyLogReport.html').is_file())
            self.assertFalse((root / 'Logs archive — SabyLogReport.html').exists())


if __name__ == '__main__':unittest.main()
