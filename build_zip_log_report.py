"""Build SabyLogReport from the newest application_logs date in a ZIP."""
import argparse
import datetime
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


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
            raise ValueError('No events.log files found in this ZIP.')
        return (None, 'ZIP / logs without a dated folder'), loose
    latest = max(date for date, prefix in groups)
    chosen = [(key, value) for key, value in groups.items() if key[0] == latest]
    if len(chosen) != 1:
        raise ValueError('Multiple application_logs folders have the newest date: ' + ', '.join(key[1] for key, _ in chosen))
    return chosen[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    archive_path = args.archive.resolve()
    output = archive_path.with_name(archive_path.stem + ' — SabyLogReport.html')
    with zipfile.ZipFile(archive_path) as archive:
        (date, prefix), entries = select_logs(archive)
        print('Log folder: ' + prefix, flush=True)
        print(f'Files: {len(entries)}; unpacked size: {sum(info.file_size for info, _ in entries) / 1048576:.1f} MB', flush=True)
        with tempfile.TemporaryDirectory(prefix='saby-zip-') as temp:
            root = Path(temp).resolve()
            for index, (info, parts) in enumerate(entries, 1):
                target = root.joinpath(*parts).resolve()
                if not target.is_relative_to(root):
                    raise ValueError('Unsafe ZIP entry: ' + info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                print(f'[{index}/{len(entries)}] {info.filename}', flush=True)
                with archive.open(info) as source, target.open('wb') as dest:
                    shutil.copyfileobj(source, dest)
            command = [sys.executable, '-u', str(Path(__file__).with_name('build_background_report.py')), str(root), '--recursive', '--output', str(output)]
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
