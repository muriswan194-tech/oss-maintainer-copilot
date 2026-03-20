from __future__ import annotations

from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"


def _skill_text(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def test_skills_readme_lists_available_workflows() -> None:
    readme = (SKILLS_ROOT / "README.md").read_text(encoding="utf-8")

    assert "triage-issue" in readme
    assert "prepare-pr-review" in readme
    assert "draft-release-notes" in readme
    assert "onboard-contributor" in readme


def test_triage_skill_contract() -> None:
    skill = _skill_text("triage-issue")

    assert "## Required Inputs" in skill
    assert "## Output Contract" in skill
    assert "omc triage-issue" in skill
    assert "good_first_issue" in skill


def test_pr_review_skill_contract() -> None:
    skill = _skill_text("prepare-pr-review")

    assert "## Required Inputs" in skill
    assert "## Output Contract" in skill
    assert "omc summarize-pr" in skill
    assert "changed_areas" in skill
    assert "input_warnings" in skill


def test_release_skill_contract() -> None:
    skill = _skill_text("draft-release-notes")

    assert "## Required Inputs" in skill
    assert "## Output Contract" in skill
    assert "omc generate-release-notes" in skill
    assert "data_quality_notes" in skill


def test_onboarding_skill_contract() -> None:
    skill = _skill_text("onboard-contributor")

    assert "## Required Inputs" in skill
    assert "## Output Contract" in skill
    assert "omc onboarding-map" in skill
    assert "starter_tasks" in skill
