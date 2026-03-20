from __future__ import annotations

from oss_maintainer_copilot.schemas.repo_intel import (
    RepositoryArea,
    RepositoryIntelligenceInput,
    RepositoryIntelligenceResult,
)

COMMAND_PREFIXES = (
    "python ",
    "python -m",
    ". ",
    "pip ",
    "pytest",
    "ruff ",
)

WORKFLOW_HINTS = {
    "issue triage": "issue triage",
    "good first issue": "good first issue classification",
    "pr review": "PR review preparation",
    "pull request": "PR review preparation",
    "release": "release drafting",
    "onboarding": "contributor onboarding",
    "repository intelligence": "repository intelligence",
    "repo intelligence": "repository intelligence",
}

AREA_HINTS = [
    (
        ".github/workflows/",
        "GitHub Actions entrypoints for issue, PR, release, and CI automation.",
        "Start here to understand how repository events are wired into maintainer workflows.",
    ),
    (
        "src/",
        "Core workflow logic, schemas, and CLI code for maintainer automation.",
        "Start here if you want to extend issue triage, PR briefs, release drafting, or repo intelligence.",
    ),
    (
        "tests/",
        "Fixture-driven regression coverage that keeps outputs stable and reviewable.",
        "Start here to learn expected behavior before changing schemas or workflow heuristics.",
    ),
    (
        "examples/",
        "Checked-in sample inputs and outputs that show how maintainers will experience the workflows.",
        "Start here if you want the fastest overview of what the project produces today.",
    ),
    (
        "docs/",
        "Supporting documentation and demo assets for contributors and evaluators.",
        "Start here when you need context, visuals, or project-facing documentation.",
    ),
]


