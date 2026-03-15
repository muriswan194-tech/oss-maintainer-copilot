from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.agents.good_first_issue import GoodFirstIssueAgent
from oss_maintainer_copilot.agents.issue_triage import IssueTriageAgent
from oss_maintainer_copilot.schemas.triage import IssueTriageInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def _load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_good_first_issue_accepts_beginner_docs_issue(fixture_root: Path) -> None:
    issue = IssueTriageInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "issues/triage/docs_windows_setup.json"))
    )
    triage = IssueTriageAgent().triage(issue)
    result = GoodFirstIssueAgent().classify(issue, triage)

    assert result.eligible is True
    assert "difficulty:beginner" in result.matched_signals
    assert "well-specified" in result.matched_signals
    assert result.blocked_by == []


def test_good_first_issue_rejects_ambiguous_issue(fixture_root: Path) -> None:
    issue = IssueTriageInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "issues/triage/ambiguous_short_request.json"))
    )
    triage = IssueTriageAgent().triage(issue)
    result = GoodFirstIssueAgent().classify(issue, triage)

    assert result.eligible is False
    assert any(item.startswith("missing:") for item in result.blocked_by)
    assert "triage-not-approved" in result.blocked_by
