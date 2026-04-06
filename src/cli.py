from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from src.build_dcg_facts import build_dcg_facts
from src.query_interface import run_query


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--root", required=True)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--root", required=True)
    query_parser.add_argument("--type", required=True)
    query_parser.add_argument("--file-path")
    query_parser.add_argument("--symbol-id")
    query_parser.add_argument("--symbol-name")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except argparse.ArgumentError as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 1

    try:
        if args.command == "build":
            result = build_dcg_facts(Path(args.root))
        else:
            query_kwargs = {
                key.replace("_", "-"): value
                for key, value in vars(args).items()
                if key not in {"command", "root", "type"} and value is not None
            }
            result = run_query(
                Path(args.root),
                args.type,
                **{
                    key.replace("-", "_"): Path(value)
                    if key == "file-path"
                    else value
                    for key, value in query_kwargs.items()
                },
            )
    except (KeyError, ValueError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
