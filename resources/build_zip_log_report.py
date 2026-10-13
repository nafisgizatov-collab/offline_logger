"""Build SabyLogReport from the newest application_logs date in a ZIP or 7z archive."""
import argparse
import contextlib
import os
from types import SimpleNamespace
import datetime
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from build_background_report import select_recent_mainservice


def select_logs(archive):
    groups = {}
    dated = {}
    loose = []
    for info in archive.infolist():
        if info.is_dir():
            continue
        parts = PurePosixPath(info.filename.replace('\\', '/')).parts
        if not parts or parts[0] == '/' or '..' in parts or any(':' in part for part in parts):
            continue
        if not parts[-1].lower().endswith(('.log', '.har')):
            continue
        loose.append((info, parts))
        for i, part in enumerate(parts[:-1]):
            digits = re.sub(r'[-_.]', '', part)
            if not re.fullmatch(r'\d{8}', digits):
                continue
            try:
                date = datetime.datetime.strptime(digits, '%Y%m%d').date()
            except ValueError:
                continue
            prefix = '/'.join(parts[:i + 1])
            dated.setdefault((date, prefix), []).append((info, parts[i + 1:]))
            break
        for i, part in enumerate(parts[:-2]):
            if part.lower() != 'application_logs':
                continue
            date_name = parts[i + 1]
            digits = re.sub(r'[-_.]', '', date_name)
            if not re.fullmatch(r'\d{8}', digits):
                continue
            try:
                date = datetime.datetime.strptime(digits, '%Y%m%d').date()
            except ValueError:
                continue
            if not parts[-1].lower().endswith(('.log', '.har')):
                continue
            prefix = '/'.join(parts[:i + 2])
            groups.setdefault((date, prefix), []).append((info, parts[i + 2:]))
    if not groups:
        groups = dated
    if not groups:
        events = re.compile(r'(?:-|_)events(?:_\d+)?\.log$', re.I)
        if not any(events.search(parts[-1]) for info, parts in loose):
            raise ValueError('No events.log files found in this archive.')
        return (None, 'Archive / logs without a dated folder'), loose
    latest = max(date for date, prefix in groups)
    chosen = [(key, value) for key, value in groups.items() if key[0] == latest]
    if len(chosen) != 1:
        raise ValueError('Multiple application_logs folders have the newest date: ' + ', '.join(key[1] for key, _ in chosen))
    return chosen[0]


class SevenZipArchive:
    def __init__(self, path):
        self.path = path
        candidates = [shutil.which(name) for name in ('7z', '7zz', '7za')]
        candidates += [str(Path(os.environ.get(env, 'C:/Program Files')) / '7-Zip' / '7z.exe')
                       for env in ('ProgramFiles', 'ProgramFiles(x86)')]
        self.executable = next((item for item in candidates if item and Path(item).is_file()), None)
        if not self.executable:
            raise RuntimeError('Reading .7z requires 7-Zip. Install it from https://www.7-zip.org/ and retry.')

    def infolist(self):
        result = subprocess.run([self.executable, 'l', '-slt', '-sccUTF-8', '--', str(self.path)],
                                capture_output=True, encoding='utf-8', errors='replace', check=True)
        listing = result.stdout.split('----------', 1)
        if len(listing) != 2:
            raise ValueError('Cannot read 7z archive listing.')
        entries = []
        for block in re.split(r'\r?\n\s*\r?\n', listing[1].strip()):
            fields = dict(line.split(' = ', 1) for line in block.splitlines() if ' = ' in line)
            if 'Path' not in fields:
                continue
            directory = fields.get('Folder') == '+' or fields.get('Attributes', '').startswith('D')
            entries.append(SimpleNamespace(filename=fields['Path'], file_size=int(fields.get('Size', 0)),
                                           is_dir=lambda directory=directory: directory))
        return entries

    @contextlib.contextmanager
    def open(self, info):
        # Stream one exact entry; never extract archive-supplied filesystem paths.
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen([self.executable, 'e', '-so', '-spd', '-y', '-p', '--',
                                        str(self.path), info.filename], stdout=subprocess.PIPE,
                                       stderr=errors, stdin=subprocess.DEVNULL)
            try:
                yield process.stdout
            finally:
                process.stdout.close()
                code = process.wait()
            if code:
                errors.seek(0)
                raise RuntimeError('7z extraction failed: ' + errors.read().decode('utf-8', errors='replace'))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    archive_path = args.archive.resolve()
    output = archive_path.with_name(archive_path.stem + ' — SabyLogReport.html')
    if archive_path.suffix.lower() not in ('.zip', '.7z'):
        raise ValueError('Supported archives: .zip and .7z')
    archive_type = SevenZipArchive if archive_path.suffix.lower() == '.7z' else zipfile.ZipFile
    with archive_type(archive_path) as archive:
        (date, prefix), entries = select_logs(archive)
        paths = [PurePosixPath(info.filename.replace('\\', '/')) for info, _ in entries]
        _, _, omitted = select_recent_mainservice(paths)
        entries = [(info, parts) for info, parts in entries
                   if PurePosixPath(info.filename.replace('\\', '/')) not in omitted]
        print('Log folder: ' + prefix, flush=True)
        if omitted:
            print(f'MainService-events: keeping latest 3; omitted {len(omitted)} before extraction', flush=True)
        print(f'Files: {len(entries)}; unpacked size: {sum(info.file_size for info, _ in entries) / 1048576:.1f} MB', flush=True)
        with tempfile.TemporaryDirectory(prefix='saby-zip-') as temp:
            root = Path(temp).resolve()
            for index, (info, parts) in enumerate(entries, 1):
                target = root.joinpath(*parts).resolve()
                if not target.is_relative_to(root):
                    raise ValueError('Unsafe archive entry: ' + info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                print(f'[{index}/{len(entries)}] {info.filename}', flush=True)
                with archive.open(info) as source, target.open('wb') as dest:
                    shutil.copyfileobj(source, dest)
            command = [sys.executable, '-u', str(Path(__file__).with_name('build_background_report.py')), str(root), '--recursive', '--output', str(output)]
            if omitted:
                command += ['--omitted-mainservice-files', str(len(omitted))]
            if args.serve:
                command.append('--serve')
            subprocess.run(command, check=True)
    print('Report: ' + str(output), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
