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
    "uv ",
    "poetry ",
    "npm ",
    "pnpm ",
    "yarn ",
    "mkdocs ",
    "cargo ",
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
        (
            "Start here to understand how repository events are wired into "
            "maintainer workflows."
        ),
    ),
    (
        "src/",
        "Core workflow logic, schemas, and CLI code for maintainer automation.",
        (
            "Start here if you want to extend issue triage, PR briefs, "
            "release drafting, or repo intelligence."
        ),
    ),
    (
        "tests/",
        "Fixture-driven regression coverage that keeps outputs stable and reviewable.",
        (
            "Start here to learn expected behavior before changing schemas "
            "or workflow heuristics."
        ),
    ),
    (
        "examples/",
        (
            "Checked-in sample inputs and outputs that show how maintainers "
            "will experience the workflows."
        ),
        "Start here if you want the fastest overview of what the project produces today.",
    ),
    (
        "docs/",
        "Supporting documentation and demo assets for contributors and evaluators.",
        "Start here when you need context, visuals, or project-facing documentation.",
    ),
]

PATH_PRIORITIES = {
    "automation-heavy maintainer workspace": [
        "README.md",
        "CONTRIBUTING.md",
        ".github/workflows/",
        "examples/",
        "tests/",
        "src/",
        "docs/",
    ],
    "docs-forward maintainer toolkit": [
        "README.md",
        "CONTRIBUTING.md",
        "docs/",
        "examples/",
        "tests/",
        "src/",
        ".github/workflows/",
    ],
    "code-first contributor toolkit": [
        "README.md",
        "CONTRIBUTING.md",
        "src/",
        "tests/",
        "examples/",
        "docs/",
        ".github/workflows/",
    ],
    "balanced maintainer toolkit": [
        "README.md",
        "CONTRIBUTING.md",
        "examples/",
        "tests/",
        "src/",
        ".github/workflows/",
        "docs/",
    ],
}


