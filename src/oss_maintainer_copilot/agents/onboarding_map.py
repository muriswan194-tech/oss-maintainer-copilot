from __future__ import annotations

from oss_maintainer_copilot.agents.repo_intel import RepositoryIntelligenceAgent
from oss_maintainer_copilot.schemas.onboarding import (
    ContributorTrack,
    OnboardingMapResult,
    OnboardingStep,
    SetupCheckpoint,
    StarterTask,
)
from oss_maintainer_copilot.schemas.repo_intel import (
    RepositoryIntelligenceInput,
    RepositoryIntelligenceResult,
)

PURPOSE_HINTS = (
    (
        "venv",
        "Create an isolated development environment.",
        "You can activate a local environment without errors.",
    ),
    (
        "pip install",
        "Install the project and development dependencies.",
        "The package and development tools install successfully.",
    ),
    (
        "pytest",
        "Verify the current workflow outputs stay stable.",
        "Tests complete without regressions.",
    ),
    (
        "ruff",
        "Check style and lint expectations before opening a pull request.",
        "Ruff finishes without reporting blocking issues.",
    ),
)


class OnboardingMapAgent:
    """Builds a contributor onboarding map on top of repository intelligence."""

    def build(self, repo: RepositoryIntelligenceInput) -> OnboardingMapResult:
        intel = RepositoryIntelligenceAgent().analyze(repo)
        setup_checkpoints = self._build_setup_checkpoints(intel.local_setup_steps)
        reading_order = self._build_reading_order(intel, repo)
        contributor_tracks = self._build_contributor_tracks(intel)
        starter_tasks = self._build_starter_tasks(intel)
        escalation_notes = self._build_escalation_notes(intel)
        confidence = self._calculate_confidence(
            intel.confidence,
            setup_checkpoints,
            reading_order,
            contributor_tracks,
        )

        return OnboardingMapResult(
            repository_summary=intel.repository_summary,
            first_session_goal=self._build_first_session_goal(
                intel.repository_shape,
                intel.maintainer_workflows,
                intel.workflow_surfaces,
            ),
            setup_checkpoints=setup_checkpoints,
            reading_order=reading_order,
            contributor_tracks=contributor_tracks,
            starter_tasks=starter_tasks,
            escalation_notes=escalation_notes,
            confidence=confidence,
        )

    def _build_first_session_goal(
        self,
        repository_shape: str,
        maintainer_workflows: list[str],
        workflow_surfaces: list[str],
    ) -> str:
        if repository_shape == "automation-heavy maintainer workspace":
            return (
                "Get the project running locally, then trace one maintainer workflow from "
                "`.github/workflows/` through the CLI and checked-in outputs."
            )
        if repository_shape == "docs-forward maintainer toolkit":
            return (
                "Get the local docs or examples path oriented, then follow one contributor "
                "journey from README.md into docs, examples, and tests."
            )
        if ".github/workflows/" in workflow_surfaces and maintainer_workflows:
            workflow = maintainer_workflows[0]
            return (
                f"Get the project running locally, then trace one complete {workflow} workflow "
                "from the automation entrypoint into fixtures and implementation."
            )
        if maintainer_workflows:
            workflow = maintainer_workflows[0]
            if not workflow_surfaces:
                return (
                    f"Get the project running locally, then trace one complete {workflow} "
                    "workflow from the setup path into the implementation."
                )
            if "examples/" not in workflow_surfaces:
                return (
                    f"Get the project running locally, then trace one complete {workflow} "
                    "workflow from tests into the implementation."
                )
            return (
                f"Get the project running locally, then trace one complete {workflow} workflow "
                "from examples and fixtures into the implementation."
            )
        return (
            "Get the project running locally, then trace one small "
            "contributor workflow end to end."
        )

    def _build_setup_checkpoints(
        self,
        local_setup_steps: list[str],
    ) -> list[SetupCheckpoint]:
        checkpoints: list[SetupCheckpoint] = []
        for step in local_setup_steps:
            purpose = "Run the documented project setup command."
            success_signal = "The command completes without blocking errors."

            lower_step = step.casefold()
            for hint, hint_purpose, hint_signal in PURPOSE_HINTS:
                if hint in lower_step:
                    purpose = hint_purpose
                    success_signal = hint_signal
                    break

            checkpoints.append(
                SetupCheckpoint(
                    command=step,
                    purpose=purpose,
                    success_signal=success_signal,
                )
            )

        return checkpoints

    def _build_reading_order(
        self,
        intel: RepositoryIntelligenceResult,
        repo: RepositoryIntelligenceInput,
    ) -> list[OnboardingStep]:
        steps = [
            OnboardingStep(
                title="Orient On The Repository",
                objective=(
                    "Read the top-level docs to understand the maintainer "
                    "workflows and public outputs."
                ),
                paths=["README.md", "CONTRIBUTING.md"],
                completion_signal=(
                    "You can explain the repository purpose and name the "
                    "core maintainer workflows."
                ),
            ),
        ]

        if repo.setup_files:
            steps.append(
                OnboardingStep(
                    title="Confirm Local Setup",
                    objective=(
                        "Use the documented setup files and commands to "
                        "prepare a working development environment."
                    ),
                    paths=repo.setup_files[:3],
                    completion_signal=(
                        "You know which file controls dependencies and which "
                        "commands are part of the local setup path."
                    ),
                )
            )

        area_by_path = {area.path: area for area in intel.major_areas}
        for path in intel.key_entry_paths:
            if path in {"README.md", "CONTRIBUTING.md"}:
                continue
            if path in repo.setup_files[:3]:
                continue
            area = area_by_path.get(path)
            if area is None:
                continue
            steps.append(
                OnboardingStep(
                    title=self._title_for_area(path, intel.repository_shape),
                    objective=area.contributor_entrypoint,
                    paths=[path],
                    completion_signal=(
                        f"You know when to visit {path} and what it owns in "
                        "the repository."
                    ),
                )
            )

        first_change_paths = ["tests/", "examples/", "src/"]
        first_change_objective = (
            "Choose a small workflow or example update, then carry it "
            "through fixtures, code, and docs."
        )

        if intel.repository_shape == "docs-forward maintainer toolkit":
            first_change_paths = ["docs/", "examples/", "tests/"]
            first_change_objective = (
                "Choose one contributor-facing docs or example improvement, "
                "then confirm the updated guidance still matches tests and "
                "examples."
            )
        elif intel.repository_shape == "automation-heavy maintainer workspace":
            first_change_paths = [".github/workflows/", "examples/", "src/"]
            first_change_objective = (
                "Choose one narrow maintainer workflow improvement, then "
                "trace it from automation to output examples and "
                "implementation."
            )

        steps.append(
            OnboardingStep(
                title="Ship A Narrow First Change",
                objective=first_change_objective,
                paths=first_change_paths,
                completion_signal=(
                    "Your first change touches the workflow logic and the "
                    "public-facing artifacts that document it."
                ),
            )
        )
        return steps

    def _build_contributor_tracks(
        self,
        intel: RepositoryIntelligenceResult,
    ) -> list[ContributorTrack]:
        paths = {area.path for area in intel.major_areas}
        tracks: list[ContributorTrack] = []

        if intel.repository_shape == "docs-forward maintainer toolkit":
            tracks.append(
                ContributorTrack(
                    name="Docs And Onboarding Clarity",
                    fit_for=(
                        "Contributors who want to improve contributor "
                        "guidance, reading order, and maintainer-facing "
                        "explanations before changing deeper logic."
                    ),
                    first_reads=["README.md", "CONTRIBUTING.md", "docs/"],
                    first_tasks=[
                        (
                            "Clarify one contributor path without changing "
                            "the underlying workflow contract."
                        ),
                        (
                            "Refresh docs and examples together so onboarding "
                            "guidance stays believable."
                        ),
                    ],
                )
            )

        if "examples/" in paths or "tests/" in paths:
            tracks.append(
                ContributorTrack(
                    name="Workflow Output Stewardship",
                    fit_for=(
                        "Contributors who want to improve examples, fixtures, "
                        "or output stability before touching deeper logic."
                    ),
                    first_reads=["examples/", "tests/"],
                    first_tasks=[
                        "Refresh checked-in example outputs when workflows change.",
                        "Add regression fixtures for edge cases maintainers want to keep stable.",
                    ],
                )
            )

        if "src/" in paths:
            tracks.append(
                ContributorTrack(
                    name="Heuristics And Schemas",
                    fit_for=(
                        "Contributors comfortable making small, typed changes "
                        "to classification logic and output models."
                    ),
                    first_reads=["src/", "tests/"],
                    first_tasks=[
                        "Refine a narrow heuristic and add a focused regression test.",
                        "Extend a schema additively before changing public output contracts.",
                    ],
                )
            )

        if ".github/workflows/" in intel.workflow_surfaces:
            tracks.append(
                ContributorTrack(
                    name="Automation And Maintainer Operations",
                    fit_for=(
                        "Contributors who want to improve GitHub workflows, "
                        "permission scopes, or maintainer-facing automation "
                        "behavior."
                    ),
                    first_reads=[".github/workflows/", "examples/"],
                    first_tasks=[
                        (
                            "Review workflow triggers and permission scopes "
                            "for least privilege."
                        ),
                        (
                            "Tighten comment or artifact handling without "
                            "widening automation behavior unexpectedly."
                        ),
                    ],
                )
            )

        if not tracks:
            tracks.append(
                ContributorTrack(
                    name="General Repository Familiarization",
                    fit_for=(
                        "Contributors who are still learning the repository "
                        "and need a safe first lane into the codebase."
                    ),
                    first_reads=["README.md", "CONTRIBUTING.md"],
                    first_tasks=[
                        (
                            "Summarize the current workflow outputs and note "
                            "any unclear contributor instructions."
                        ),
                        (
                            "Refresh one small example or doc path so the "
                            "next contributor can ramp up faster."
                        ),
                    ],
                )
            )

        return tracks

    def _build_starter_tasks(self, intel: RepositoryIntelligenceResult) -> list[StarterTask]:
        paths = {area.path for area in intel.major_areas}
        tasks: list[StarterTask] = []

        if intel.repository_shape == "docs-forward maintainer toolkit":
            tasks.append(
                StarterTask(
                    title="Clarify A Contributor Path",
                    reason=(
                        "The fastest way to help maintainers in a "
                        "docs-forward repo is to remove one confusing "
                        "onboarding step."
                    ),
                    suggested_paths=["README.md", "CONTRIBUTING.md", "docs/"],
                    difficulty="beginner",
                )
            )
        if "examples/" in paths:
            tasks.append(
                StarterTask(
                    title="Refresh An Example Flow",
                    reason=(
                        "Example outputs are the fastest way for maintainers "
                        "and evaluators to understand the product."
                    ),
                    suggested_paths=["examples/", "README.md"],
                    difficulty="beginner",
                )
            )
        if "tests/" in paths:
            tasks.append(
                StarterTask(
                    title="Add A Regression Fixture",
                    reason=(
                        "Maintainers need stable outputs before they trust "
                        "automation in triage, review, or release workflows."
                    ),
                    suggested_paths=["tests/", "tests/fixtures/"],
                    difficulty="beginner",
                )
            )
        if "src/" in paths:
            tasks.append(
                StarterTask(
                    title="Improve One Narrow Heuristic",
                    reason=(
                        "Small deterministic improvements compound well when "
                        "they ship with fixtures and examples."
                    ),
                    suggested_paths=["src/", "tests/"],
                    difficulty="intermediate",
                )
            )
        if ".github/workflows/" in intel.workflow_surfaces:
            tasks.append(
                StarterTask(
                    title="Tighten One Workflow Surface",
                    reason=(
                        "Maintainer automation becomes more trustworthy when "
                        "permission scope and artifact handling stay explicit."
                    ),
                    suggested_paths=[".github/workflows/"],
                    difficulty="intermediate",
                )
            )

        if not tasks:
            tasks.append(
                StarterTask(
                    title="Clarify One Onboarding Step",
                    reason=(
                        "A small docs or example improvement is the safest "
                        "way to reduce maintainer repetition in a new "
                        "repository."
                    ),
                    suggested_paths=["README.md", "CONTRIBUTING.md"],
                    difficulty="beginner",
                )
            )
        return tasks

    def _build_escalation_notes(self, intel: RepositoryIntelligenceResult) -> list[str]:
        notes = [
            (
                "Ask a maintainer before renaming public output fields, "
                "changing checked-in example expectations, or widening "
                "automation behavior."
            ),
            (
                "Escalate changes that affect release note wording, issue "
                "labels, or contributor-facing output stability."
            ),
        ]

        if ".github/workflows/" in intel.workflow_surfaces:
            notes.append(
                "Treat GitHub workflow permission changes as "
                "maintainer-review items, even when the code change "
                "seems small."
            )
        if any(area.path == "src/" for area in intel.major_areas):
            notes.append(
                "Favor additive schema evolution and narrow heuristics "
                "before proposing broader refactors."
            )
        if "docs/" in intel.docs_surfaces:
            notes.append(
                "Escalate onboarding-doc rewrites when they change the "
                "recommended contributor path or maintainer expectations."
            )

        return notes

    def _calculate_confidence(
        self,
        base_confidence: float,
        setup_checkpoints: list[SetupCheckpoint],
        reading_order: list[OnboardingStep],
        contributor_tracks: list[ContributorTrack],
    ) -> float:
        confidence = base_confidence - 0.04
        confidence += min(len(setup_checkpoints) * 0.02, 0.1)
        confidence += min(len(reading_order) * 0.01, 0.08)
        confidence += min(len(contributor_tracks) * 0.03, 0.09)
        return round(min(max(confidence, 0.0), 0.98), 2)

    def _title_for_area(self, path: str, repository_shape: str) -> str:
        if path == "examples/":
            if repository_shape == "docs-forward maintainer toolkit":
                return "Read The Contributor Examples"
            return "Read The User-Facing Examples"
        if path == "tests/":
            return "Learn The Stable Contracts"
        if path == "src/":
            return "Trace The Core Implementation"
        if path == ".github/workflows/":
            return "Inspect The Automation Entry Points"
        if path == "docs/":
            if repository_shape == "docs-forward maintainer toolkit":
                return "Review The Contributor Docs Path"
            return "Review Supporting Docs And Assets"
        return f"Inspect {path}"


