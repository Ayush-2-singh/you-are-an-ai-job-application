from __future__ import annotations

import argparse

from .agent import run_agent, write_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Job Application Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Rank jobs from a local JSON file")
    _add_common_args(run_parser)
    run_parser.add_argument("--jobs", required=True, help="Path to job listings JSON")

    search_parser = subparsers.add_parser("search", help="Live search through configured providers")
    _add_common_args(search_parser)
    search_parser.add_argument("--jobs", help="Optional local job listings JSON to include")

    args = parser.parse_args()
    recommendations = run_agent(
        config_path=args.config,
        resume_path=args.resume,
        jobs_path=getattr(args, "jobs", None),
        limit=args.limit,
        live_search=args.command == "search",
    )
    json_path, md_path = write_outputs(recommendations, args.output)
    print(f"Found {len(recommendations)} recommendations")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", required=True, help="Path to preferences JSON")
    parser.add_argument("--resume", required=True, help="Path to resume .docx")
    parser.add_argument("--limit", type=int, default=10, help="Maximum recommendations")
    parser.add_argument("--output", default="outputs", help="Output directory")


if __name__ == "__main__":
    main()

