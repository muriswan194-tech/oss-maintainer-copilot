from __future__ import annotations

from pathlib import Path

from oss_maintainer_copilot.agents.repo_intel import RepositoryIntelligenceAgent
from oss_maintainer_copilot.schemas.repo_intel import RepositoryIntelligenceInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def test_repo_intel_builds_summary_and_setup_steps(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_python_toolkit.json").read_text(encoding="utf-8")
    )

    result = RepositoryIntelligenceAgent().analyze(repo_input)

    assert result.repository_summary.startswith("oss-maintainer-copilot is a Python repository")
    assert "issue triage" in result.maintainer_workflows
    assert "PR review preparation" in result.maintainer_workflows
    assert "release drafting" in result.maintainer_workflows
    assert "python -m venv .venv" in result.local_setup_steps
    assert "ruff check ." in result.local_setup_steps
    assert any(area.path == "src/" for area in result.major_areas)
    assert any(item.startswith("Start with examples/") for item in result.good_starting_points)
    assert result.confidence >= 0.8