class RepositoryIntelligenceAgent:
    """Build a deterministic repository overview for maintainer context."""

    def analyze(self, repo: RepositoryIntelligenceInput) -> RepositoryIntelligenceResult:
        maintainer_workflows = self._infer_workflows(repo)
        local_setup_steps = self._extract_setup_steps(repo)
        major_areas = self._build_major_areas(repo.top_level_paths)
        repository_shape = self._infer_repository_shape(
            repo,
            maintainer_workflows,
            major_areas,
        )
        key_entry_paths = self._build_key_entry_paths(
            repo,
            major_areas,
            repository_shape,
        )
        docs_surfaces = self._build_docs_surfaces(repo, major_areas)
        workflow_surfaces = self._build_workflow_surfaces(major_areas)
        good_starting_points = self._build_good_starting_points(
            repository_shape,
            key_entry_paths,
            workflow_surfaces,
        )
        contributor_checklist = self._build_contributor_checklist(
            local_setup_steps,
            docs_surfaces,
            workflow_surfaces,
        )
        repository_summary = self._build_summary(repo, maintainer_workflows)
        maintainer_summary = self._build_maintainer_summary(
            repo,
            repository_shape,
            maintainer_workflows,
            key_entry_paths,
            workflow_surfaces,
        )
        confidence = self._calculate_confidence(
            repo,
            maintainer_workflows,
            local_setup_steps,
            major_areas,
            key_entry_paths,
            workflow_surfaces,
        )

        return RepositoryIntelligenceResult(
            repository_summary=repository_summary,
            maintainer_summary=maintainer_summary,
            repository_shape=repository_shape,
            maintainer_workflows=maintainer_workflows,
            local_setup_steps=local_setup_steps,
            major_areas=major_areas,
            key_entry_paths=key_entry_paths,
            docs_surfaces=docs_surfaces,
            workflow_surfaces=workflow_surfaces,
            good_starting_points=good_starting_points,
            contributor_checklist=contributor_checklist,
            confidence=confidence,
        )

    def _infer_workflows(self, repo: RepositoryIntelligenceInput) -> list[str]:
        text = " ".join(
            [repo.description, repo.readme_text, repo.contributing_text]
        ).casefold()
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

    def _infer_repository_shape(
        self,
        repo: RepositoryIntelligenceInput,
        maintainer_workflows: list[str],
        major_areas: list[RepositoryArea],
    ) -> str:
        paths = {area.path for area in major_areas}
        docs_score = int(bool(repo.readme_text)) + int(bool(repo.contributing_text))
        docs_score += int("docs/" in paths) + int("examples/" in paths)

        workflow_score = int(".github/workflows/" in paths)
        workflow_score += int("tests/" in paths)
        workflow_score += int("issue triage" in maintainer_workflows)
        workflow_score += int("PR review preparation" in maintainer_workflows)
        workflow_score += int("release drafting" in maintainer_workflows)

        code_score = int("src/" in paths) + int("tests/" in paths)

        if docs_score >= code_score + 3 and "docs/" in paths:
            return "docs-forward maintainer toolkit"
        if workflow_score >= 4 and ".github/workflows/" in paths:
            return "automation-heavy maintainer workspace"
        if code_score >= 2 and ".github/workflows/" not in paths:
            return "code-first contributor toolkit"
        return "balanced maintainer toolkit"

    def _build_major_areas(self, top_level_paths: list[str]) -> list[RepositoryArea]:
        major_areas: list[RepositoryArea] = []
        seen_paths: set[str] = set()

        for path in top_level_paths:
            normalized = path.replace("\\", "/")
            if normalized in seen_paths:
                continue
            seen_paths.add(normalized)

            purpose = "Repository metadata and project configuration."
            contributor_entrypoint = (
                "Read this area when you need context about how the project "
                "is organized."
            )

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

    def _build_key_entry_paths(
        self,
        repo: RepositoryIntelligenceInput,
        major_areas: list[RepositoryArea],
        repository_shape: str,
    ) -> list[str]:
        available_paths = {area.path for area in major_areas}
        key_paths: list[str] = []

        for candidate in PATH_PRIORITIES[repository_shape]:
            if candidate == "README.md" and repo.readme_text:
                key_paths.append(candidate)
            elif candidate == "CONTRIBUTING.md" and repo.contributing_text:
                key_paths.append(candidate)
            elif candidate in available_paths:
                key_paths.append(candidate)

        return key_paths[:6]

    def _build_docs_surfaces(
        self,
        repo: RepositoryIntelligenceInput,
        major_areas: list[RepositoryArea],
    ) -> list[str]:
        paths = {area.path for area in major_areas}
        docs_surfaces: list[str] = []

        if repo.readme_text:
            docs_surfaces.append("README.md")
        if repo.contributing_text:
            docs_surfaces.append("CONTRIBUTING.md")
        if "docs/" in paths:
            docs_surfaces.append("docs/")
        if "examples/" in paths:
            docs_surfaces.append("examples/")

        return docs_surfaces

    def _build_workflow_surfaces(self, major_areas: list[RepositoryArea]) -> list[str]:
        paths = {area.path for area in major_areas}
        workflow_surfaces: list[str] = []

        for path in (".github/workflows/", "examples/", "tests/", "src/"):
            if path in paths:
                workflow_surfaces.append(path)

        return workflow_surfaces

    def _build_good_starting_points(
        self,
        repository_shape: str,
        key_entry_paths: list[str],
        workflow_surfaces: list[str],
    ) -> list[str]:
        starting_points: list[str] = []

        if "README.md" in key_entry_paths:
            starting_points.append(
                "Start with README.md to understand the maintainer promise "
                "and public workflows."
            )
        if repository_shape == "docs-forward maintainer toolkit":
            starting_points.append(
                "Use docs/ and CONTRIBUTING.md early so you can follow the "
                "intended contributor path."
            )
        if ".github/workflows/" in workflow_surfaces:
            starting_points.append(
                "Review .github/workflows/ to see how repository events "
                "enter the maintainer workflows."
            )
        if "examples/" in workflow_surfaces:
            starting_points.append(
                "Read examples/ next to see the checked-in JSON and markdown "
                "outputs maintainers review."
            )
        if "tests/" in workflow_surfaces:
            starting_points.append(
                "Use tests/ to learn which workflow outputs are treated as stable contracts."
            )
        if "src/" in workflow_surfaces:
            starting_points.append(
                "Move into src/ after the docs and fixtures make the "
                "workflow boundaries clear."
            )
        if not starting_points:
            starting_points.append(
                "Start with the README and CONTRIBUTING guide, then inspect "
                "the top-level project files."
            )

        return starting_points[:5]

    def _build_contributor_checklist(
        self,
        local_setup_steps: list[str],
        docs_surfaces: list[str],
        workflow_surfaces: list[str],
    ) -> list[str]:
        checklist = [
            "Read README.md and CONTRIBUTING.md before changing workflow behavior.",
            "Pick a narrow workflow area or fixture before making broader refactors.",
        ]

        if local_setup_steps:
            checklist.append(
                "Follow the documented local setup path before editing code "
                "or fixtures."
            )
        if any("pytest" in step for step in local_setup_steps):
            checklist.append(
                "Run pytest after changing schemas, heuristics, or workflow "
                "outputs."
            )
        if any("ruff" in step for step in local_setup_steps):
            checklist.append("Run ruff check . before opening a pull request.")
        if "docs/" in docs_surfaces:
            checklist.append(
                "Refresh docs or onboarding guidance when contributor paths "
                "become outdated."
            )
        if ".github/workflows/" in workflow_surfaces:
            checklist.append(
                "Treat workflow permission or trigger changes as "
                "maintainer-review items."
            )

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

    def _build_maintainer_summary(
        self,
        repo: RepositoryIntelligenceInput,
        repository_shape: str,
        maintainer_workflows: list[str],
        key_entry_paths: list[str],
        workflow_surfaces: list[str],
    ) -> str:
        workflow_text = ", ".join(maintainer_workflows[:3])
        entry_paths = ", ".join(key_entry_paths[:3]) or "README.md"
        article = "an" if repository_shape[:1].lower() in "aeiou" else "a"

        summary = (
            f"{repo.repository_name} looks like {article} {repository_shape} "
            f"centered on {workflow_text}. "
            f"Start with {entry_paths} if you need fast maintainer context."
        )

        if ".github/workflows/" in workflow_surfaces:
            summary += (
                " The automation layer is an explicit part of how "
                "contributors should understand the project."
            )

        return summary

    def _calculate_confidence(
        self,
        repo: RepositoryIntelligenceInput,
        maintainer_workflows: list[str],
        local_setup_steps: list[str],
        major_areas: list[RepositoryArea],
        key_entry_paths: list[str],
        workflow_surfaces: list[str],
    ) -> float:
        confidence = 0.55
        confidence += 0.1 if repo.description else 0.0
        confidence += min(len(maintainer_workflows) * 0.05, 0.15)
        confidence += min(len(local_setup_steps) * 0.03, 0.12)
        confidence += min(len(major_areas) * 0.03, 0.12)
        confidence += min(len(key_entry_paths) * 0.02, 0.08)
        confidence += min(len(workflow_surfaces) * 0.01, 0.04)
        return round(min(confidence, 0.95), 2)


