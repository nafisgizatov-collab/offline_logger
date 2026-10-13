#!/bin/bash
# Install locally from a checkout, or download the package when used standalone.
set -euo pipefail
finish() {
    status=$?
    if [[ -n "${stage:-}" && "$stage" == "${TMPDIR:-/tmp/}saby-logger."* ]]; then
        /bin/rm -rf -- "$stage"
    fi
    if [[ $status -ne 0 ]]; then printf '\nУстановка не завершена. Подробности выше.\n'; fi
    if [[ -t 0 ]]; then read -r -p 'Нажмите Enter, чтобы закрыть окно… ' unused || true; fi
}
stage=''
trap finish EXIT
if [[ "$(/usr/bin/uname -s)" != Darwin ]]; then
    printf 'Этот установщик предназначен для macOS.\n' >&2
    exit 1
fi
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
python=''
for candidate in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 || true)"; do
    [[ -x "$candidate" ]] || continue
    # Avoid triggering Apple's developer-tools installation stub.
    if [[ "$candidate" == /usr/bin/python3 ]] && ! /usr/bin/xcode-select -p >/dev/null 2>&1; then continue; fi
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' </dev/null >/dev/null 2>&1; then
        python="$candidate"
        break
    fi
done
if [[ -z "$python" ]]; then
    printf 'Не найден работающий Python 3.9 или новее.\nУстановите Python для macOS: https://www.python.org/downloads/macos/\nЗатем запустите установщик повторно.\n' >&2
    exit 1
fi
source_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ "${1:-}" == --update || ! -f "$source_dir/resources/install_macos.py" ]]; then
    printf 'Скачивание актуального анализатора с GitHub…\n'
    stage=$(/usr/bin/mktemp -d "${TMPDIR:-/tmp/}saby-logger.XXXXXX")
    /usr/bin/curl --fail --location --connect-timeout 20 --max-time 180 \
        'https://github.com/nafisgizatov-collab/offline_logger/archive/refs/heads/main.zip' -o "$stage/logger.zip"
    /usr/bin/ditto -x -k "$stage/logger.zip" "$stage/package"
    source_dir="$stage/package/offline_logger-main"
fi
"$python" "$source_dir/resources/install_macos.py" --source "$source_dir"
