from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_maintainer_copilot.agents.issue_triage import IssueTriageAgent, build_triage_labels
from oss_maintainer_copilot.schemas.common import DifficultyLevel, IssueCategory
from oss_maintainer_copilot.schemas.triage import IssueTriageInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def _load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("fixture_name", "category", "difficulty", "good_first_issue", "missing_context"),
    [
        (
            "issues/triage/bug_login_redirect_loop.json",
            IssueCategory.BUG,
            DifficultyLevel.INTERMEDIATE,
            False,
            [],
        ),
        (
            "issues/triage/bug_report_missing_repro.json",
            IssueCategory.BUG,
            DifficultyLevel.INTERMEDIATE,
            False,
            ["problem_statement", "reproduction_steps", "expected_behavior"],
        ),
        (
            "issues/triage/docs_windows_setup.json",
            IssueCategory.DOCS,
            DifficultyLevel.BEGINNER,
            True,
            [],
        ),
        (
            "issues/triage/docs_broken_link.json",
            IssueCategory.DOCS,
            DifficultyLevel.BEGINNER,
            True,
            [],
        ),
        (
            "issues/triage/feature_add_label_filter.json",
            IssueCategory.FEATURE_REQUEST,
            DifficultyLevel.INTERMEDIATE,
            False,
            [],
        ),
        (
            "issues/triage/feature_cross_surface_dashboard.json",
            IssueCategory.FEATURE_REQUEST,
            DifficultyLevel.MAINTAINER_ONLY,
            False,
            ["acceptance_criteria", "user_need"],
        ),
        (
            "issues/triage/refactor_extract_parser.json",
            IssueCategory.REFACTOR,
            DifficultyLevel.INTERMEDIATE,
            False,
            [],
        ),
        (
            "issues/triage/refactor_cleanup_unknown_target.json",
            IssueCategory.REFACTOR,
            DifficultyLevel.INTERMEDIATE,
            False,
            ["problem_statement", "acceptance_criteria", "target_area"],
        ),
        (
            "issues/triage/ambiguous_short_request.json",
            IssueCategory.AMBIGUOUS,
            DifficultyLevel.ADVANCED,
            False,
            ["problem_statement", "acceptance_criteria", "target_area", "motivation"],
        ),
        (
            "issues/triage/ambiguous_open_question.json",
            IssueCategory.AMBIGUOUS,
            DifficultyLevel.ADVANCED,
            False,
            ["problem_statement", "acceptance_criteria", "target_area", "motivation"],
        ),
    ],
)
def test_triage_issue_cases(
    fixture_root: Path,
    fixture_name: str,
    category: IssueCategory,
    difficulty: DifficultyLevel,
    good_first_issue: bool,
    missing_context: list[str],
) -> None:
    triage_input = IssueTriageInput.model_validate(_load_json_fixture(_fixture(fixture_root, fixture_name)))
    result = IssueTriageAgent().triage(triage_input)

    assert result.category is category
    assert result.difficulty is difficulty
    assert result.good_first_issue is good_first_issue
    assert result.missing_context == missing_context
    assert 0.0 <= result.confidence <= 0.99
    assert len(result.reasoning) == 3
    assert [item.category for item in result.reasoning] == [
        "category",
        "difficulty",
        "good_first_issue",
    ]


def test_build_triage_labels_for_good_first_issue(fixture_root: Path) -> None:
    triage_input = IssueTriageInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "issues/triage/docs_windows_setup.json"))
    )
    result = IssueTriageAgent().triage(triage_input)

    assert build_triage_labels(result) == [
        "triage:category:docs",
        "difficulty:beginner",
        "triage:good-first-issue",
    ]
