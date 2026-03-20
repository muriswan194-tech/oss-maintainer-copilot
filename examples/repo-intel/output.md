<!-- oss-maintainer-copilot:repo-intel -->
## OSS Maintainer Copilot Repository Intelligence

**Repository:** oss-maintainer-copilot

### Summary
oss-maintainer-copilot is a Python repository focused on issue triage, PR review preparation, release drafting. A maintainer operations toolkit for GitHub repositories with structured issue triage, PR briefs, release drafts, repository intelligence, and contributor onboarding guidance.

### Maintainer Summary
oss-maintainer-copilot looks like an automation-heavy maintainer workspace centered on issue triage, PR review preparation, release drafting. Start with README.md, CONTRIBUTING.md, .github/workflows/ if you need fast maintainer context. The automation layer is an explicit part of how contributors should understand the project.

### Repository Shape
`automation-heavy maintainer workspace`

### Maintainer Workflows
- `issue triage`
- `PR review preparation`
- `release drafting`
- `contributor onboarding`
- `repository intelligence`

### Local Setup Path
- `python -m venv .venv`
- `. .venv/Scripts/activate`
- `python -m pip install --upgrade pip`
- `python -m pip install -e .[dev]`
- `pytest`
- `ruff check .`

### Major Areas
- `src/`: Core workflow logic, schemas, and CLI code for maintainer automation. Entry point: Start here if you want to extend issue triage, PR briefs, release drafting, or repo intelligence.
- `tests/`: Fixture-driven regression coverage that keeps outputs stable and reviewable. Entry point: Start here to learn expected behavior before changing schemas or workflow heuristics.
- `examples/`: Checked-in sample inputs and outputs that show how maintainers will experience the workflows. Entry point: Start here if you want the fastest overview of what the project produces today.
- `docs/`: Supporting documentation and demo assets for contributors and evaluators. Entry point: Start here when you need context, visuals, or project-facing documentation.
- `.github/workflows/`: GitHub Actions entrypoints for issue, PR, release, and CI automation. Entry point: Start here to understand how repository events are wired into maintainer workflows.

### Key Entry Paths
- `README.md`
- `CONTRIBUTING.md`
- `.github/workflows/`
- `examples/`
- `tests/`
- `src/`

### Documentation Surfaces
- `README.md`
- `CONTRIBUTING.md`
- `docs/`
- `examples/`

### Workflow Surfaces
- `.github/workflows/`
- `examples/`
- `tests/`
- `src/`

### Good Starting Points
- Start with README.md to understand the maintainer promise and public workflows.
- Review .github/workflows/ to see how repository events enter the maintainer workflows.
- Read examples/ next to see the checked-in JSON and markdown outputs maintainers review.
- Use tests/ to learn which workflow outputs are treated as stable contracts.
- Move into src/ after the docs and fixtures make the workflow boundaries clear.

### Contributor Checklist
- Read README.md and CONTRIBUTING.md before changing workflow behavior.
- Pick a narrow workflow area or fixture before making broader refactors.
- Follow the documented local setup path before editing code or fixtures.
- Run pytest after changing schemas, heuristics, or workflow outputs.
- Run ruff check . before opening a pull request.
- Refresh docs or onboarding guidance when contributor paths become outdated.
- Treat workflow permission or trigger changes as maintainer-review items.
- Update examples, fixtures, and docs when public outputs change.
