from __future__ import annotations

from pathlib import Path

from oss_maintainer_copilot.agents.onboarding_map import OnboardingMapAgent
from oss_maintainer_copilot.schemas.repo_intel import RepositoryIntelligenceInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def test_onboarding_map_builds_tracks_reading_order_and_starter_tasks(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_python_toolkit.json").read_text(encoding="utf-8")
    )

    result = OnboardingMapAgent().build(repo_input)

    assert ".github/workflows/" in result.first_session_goal
    assert any(step.title == "Orient On The Repository" for step in result.reading_order)
    assert any(
        step.title == "Inspect The Automation Entry Points"
        for step in result.reading_order
    )
    assert any(
        track.name == "Workflow Output Stewardship"
        for track in result.contributor_tracks
    )
    assert any(
        track.name == "Automation And Maintainer Operations"
        for track in result.contributor_tracks
    )
    assert any(task.title == "Refresh An Example Flow" for task in result.starter_tasks)
    assert any("maintainer" in note.casefold() for note in result.escalation_notes)
    assert result.confidence >= 0.85


def test_onboarding_map_adapts_to_docs_forward_repositories(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_docs_handbook.json").read_text(encoding="utf-8")
    )

    result = OnboardingMapAgent().build(repo_input)

    assert "README.md into docs, examples, and tests" in result.first_session_goal
    assert any(
        step.title == "Review The Contributor Docs Path"
        for step in result.reading_order
    )
    assert any(
        track.name == "Docs And Onboarding Clarity"
        for track in result.contributor_tracks
    )
    assert any(
        task.title == "Clarify A Contributor Path"
        for task in result.starter_tasks
    )
    assert any("onboarding-doc" in note for note in result.escalation_notes)


def test_onboarding_map_adapts_to_code_first_repositories(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_small_library.json").read_text(encoding="utf-8")
    )

    result = OnboardingMapAgent().build(repo_input)

    assert "from tests into the implementation" in result.first_session_goal
    assert any(step.title == "Trace The Core Implementation" for step in result.reading_order)
    assert any(
        track.name == "Heuristics And Schemas"
        for track in result.contributor_tracks
    )
    assert all(
        track.name != "Automation And Maintainer Operations"
        for track in result.contributor_tracks
    )


def test_onboarding_map_provides_safe_fallbacks_for_sparse_repositories() -> None:
    repo_input = RepositoryIntelligenceInput(
        repository_name="tiny-maintainer-tool",
        description="Small maintainer helper.",
        readme_text="python -m venv .venv",
    )

    result = OnboardingMapAgent().build(repo_input)

    assert any(
        track.name == "General Repository Familiarization"
        for track in result.contributor_tracks
    )
    assert any(task.title == "Clarify One Onboarding Step" for task in result.starter_tasks)
    assert any(step.title == "Orient On The Repository" for step in result.reading_order)
