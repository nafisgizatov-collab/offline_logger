"""Finder entry point: run folder/ZIP/7z reports with progress in Terminal."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys
import uuid


def report_command(target, resources, downloads, python):
    target = target.resolve()
    output = downloads / (target.stem if target.is_file() else target.name)
    output = output.with_name(output.name + ' — SabyLogReport.html')
    if target.is_dir():
        return [str(python), '-u', str(resources / 'build_background_report.py'), str(target),
                '--recursive', '--output', str(output), '--serve']
    if target.is_file() and target.suffix.lower() in ('.zip', '.7z'):
        return [str(python), '-u', str(resources / 'build_zip_log_report.py'), str(target),
                '--output', str(output), '--serve']
    raise ValueError('Выберите папку с логами, .zip или .7z: ' + str(target))


def terminal_job(targets, runner, python, jobs):
    jobs.mkdir(parents=True, exist_ok=True)
    job = jobs / ('report-' + uuid.uuid4().hex + '.command')
    command = shlex.join([str(python), '-u', str(runner), '--run'] + [str(p) for p in targets])
    job.write_text('#!/bin/bash\n' + command + '\nstatus=$?\n'
                   'printf "\\nЗавершено. Код: %s\\n" "$status"\n'
                   'read -r -p "Нажмите Enter, чтобы закрыть окно… " unused\n'
                   'exit "$status"\n', encoding='utf-8')
    job.chmod(0o700)
    return job


def main():
    if sys.platform != 'darwin':
        raise RuntimeError('Этот запуск предназначен для macOS.')
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--terminal', action='store_true')
    mode.add_argument('--run', action='store_true')
    parser.add_argument('targets', type=Path, nargs='+')
    args = parser.parse_args()
    home = Path.home(); resources = Path(__file__).resolve().parent
    downloads = home / 'Downloads'
    downloads.mkdir(exist_ok=True)
    # Finder does not inherit a user's interactive shell PATH.
    os.environ['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + os.environ.get('PATH', '/usr/bin:/bin')
    if args.terminal:
        job = terminal_job(args.targets, Path(__file__).resolve(), Path(sys.executable),
                           home / 'Library/Logs/SabyOfflineLogger/jobs')
        subprocess.run(['/usr/bin/open', '-a', 'Terminal', str(job)], check=True)
        return
    for target in args.targets:
        command = report_command(target, resources, downloads, Path(sys.executable))
        print('Построение отчета: ' + str(target), flush=True)
        subprocess.run(command, check=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
