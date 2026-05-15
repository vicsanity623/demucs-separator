# HUMAN DIRECTIVES (CRITICAL)
1. This repository uses extremely strict CI checks via `check.sh`.
2. BEFORE you finalize any code changes, you MUST ensure they pass Ruff formatting and Mypy strict typing.
3. If you add new third-party imports that cause Mypy `[no-any-unimported]` errors, you MUST append `# type: ignore[import-untyped]` to the import line.
4. Run `./check.sh` locally in your sandbox to verify your changes before committing.
