#!/usr/bin/env python
"""CLI wrapper to execute the evaluation suite and print results."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation import GatewayEvaluationSuite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run gateway evaluation scenarios")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format for results",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    suite = GatewayEvaluationSuite()
    results = suite.run()
    summary = suite.summarize(results)

    if args.format == "markdown":
        print(suite.render_markdown_table(results))
        print()
        print(f"Pass rate: {summary.passed}/{summary.total} ({summary.pass_rate:.0%})")
    else:
        payload: dict[str, Any] = {
            "summary": asdict(summary),
            "results": [result.model_dump() for result in results],
        }
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
