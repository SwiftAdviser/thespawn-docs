#!/usr/bin/env python3
"""Run Claude Blog analysis across every Mintlify MDX page.

The upstream analyzer batch mode scans only root markdown-like files in this
docs repo, so this wrapper walks recursively and normalizes the current JSON
schema into one release report.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ANALYZER = Path("/Users/krutovoy/.claude/scripts/analyze_blog.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--table", type=Path, default=None)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Path to exclude, relative to --root. Can be passed more than once.",
    )
    parser.add_argument(
        "--strict-blog",
        action="store_true",
        help="Exit non-zero unless every page reaches Claude Blog's publishable >=90 threshold.",
    )
    return parser.parse_args()


def run_analyzer(path: Path, timeout: int) -> dict:
    try:
        result = subprocess.run(
            ["python3", str(ANALYZER), str(path), "--format", "json"],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "file": str(path),
            "score": None,
            "rating": "TIMEOUT",
            "top_issue": f"analyze_blog.py timed out after {timeout}s",
        }

    if result.returncode != 0:
        return {
            "file": str(path),
            "score": None,
            "rating": "ERROR",
            "top_issue": result.stderr.strip() or "analyze_blog.py returned non-zero",
        }

    data = json.loads(result.stdout)
    score = data.get("score", {})
    categories = score.get("categories", {})
    issues = score.get("issues") or []
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues = sorted(issues, key=lambda item: severity_order.get(item.get("severity", "low"), 9))
    top_issue = ""
    if issues:
        top = issues[0]
        top_issue = f"{top.get('severity')}: {top.get('issue')}"

    return {
        "file": data.get("file", str(path)),
        "score": score.get("total"),
        "rating": score.get("rating"),
        "word_count": data.get("paragraphs", {}).get("total_word_count"),
        "content": categories.get("content_quality"),
        "seo": categories.get("seo_optimization"),
        "eeat": categories.get("eeat_signals"),
        "technical": categories.get("technical_elements"),
        "ai_citation": categories.get("ai_citation_readiness"),
        "issue_count": len(issues),
        "high_or_critical": sum(
            1 for issue in issues if issue.get("severity") in {"critical", "high"}
        ),
        "ai_phrase_count": data.get("ai_signals", {}).get("ai_phrase_count"),
        "likely_ai": data.get("ai_signals", {}).get("likely_ai"),
        "burstiness": data.get("ai_signals", {}).get("burstiness"),
        "ttr": data.get("ai_signals", {}).get("vocabulary_diversity_ttr"),
        "top_issue": top_issue,
    }


def build_table(rows: list[dict]) -> str:
    lines = [
        "| Page | Score | Rating | C | SEO | EEAT | Tech | AI cite | Top issue |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        issue = (row.get("top_issue") or "").replace("|", "/").replace("\n", " ")
        if len(issue) > 96:
            issue = issue[:93] + "..."
        lines.append(
            f"| `{row['file']}` | {row['score']} | {row['rating']} | "
            f"{row['content']} | {row['seo']} | {row['eeat']} | "
            f"{row['technical']} | {row['ai_citation']} | {issue} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    excluded = {str(Path(item)) for item in args.exclude}
    files = [
        path
        for path in sorted(args.root.glob("**/*.mdx"))
        if str(path.relative_to(args.root)) not in excluded
    ]
    rows = [run_analyzer(path, args.timeout) for path in files]
    rows = sorted(rows, key=lambda row: (row.get("score") is None, row.get("score") or 999, row["file"]))
    scored = [row for row in rows if row.get("score") is not None]
    ratings: dict[str, int] = {}
    for row in rows:
        ratings[row.get("rating", "ERROR")] = ratings.get(row.get("rating", "ERROR"), 0) + 1

    summary = {
        "tool": str(ANALYZER),
        "command_shape": "python3 /Users/krutovoy/.claude/scripts/analyze_blog.py <file> --format json",
        "file_count": len(rows),
        "scored_count": len(scored),
        "min_score": min((row["score"] for row in scored), default=None),
        "max_score": max((row["score"] for row in scored), default=None),
        "average_score": round(sum(row["score"] for row in scored) / len(scored), 1) if scored else None,
        "ratings": ratings,
        "rows": rows,
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, indent=2) + "\n")
    if args.table:
        args.table.parent.mkdir(parents=True, exist_ok=True)
        args.table.write_text(build_table(rows))

    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=2))

    if args.strict_blog and any((row.get("score") or 0) < 90 for row in rows):
        return 1
    if any(row.get("rating") in {"ERROR", "TIMEOUT"} for row in rows):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
