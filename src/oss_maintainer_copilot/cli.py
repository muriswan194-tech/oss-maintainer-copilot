from __future__ import annotations

import argparse
import json
from pathlib import Path

from oss_maintainer_copilot.agents.issue_triage import (
    IssueTriageAgent,
    build_triage_labels,
    render_triage_markdown,
)
from oss_maintainer_copilot.agents.pr_summary import PullRequestSummarizer, render_pr_summary_markdown
from oss_maintainer_copilot.agents.repo_intel import (
    RepositoryIntelligenceAgent,
    render_repo_intel_markdown,
)
from oss_maintainer_copilot.agents.release_notes import ReleaseNotesGenerator
from oss_maintainer_copilot.github.events import (
    load_issue_envelope,
    load_pull_request_summary_input,
    load_repo_intel_input,
    load_release_notes_input,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OSS Maintainer Copilot CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage_parser = subparsers.add_parser("triage-issue", help="Triage a GitHub issue payload")
    triage_parser.add_argument("--input", required=True, type=Path, help="Path to JSON payload")
    triage_parser.add_argument("--output", type=Path, help="Optional output JSON path")
    triage_parser.add_argument("--markdown", type=Path, help="Optional markdown output path")

    pr_parser = subparsers.add_parser("summarize-pr", help="Summarize a pull request payload")
    pr_parser.add_argument("--input", required=True, type=Path, help="Path to JSON payload")
    pr_parser.add_argument("--output", type=Path, help="Optional output JSON path")
    pr_parser.add_argument("--markdown", type=Path, help="Optional markdown output path")

    release_parser = subparsers.add_parser("generate-release-notes", help="Generate release notes from merged PR metadata")
    release_parser.add_argument("--input", required=True, type=Path, help="Path to JSON payload")
    release_parser.add_argument("--output", type=Path, help="Optional output JSON path")
    release_parser.add_argument("--markdown", type=Path, help="Optional markdown output path")

    repo_intel_parser = subparsers.add_parser("repo-intel", help="Generate repository intelligence from a normalized repo payload")
    repo_intel_parser.add_argument("--input", required=True, type=Path, help="Path to JSON payload")
    repo_intel_parser.add_argument("--output", type=Path, help="Optional output JSON path")
    repo_intel_parser.add_argument("--markdown", type=Path, help="Optional markdown output path")

    return parser


def _write_outputs(payload: dict, output_path: Path | None) -> None:
    json_output = json.dumps(payload, indent=2)
    if output_path is not None:
        output_path.write_text(json_output + "\n", encoding="utf-8")
    else:
        print(json_output)


def run_triage_issue(input_path: Path, output_path: Path | None, markdown_path: Path | None) -> int:
    envelope = load_issue_envelope(input_path)
    triage_input = IssueTriageAgent.from_github_issue(envelope.issue, envelope.repository)
    triage_result = IssueTriageAgent().triage(triage_input)
    payload = triage_result.model_dump(mode="json")
    payload["recommended_labels"] = build_triage_labels(triage_result)
    _write_outputs(payload, output_path)

    if markdown_path is not None:
        markdown = render_triage_markdown(triage_input, triage_result)
        markdown_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


def run_summarize_pr(input_path: Path, output_path: Path | None, markdown_path: Path | None) -> int:
    pull_request = load_pull_request_summary_input(input_path)
    summary = PullRequestSummarizer().summarize(pull_request)
    _write_outputs(summary.model_dump(mode="json"), output_path)

    if markdown_path is not None:
        markdown = render_pr_summary_markdown(pull_request, summary)
        markdown_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


def run_generate_release_notes(input_path: Path, output_path: Path | None, markdown_path: Path | None) -> int:
    release_input = load_release_notes_input(input_path)
    generator = ReleaseNotesGenerator()
    release_notes = generator.generate(release_input)
    _write_outputs(release_notes.model_dump(mode="json"), output_path)

    if markdown_path is not None:
        markdown = generator.render_markdown(release_notes)
        markdown_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


def run_repo_intel(input_path: Path, output_path: Path | None, markdown_path: Path | None) -> int:
    repo_input = load_repo_intel_input(input_path)
    result = RepositoryIntelligenceAgent().analyze(repo_input)
    _write_outputs(result.model_dump(mode="json"), output_path)

    if markdown_path is not None:
        markdown = render_repo_intel_markdown(repo_input, result)
        markdown_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "triage-issue":
        return run_triage_issue(args.input, args.output, args.markdown)
    if args.command == "summarize-pr":
        return run_summarize_pr(args.input, args.output, args.markdown)
    if args.command == "generate-release-notes":
        return run_generate_release_notes(args.input, args.output, args.markdown)
    if args.command == "repo-intel":
        return run_repo_intel(args.input, args.output, args.markdown)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
