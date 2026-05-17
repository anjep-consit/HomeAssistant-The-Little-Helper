#!/usr/bin/env python3
"""Append The Little Helper history events and weekly reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path("/config/the_little_helper_history")
EVENTS = ROOT / "daily_completion.jsonl"
REPORTS = ROOT / "reports"


def ensure_dirs() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)


def log_event(category: str, status: str, value: str) -> None:
    ensure_dirs()
    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "date": datetime.now().date().isoformat(),
        "category": category,
        "status": status,
        "value": value,
    }
    with EVENTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def write_report(week: str, content: str) -> None:
    ensure_dirs()
    (REPORTS / f"uge-{week}.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    log_parser = subparsers.add_parser("log")
    log_parser.add_argument("--category", required=True)
    log_parser.add_argument("--status", required=True)
    log_parser.add_argument("--value", default="")
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--week", required=True)
    report_parser.add_argument("--content", required=True)
    args = parser.parse_args()
    if args.command == "log":
        log_event(args.category, args.status, args.value)
    elif args.command == "report":
        write_report(args.week, args.content)


if __name__ == "__main__":
    main()
