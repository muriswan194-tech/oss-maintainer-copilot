<!-- oss-maintainer-copilot:onboarding-map -->
## OSS Maintainer Copilot Onboarding Map

**Repository:** oss-maintainer-copilot

### Summary
oss-maintainer-copilot is a Python repository focused on issue triage, PR review preparation, release drafting. A maintainer operations toolkit for GitHub repositories with structured issue triage, PR briefs, release drafts, repository intelligence, and contributor onboarding guidance.

### First Session Goal
Get the project running locally, then trace one maintainer workflow from `.github/workflows/` through the CLI and checked-in outputs.

### Setup Checkpoints
- `python -m venv .venv`: Create an isolated development environment. Success signal: You can activate a local environment without errors.
- `. .venv/Scripts/activate`: Run the documented project setup command. Success signal: The command completes without blocking errors.
- `python -m pip install --upgrade pip`: Install the project and development dependencies. Success signal: The package and development tools install successfully.
- `python -m pip install -e .[dev]`: Install the project and development dependencies. Success signal: The package and development tools install successfully.
- `pytest`: Verify the current workflow outputs stay stable. Success signal: Tests complete without regressions.
- `ruff check .`: Check style and lint expectations before opening a pull request. Success signal: Ruff finishes without reporting blocking issues.

### Reading Order
- **Orient On The Repository**: Read the top-level docs to understand the maintainer workflows and public outputs. Paths: `README.md`, `CONTRIBUTING.md`. Done when: You can explain the repository purpose and name the core maintainer workflows.
- **Confirm Local Setup**: Use the documented setup files and commands to prepare a working development environment. Paths: `pyproject.toml`, `README.md`, `CONTRIBUTING.md`. Done when: You know which file controls dependencies and which commands are part of the local setup path.
- **Inspect The Automation Entry Points**: Start here to understand how repository events are wired into maintainer workflows. Paths: `.github/workflows/`. Done when: You know when to visit .github/workflows/ and what it owns in the repository.
- **Read The User-Facing Examples**: Start here if you want the fastest overview of what the project produces today. Paths: `examples/`. Done when: You know when to visit examples/ and what it owns in the repository.
- **Learn The Stable Contracts**: Start here to learn expected behavior before changing schemas or workflow heuristics. Paths: `tests/`. Done when: You know when to visit tests/ and what it owns in the repository.
- **Trace The Core Implementation**: Start here if you want to extend issue triage, PR briefs, release drafting, or repo intelligence. Paths: `src/`. Done when: You know when to visit src/ and what it owns in the repository.
- **Ship A Narrow First Change**: Choose one narrow maintainer workflow improvement, then trace it from automation to output examples and implementation. Paths: `.github/workflows/`, `examples/`, `src/`. Done when: Your first change touches the workflow logic and the public-facing artifacts that document it.

### Contributor Tracks
- **Workflow Output Stewardship**: Contributors who want to improve examples, fixtures, or output stability before touching deeper logic. First reads: `examples/`, `tests/`. First tasks: Refresh checked-in example outputs when workflows change.; Add regression fixtures for edge cases maintainers want to keep stable.
- **Heuristics And Schemas**: Contributors comfortable making small, typed changes to classification logic and output models. First reads: `src/`, `tests/`. First tasks: Refine a narrow heuristic and add a focused regression test.; Extend a schema additively before changing public output contracts.
- **Automation And Maintainer Operations**: Contributors who want to improve GitHub workflows, permission scopes, or maintainer-facing automation behavior. First reads: `.github/workflows/`, `examples/`. First tasks: Review workflow triggers and permission scopes for least privilege.; Tighten comment or artifact handling without widening automation behavior unexpectedly.

### Starter Tasks
- **Refresh An Example Flow** (`beginner`): Example outputs are the fastest way for maintainers and evaluators to understand the product. Suggested paths: `examples/`, `README.md`
- **Add A Regression Fixture** (`beginner`): Maintainers need stable outputs before they trust automation in triage, review, or release workflows. Suggested paths: `tests/`, `tests/fixtures/`
- **Improve One Narrow Heuristic** (`intermediate`): Small deterministic improvements compound well when they ship with fixtures and examples. Suggested paths: `src/`, `tests/`
- **Tighten One Workflow Surface** (`intermediate`): Maintainer automation becomes more trustworthy when permission scope and artifact handling stay explicit. Suggested paths: `.github/workflows/`

### Escalation Notes
- Ask a maintainer before renaming public output fields, changing checked-in example expectations, or widening automation behavior.
- Escalate changes that affect release note wording, issue labels, or contributor-facing output stability.
- Treat GitHub workflow permission changes as maintainer-review items, even when the code change seems small.
- Favor additive schema evolution and narrow heuristics before proposing broader refactors.
- Escalate onboarding-doc rewrites when they change the recommended contributor path or maintainer expectations.
