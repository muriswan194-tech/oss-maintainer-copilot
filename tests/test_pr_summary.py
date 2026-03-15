from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.agents.pr_summary import PullRequestSummarizer
from oss_maintainer_copilot.schemas.common import RiskLevel
from oss_maintainer_copilot.schemas.pull_request import PullRequestSummaryInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def _load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_summarize_docs_only_pull_request(fixture_root: Path) -> None:
    pull_request = PullRequestSummaryInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "pulls/docs_only_pr.json"))
    )
    result = PullRequestSummarizer().summarize(pull_request)

    assert result.short_summary.startswith("Documentation-only change:")
    assert "does not appear to change runtime behavior" in result.technical_summary
    assert result.risk_assessment.level is RiskLevel.LOW
    assert "documentation-only" in result.risk_assessment.summary.casefold()
    assert result.release_note_snippet.startswith("Docs:")
    assert any("documentation instructions" in item.casefold() for item in result.reviewer_checklist)


def test_summarize_risky_code_change_pull_request(fixture_root: Path) -> None:
    pull_request = PullRequestSummaryInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "pulls/risky_code_change_pr.json"))
    )
    result = PullRequestSummarizer().summarize(pull_request)

    assert "automation" in result.short_summary or "application code" in result.short_summary
    assert "runtime behavior or automation" in result.technical_summary
    assert result.risk_assessment.level is RiskLevel.HIGH
    assert "risky-file-paths" in result.risk_assessment.flags
    assert any("sensitive code paths or workflows" in item.casefold() for item in result.reviewer_checklist)
    assert result.release_note_snippet.startswith("Updated:")


def test_summarize_breaking_change_pull_request(fixture_root: Path) -> None:
    pull_request = PullRequestSummaryInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "pulls/breaking_change_pr.json"))
    )
    result = PullRequestSummarizer().summarize(pull_request)

    assert result.short_summary.startswith("Breaking change:")
    assert "migration" in result.technical_summary.casefold()
    assert result.risk_assessment.level is RiskLevel.HIGH
    assert "breaking-change-language" in result.risk_assessment.flags
    assert any("migration guidance" in item.casefold() for item in result.reviewer_checklist)
    assert result.release_note_snippet.startswith("Breaking:")
