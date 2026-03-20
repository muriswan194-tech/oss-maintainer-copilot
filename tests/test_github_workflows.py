from __future__ import annotations

from pathlib import Path

WORKFLOWS_ROOT = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def _workflow_text(name: str) -> str:
    return (WORKFLOWS_ROOT / name).read_text(encoding="utf-8")


def test_issue_triage_workflow_contract() -> None:
    workflow = _workflow_text("issue-triage.yml")

    assert "issues:" in workflow
    assert "issues: write" in workflow
    assert "python -m oss_maintainer_copilot.cli triage-issue" in workflow
    assert "triage.json" in workflow
    assert "triage.md" in workflow
    assert "<!-- oss-maintainer-copilot:issue-triage -->" in workflow


def test_pr_summary_workflow_contract() -> None:
    workflow = _workflow_text("pr-summary.yml")

    assert "pull_request:" in workflow
    assert "pull-requests: write" in workflow
    assert "changed_file_paths" in workflow
    assert "commit_messages" in workflow
    assert "python -m oss_maintainer_copilot.cli summarize-pr" in workflow
    assert "pr-summary.json" in workflow
    assert "pr-summary.md" in workflow
    assert "<!-- oss-maintainer-copilot:pr-summary -->" in workflow


def test_release_notes_workflow_contract() -> None:
    workflow = _workflow_text("release-notes.yml")

    assert "workflow_dispatch:" in workflow
    assert "previous_version:" in workflow
    assert "current_version:" in workflow
    assert "target_commitish:" in workflow
    assert "TARGET_COMMITISH" in workflow
    assert "compareTarget" in workflow
    assert "basehead: `${previousVersion}...${compareTarget}`" in workflow
    assert "compare.data.total_commits > compare.data.commits.length" in workflow
    assert "number: pr.number" in workflow
    assert "body: pr.body || \"\"" in workflow
    assert "python -m oss_maintainer_copilot.cli generate-release-notes" in workflow
    assert "getReleaseByTag" in workflow
    assert "updateRelease" in workflow
    assert "createRelease" in workflow