def render_repo_intel_markdown(
    repo: RepositoryIntelligenceInput,
    result: RepositoryIntelligenceResult,
) -> str:
    maintainer_summary = result.maintainer_summary
    repository_shape = result.repository_shape
    workflow_lines = "\n".join(
        f"- `{workflow}`" for workflow in result.maintainer_workflows
    )
    setup_lines = "\n".join(
        f"- `{step}`" for step in result.local_setup_steps
    ) or "- No setup steps detected."
    area_lines = "\n".join(
        f"- `{area.path}`: {area.purpose} Entry point: {area.contributor_entrypoint}"
        for area in result.major_areas
    )
    key_entry_lines = "\n".join(f"- `{path}`" for path in result.key_entry_paths)
    key_entry_lines = key_entry_lines or "- No key entry paths detected."
    docs_surface_lines = "\n".join(f"- `{path}`" for path in result.docs_surfaces)
    docs_surface_lines = docs_surface_lines or "- No documentation surfaces detected."
    workflow_surface_lines = "\n".join(
        f"- `{path}`" for path in result.workflow_surfaces
    )
    workflow_surface_lines = workflow_surface_lines or "- No workflow surfaces detected."
    starting_point_lines = "\n".join(
        f"- {item}" for item in result.good_starting_points
    )
    contributor_checklist_lines = "\n".join(
        f"- {item}" for item in result.contributor_checklist
    )

    return f"""<!-- oss-maintainer-copilot:repo-intel -->
## OSS Maintainer Copilot Repository Intelligence

**Repository:** {repo.repository_name}

### Summary
{result.repository_summary}

### Maintainer Summary
{maintainer_summary}

### Repository Shape
`{repository_shape}`

### Maintainer Workflows
{workflow_lines}

### Local Setup Path
{setup_lines}

### Major Areas
{area_lines}

### Key Entry Paths
{key_entry_lines}

### Documentation Surfaces
{docs_surface_lines}

### Workflow Surfaces
{workflow_surface_lines}

### Good Starting Points
{starting_point_lines}

### Contributor Checklist
{contributor_checklist_lines}
"""