class RepositoryIntelligenceAgent:
    """Builds a deterministic repository overview for contributor onboarding and maintainer context."""

    def analyze(self, repo: RepositoryIntelligenceInput) -> RepositoryIntelligenceResult:
        maintainer_workflows = self._infer_workflows(repo)
        local_setup_steps = self._extract_setup_steps(repo)
        major_areas = self._build_major_areas(repo.top_level_paths)
        good_starting_points = self._build_good_starting_points(major_areas)
        contributor_checklist = self._build_contributor_checklist(local_setup_steps)
        repository_summary = self._build_summary(repo, maintainer_workflows)
        confidence = self._calculate_confidence(repo, maintainer_workflows, local_setup_steps, major_areas)

        return RepositoryIntelligenceResult(
            repository_summary=repository_summary,
            maintainer_workflows=maintainer_workflows,
            local_setup_steps=local_setup_steps,
            major_areas=major_areas,
            good_starting_points=good_starting_points,
            contributor_checklist=contributor_checklist,
            confidence=confidence,
        )

    def _infer_workflows(self, repo: RepositoryIntelligenceInput) -> list[str]:
        text = " ".join([repo.description, repo.readme_text, repo.contributing_text]).casefold()
        workflows: list[str] = []
        for hint, workflow in WORKFLOW_HINTS.items():
            if hint in text and workflow not in workflows:
                workflows.append(workflow)
        if not workflows:
            workflows.append("repository maintenance")
        return workflows

    def _extract_setup_steps(self, repo: RepositoryIntelligenceInput) -> list[str]:
        combined_text = "\n".join([repo.readme_text, repo.contributing_text])
        setup_steps: list[str] = []

        for raw_line in combined_text.splitlines():
            line = raw_line.strip().strip("`")
            if not line or line.startswith("```"):
                continue
            if any(line.startswith(prefix) for prefix in COMMAND_PREFIXES):
                if line not in setup_steps:
                    setup_steps.append(line)

        return setup_steps[:8]

    def _build_major_areas(self, top_level_paths: list[str]) -> list[RepositoryArea]:
        major_areas: list[RepositoryArea] = []
        seen_paths: set[str] = set()

        for path in top_level_paths:
            normalized = path.replace("\\", "/")
            if normalized in seen_paths:
                continue
            seen_paths.add(normalized)

            purpose = "Repository metadata and project configuration."
            contributor_entrypoint = "Read this area when you need context about how the project is organized."

            for prefix, area_purpose, area_entrypoint in AREA_HINTS:
                if normalized.startswith(prefix):
                    purpose = area_purpose
                    contributor_entrypoint = area_entrypoint
                    break

            major_areas.append(
                RepositoryArea(
                    path=normalized,
                    purpose=purpose,
                    contributor_entrypoint=contributor_entrypoint,
                )
            )

        return major_areas[:6]

    def _build_good_starting_points(self, major_areas: list[RepositoryArea]) -> list[str]:
        starting_points: list[str] = []
        paths = {area.path for area in major_areas}

        if "examples/" in paths:
            starting_points.append("Start with examples/ to see the JSON and markdown outputs expected from each workflow.")
        if "tests/" in paths:
            starting_points.append("Read tests/ next to understand which public outputs are treated as stable.")
        if "src/" in paths:
            starting_points.append("Move into src/ once you know which workflow you want to extend or debug.")
        if ".github/workflows/" in paths:
            starting_points.append("Review .github/workflows/ when you want to understand how repository events trigger automation.")
        if not starting_points:
            starting_points.append("Start with the README and CONTRIBUTING guide, then inspect the top-level project files.")

        return starting_points

    def _build_contributor_checklist(self, local_setup_steps: list[str]) -> list[str]:
        checklist = [
            "Read README.md and CONTRIBUTING.md before changing workflow behavior.",
            "Pick a narrow workflow area or fixture before making broader refactors.",
        ]

        if local_setup_steps:
            checklist.append("Follow the documented local setup path before editing code or fixtures.")
        if any("pytest" in step for step in local_setup_steps):
            checklist.append("Run pytest after changing schemas, heuristics, or workflow outputs.")
        if any("ruff" in step for step in local_setup_steps):
            checklist.append("Run ruff check . before opening a pull request.")

        checklist.append("Update examples, fixtures, and docs when public outputs change.")
        return checklist

    def _build_summary(
        self,
        repo: RepositoryIntelligenceInput,
        maintainer_workflows: list[str],
    ) -> str:
        language = f"{repo.primary_language} " if repo.primary_language else ""
        workflow_text = ", ".join(maintainer_workflows[:3])

        if repo.description:
            return (
                f"{repo.repository_name} is a {language}repository focused on {workflow_text}. "
                f"{repo.description.strip()}"
            )

        return (
            f"{repo.repository_name} is a {language}repository focused on {workflow_text} "
            "with structured outputs for maintainers and contributors."
        )

    def _calculate_confidence(
        self,
        repo: RepositoryIntelligenceInput,
        maintainer_workflows: list[str],
        local_setup_steps: list[str],
        major_areas: list[RepositoryArea],
    ) -> float:
        confidence = 0.55
        confidence += 0.1 if repo.description else 0.0
        confidence += min(len(maintainer_workflows) * 0.05, 0.15)
        confidence += min(len(local_setup_steps) * 0.03, 0.12)
        confidence += min(len(major_areas) * 0.03, 0.12)
        return round(min(confidence, 0.95), 2)


def render_repo_intel_markdown(
    repo: RepositoryIntelligenceInput,
    result: RepositoryIntelligenceResult,
) -> str:
    workflow_lines = "\n".join(f"- `{workflow}`" for workflow in result.maintainer_workflows)
    setup_lines = "\n".join(f"- `{step}`" for step in result.local_setup_steps) or "- No setup steps detected."
    area_lines = "\n".join(
        f"- `{area.path}`: {area.purpose} Entry point: {area.contributor_entrypoint}"
        for area in result.major_areas
    )
    starting_point_lines = "\n".join(f"- {item}" for item in result.good_starting_points)
    contributor_checklist_lines = "\n".join(f"- {item}" for item in result.contributor_checklist)

    return f"""<!-- oss-maintainer-copilot:repo-intel -->
## OSS Maintainer Copilot Repository Intelligence

**Repository:** {repo.repository_name}

### Summary
{result.repository_summary}

### Maintainer Workflows
{workflow_lines}

### Local Setup Path
{setup_lines}

### Major Areas
{area_lines}

### Good Starting Points
{starting_point_lines}

### Contributor Checklist
{contributor_checklist_lines}
"""
