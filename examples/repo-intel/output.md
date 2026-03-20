<!-- oss-maintainer-copilot:repo-intel -->
## OSS Maintainer Copilot Repository Intelligence

**Repository:** oss-maintainer-copilot

### Summary
oss-maintainer-copilot is a Python repository focused on issue triage, PR review preparation, release drafting. A maintainer operations toolkit for GitHub repositories with structured issue triage, PR briefs, release drafts, and repository intelligence.

### Maintainer Workflows
- `issue triage`
- `PR review preparation`
- `release drafting`
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

### Good Starting Points
- Start with examples/ to see the JSON and markdown outputs expected from each workflow.
- Read tests/ next to understand which public outputs are treated as stable.
- Move into src/ once you know which workflow you want to extend or debug.
- Review .github/workflows/ when you want to understand how repository events trigger automation.

### Contributor Checklist
- Read README.md and CONTRIBUTING.md before changing workflow behavior.
- Pick a narrow workflow area or fixture before making broader refactors.
- Follow the documented local setup path before editing code or fixtures.
- Run pytest after changing schemas, heuristics, or workflow outputs.
- Run ruff check . before opening a pull request.
- Update examples, fixtures, and docs when public outputs change.
