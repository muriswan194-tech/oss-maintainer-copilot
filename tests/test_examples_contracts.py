from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.schemas.onboarding import OnboardingMapResult
from oss_maintainer_copilot.schemas.pull_request import PullRequestSummaryResult
from oss_maintainer_copilot.schemas.release_notes import ReleaseNotesResult
from oss_maintainer_copilot.schemas.repo_intel import RepositoryIntelligenceResult
from oss_maintainer_copilot.schemas.triage import IssueTriageResult

EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_issue_triage_example_matches_schema_and_comment_marker() -> None:
    payload = _load_json(EXAMPLES_ROOT / "issue-triage" / "output.json")
    markdown = (EXAMPLES_ROOT / "issue-triage" / "output.md").read_text(
        encoding="utf-8"
    )

    core_payload = {
        key: value for key, value in payload.items() if key != "recommended_labels"
    }

    IssueTriageResult.model_validate(core_payload)

    assert payload["recommended_labels"]
    assert "<!-- oss-maintainer-copilot:issue-triage -->" in markdown


def test_pr_brief_example_matches_schema_and_comment_marker() -> None:
    payload = _load_json(EXAMPLES_ROOT / "pr-brief" / "output.json")
    markdown = (EXAMPLES_ROOT / "pr-brief" / "output.md").read_text(
        encoding="utf-8"
    )

    PullRequestSummaryResult.model_validate(payload)

    assert payload["changed_areas"]
    assert "<!-- oss-maintainer-copilot:pr-summary -->" in markdown


def test_release_draft_example_matches_schema_and_sections() -> None:
    payload = _load_json(EXAMPLES_ROOT / "release-draft" / "output.json")
    markdown = (EXAMPLES_ROOT / "release-draft" / "output.md").read_text(
        encoding="utf-8"
    )

    ReleaseNotesResult.model_validate(payload)

    assert "## Highlights" in markdown
    assert "## Breaking Changes" in markdown


def test_repo_intel_example_matches_schema_and_comment_marker() -> None:
    payload = _load_json(EXAMPLES_ROOT / "repo-intel" / "output.json")
    markdown = (EXAMPLES_ROOT / "repo-intel" / "output.md").read_text(
        encoding="utf-8"
    )

    RepositoryIntelligenceResult.model_validate(payload)

    assert payload["maintainer_workflows"]
    assert "<!-- oss-maintainer-copilot:repo-intel -->" in markdown


def test_onboarding_map_example_matches_schema_and_comment_marker() -> None:
    payload = _load_json(EXAMPLES_ROOT / "onboarding-map" / "output.json")
    markdown = (EXAMPLES_ROOT / "onboarding-map" / "output.md").read_text(
        encoding="utf-8"
    )

    OnboardingMapResult.model_validate(payload)

    assert payload["starter_tasks"]
    assert "<!-- oss-maintainer-copilot:onboarding-map -->" in markdown
