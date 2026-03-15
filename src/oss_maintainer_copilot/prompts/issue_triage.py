from __future__ import annotations

from oss_maintainer_copilot.schemas.github import GitHubIssue

ISSUE_TRIAGE_SYSTEM_PROMPT = """
You are OSS Maintainer Copilot. Classify GitHub issues for maintainers using structured outputs.
Always explain difficulty, scope, risk, and context with explicit evidence.
Only mark an issue as a good first issue when it is narrowly scoped, low-risk, and low-context.
""".strip()


def build_issue_triage_user_prompt(issue: GitHubIssue) -> str:
    return f"""
Triage the following issue.

Title: {issue.title}

Body:
{issue.body or "(empty)"}
""".strip()

