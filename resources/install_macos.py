"""Install the analyzer and a per-user Finder Quick Action on macOS."""
import argparse
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import uuid

TITLE = 'Построить отчет логов оффлайн'
FILES = ('build_background_report.py', 'build_zip_log_report.py', 'install_macos.py',
         'run_macos.py', 'UI-console-keys', 'UI-console-ignore')


def workflow_documents(python, runner):
    command = shlex.join([str(python), str(runner), '--terminal']) + ' "$@"'
    action = {
        'AMAccepts': {'Container': 'List', 'Optional': False, 'Types': ['com.apple.cocoa.path']},
        'AMProvides': {'Container': 'List', 'Types': ['com.apple.cocoa.string']},
        'AMActionVersion': '2.0.3', 'AMApplication': [],
        'ActionBundlePath': '/System/Library/Automator/Run Shell Script.action',
        'ActionName': 'Run Shell Script', 'BundleIdentifier': 'com.apple.RunShellScript',
        'ActionParameters': {'COMMAND_STRING': command, 'inputMethod': 1, 'shell': '/bin/bash'},
        'CanShowSelectedItemsWhenRun': False, 'CanShowWhenRun': True,
        'InputUUID': str(uuid.uuid4()), 'OutputUUID': str(uuid.uuid4()), 'UUID': str(uuid.uuid4()),
        'isViewVisible': True,
    }
    document = {'AMApplicationBuild': '523', 'AMApplicationVersion': '2.10',
                'AMDocumentVersion': '2', 'actions': [{'action': action}], 'connectors': [],
                'workflowMetaData': {
                    'workflowTypeIdentifier': 'com.apple.Automator.servicesMenu',
                    'serviceInputTypeIdentifier': 'com.apple.Automator.fileSystemObject',
                    'serviceOutputTypeIdentifier': 'com.apple.Automator.nothing',
                    'serviceApplicationBundleID': 'com.apple.finder',
                    'serviceApplicationPath': '/System/Library/CoreServices/Finder.app',
                    'serviceProcessesInput': 0, 'serviceReceivesInput': 1, 'serviceRequiresInput': 1,
                    'useAutomaticInputType': False,
                }}
    info = {'CFBundleIdentifier': 'ru.saby.offline-logger.finder-report',
            'CFBundleName': TITLE, 'CFBundleVersion': '1.0',
            'NSServices': [{'NSMenuItem': {'default': TITLE}, 'NSMessage': 'runWorkflowAsService',
                            'NSRequiredContext': {'NSApplicationIdentifier': 'com.apple.finder'},
                            'NSSendTypes': ['NSFilenamesPboardType'], 'NSReturnTypes': []}]}
    return document, info


def install(source, home, python):
    source = source.resolve()
    installer = source / 'installSabyLogContextMenu-macOS.command'
    required = [installer] + [source / 'resources' / name for name in FILES]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError('В пакете отсутствует файл: ' + str(path))
    # Validate all payloads before replacing any installed files.
    for name in FILES:
        if name.endswith('.py'):
            payload = source / 'resources' / name
            try:
                text = payload.read_bytes().decode('utf-8-sig')
                compile(text, str(payload), 'exec')
            except (UnicodeError, SyntaxError) as error:
                raise RuntimeError(
                    'Поврежден Python-файл пакета: ' + str(payload) +
                    '. Скачайте пакет заново или запустите установщик с --update.'
                ) from error
    destination = home / 'Library/Application Support/SabyOfflineLogger'
    resources = destination / 'resources'
    resources.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = resources / name
        if name in ('UI-console-keys', 'UI-console-ignore') and target.exists():
            continue
        original = source / 'resources' / name
        if original.resolve() != target.resolve():
            shutil.copy2(original, target)
    installed_installer = destination / installer.name
    if installer.resolve() != installed_installer.resolve():
        shutil.copy2(installer, installed_installer)
    installed_installer.chmod(0o755)
    update = destination / 'Обновить анализатор.command'
    update.write_text('#!/bin/bash\nexec ' + shlex.join([str(installed_installer), '--update']) + '\n', encoding='utf-8')
    update.chmod(0o755)
    workflow = home / 'Library/Services' / (TITLE + '.workflow')
    contents = workflow / 'Contents'
    contents.mkdir(parents=True, exist_ok=True)
    document, info = workflow_documents(python, resources / 'run_macos.py')
    for name, data in (('document.wflow', document), ('Info.plist', info)):
        with (contents / name).open('wb') as stream:
            plistlib.dump(data, stream, sort_keys=False)
    return destination, workflow


def main():
    if sys.platform != 'darwin':
        raise RuntimeError('Установщик предназначен для macOS.')
    if sys.version_info < (3, 9):
        raise RuntimeError('Нужен Python 3.9+: https://www.python.org/downloads/macos/')
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    destination, workflow = install(args.source, Path.home(), Path(sys.executable))
    refresh = Path('/System/Library/CoreServices/pbs')
    if refresh.is_file():
        subprocess.run([str(refresh), '-update'], check=False)
    print(f'Установлено: {destination}\nБыстрое действие Finder: {workflow}')
    print('Выберите папку логов, ZIP или 7z → Быстрые действия / Службы → ' + TITLE)
    print('Отчеты сохраняются в Загрузки. Повторное обновление: Обновить анализатор.command в папке установки.')
    print('Если пункта нет, включите его в настройках быстрых действий/служб macOS или перезапустите Finder вручную.')
    print('Для 7z нужен 7zz/7z: https://formulae.brew.sh/formula/sevenzip (brew install sevenzip).')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