def render_onboarding_map_markdown(
    repo: RepositoryIntelligenceInput,
    result: OnboardingMapResult,
) -> str:
    setup_lines = "\n".join(
        f"- `{checkpoint.command}`: {checkpoint.purpose} "
        f"Success signal: {checkpoint.success_signal}"
        for checkpoint in result.setup_checkpoints
    ) or "- No setup checkpoints detected."
    reading_order_lines = "\n".join(
        f"- **{step.title}**: {step.objective} "
        f"Paths: {', '.join(f'`{path}`' for path in step.paths)}. "
        f"Done when: {step.completion_signal}"
        for step in result.reading_order
    )
    track_lines = "\n".join(
        f"- **{track.name}**: {track.fit_for} "
        f"First reads: {', '.join(f'`{path}`' for path in track.first_reads)}. "
        f"First tasks: {'; '.join(track.first_tasks)}"
        for track in result.contributor_tracks
    ) or "- No contributor tracks detected yet."
    starter_task_lines = "\n".join(
        f"- **{task.title}** (`{task.difficulty}`): {task.reason} "
        f"Suggested paths: "
        f"{', '.join(f'`{path}`' for path in task.suggested_paths)}"
        for task in result.starter_tasks
    ) or "- No starter tasks detected yet."
    escalation_lines = "\n".join(
        f"- {note}" for note in result.escalation_notes
    ) or "- No escalation notes detected."

    return f"""<!-- oss-maintainer-copilot:onboarding-map -->
## OSS Maintainer Copilot Onboarding Map

**Repository:** {repo.repository_name}

### Summary
{result.repository_summary}

### First Session Goal
{result.first_session_goal}

### Setup Checkpoints
{setup_lines}

### Reading Order
{reading_order_lines}

### Contributor Tracks
{track_lines}

### Starter Tasks
{starter_task_lines}

### Escalation Notes
{escalation_lines}
"""
