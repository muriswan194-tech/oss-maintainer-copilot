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
    assert result.repository_shape == "automation-heavy maintainer workspace"
    assert "automation-heavy maintainer workspace" in result.maintainer_summary
    assert "issue triage" in result.maintainer_workflows
    assert "PR review preparation" in result.maintainer_workflows
    assert "release drafting" in result.maintainer_workflows
    assert "python -m venv .venv" in result.local_setup_steps
    assert "ruff check ." in result.local_setup_steps
    assert any(area.path == "src/" for area in result.major_areas)
    assert "README.md" in result.key_entry_paths
    assert ".github/workflows/" in result.workflow_surfaces
    assert "docs/" in result.docs_surfaces
    assert any(item.startswith("Start with README.md") for item in result.good_starting_points)
    assert result.confidence >= 0.8


def test_repo_intel_infers_docs_forward_shape(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_docs_handbook.json").read_text(encoding="utf-8")
    )

    result = RepositoryIntelligenceAgent().analyze(repo_input)

    assert result.repository_shape == "docs-forward maintainer toolkit"
    assert result.key_entry_paths[:3] == ["README.md", "CONTRIBUTING.md", "docs/"]
    assert "docs/" in result.docs_surfaces
    assert ".github/workflows/" in result.workflow_surfaces
    assert any("docs/" in item for item in result.good_starting_points)


def test_repo_intel_infers_code_first_shape(fixture_root: Path) -> None:
    repo_input = RepositoryIntelligenceInput.model_validate_json(
        _fixture(fixture_root, "repos/repo_intel_small_library.json").read_text(encoding="utf-8")
    )

    result = RepositoryIntelligenceAgent().analyze(repo_input)

    assert result.repository_shape == "code-first contributor toolkit"
    assert result.key_entry_paths[:3] == ["README.md", "CONTRIBUTING.md", "src/"]
    assert result.workflow_surfaces == ["tests/", "src/"]
    assert "README.md" in result.docs_surfaces
