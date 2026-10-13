# Repository workflow

This repository contains only the offline log analyzer and its launchers/installers.
Do not commit installed applications, real logs, HAR files, generated reports, research
documents, or archives. The root .gitignore deliberately uses an allowlist.

The user has requested that ongoing analyzer changes be maintained on
https://github.com/nafisgizatov-collab/offline_logger.git.
After implementing and verifying requested analyzer changes, commit and push them
to origin, unless the user asks otherwise. Never force-push or overwrite remote work.

The Python payload after #__PYTHON_PAYLOAD__ in SabyLogReport.cmd must match
build_background_report.py. The payload in ReportBackrgoudProcees.cmd must match
build_nine_methods_report.py. Preserve launcher headers when synchronizing payloads.
Use UTF-8 with BOM for PowerShell scripts containing Russian text so Windows
PowerShell 5.1 reads them correctly; CMD launchers use CRLF.

Project layout: root launchers are installSabyLogContextMenu-Windows.cmd (Windows) and installSabyLogContextMenu-macOS.command (macOS). All analyzer code, sidecar files, tests and supporting installers live under resources/. Maintain hybrid payloads there. Do not add compatibility wrappers from the parent workspace to Git. resources/local is local-only scratch space. macOS .command files use LF and executable mode.
