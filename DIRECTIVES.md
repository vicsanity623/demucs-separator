# HUMAN DIRECTIVES (CRITICAL)
1. This repository uses extremely strict CI checks via `check.sh`.
2. BEFORE you finalize any code changes, you MUST ensure they pass Ruff formatting and Mypy strict typing.
3. If you add new third-party imports that cause Mypy `[no-any-unimported]` errors, you MUST append `# type: ignore[import-untyped]` to the import line.
4. Run `./check.sh` locally in your sandbox to verify your changes before committing.

# ARCHITECTURAL DIRECTIVES: LEDGER DATABASE MIGRATION
5. **CRITICAL BOTTLENECK FIX:** The current flat-file/JSON storage for the Axiom Ledger is deprecated due to scaling and memory constraints. You are tasked with migrating the ledger storage to a high-speed, embedded database capable of handling Node/Edge logic (Atomic Facts and their relationships).
6. **CI/CD COMPATIBILITY (GITHUB ACTIONS):** The new database MUST be "serverless" and embedded directly within the Python environment so it runs natively inside GitHub Actions without requiring background services or Docker daemons. 
    * *Approved Targets:* `sqlite3` (using strict Node and Edge relational tables), `NetworkX` (with fast chunked Parquet/Pickle serialization), or embedded graph/vector databases like `Kuzu` or `ChromaDB`.
7. **IMPLEMENTATION STEPS:**
    * Update ledger I/O functions to read/write to the new embedded database file (e.g., `ledger.db`).
    * Ensure the DB file is correctly added to `.gitignore` to prevent bloating the repo, but ensure the CI scripts (`.github/workflows/`) are updated to cache or persist the database artifact between runs if necessary.
    * Update `requirements.txt` with any new dependencies.
    * Add strict Mypy types to all new database transaction functions.
