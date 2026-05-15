```python
"""
ledger_cli.py

A simple interactive command‑line interface for inspecting the ledger.
"""

import argparse
from datetime import datetime
from typing import List, Dict, Any

from ledger_manager import load_ledger
from engine import get_ledger_statistics, get_previous_hash  # type: ignore[import-untyped]


def print_latest_block(block: Dict[str, Any]) -> None:
    """Pretty‑print the latest block in the ledger."""
    print("\n--- Latest Block ---")
    for key, value in block.items():
        print(f"{key:<10}: {value}")
    print("---------------------\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ledger inspection tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--latest",
        action="store_true",
        help="Print the most recent block in the ledger",
    )
    group.add_argument(
        "--stats",
        action="store_true",
        help="Show simple statistics about the ledger",
    )

    args = parser.parse_args()

    ledger: List[Dict[str, Any]] = load_ledger()

    if args.latest:
        if not ledger:
            print("🏧 Ledger is empty.")
            return
        print_latest_block(ledger[0])

    if args.stats:
        stats = get_ledger_statistics(ledger)
        print("\n--- Ledger Stats ---")
        print(f"Total blocks: {stats.get('total_blocks', 0)}")
        latest_ts = stats.get("latest_timestamp")
        if latest_ts:
            ts = datetime.fromisoformat(latest_ts)
            print(f"Latest block timestamp: {ts.isoformat()}")
        print("---------------------\n")


if __name__ == "__main__":
    main()
```