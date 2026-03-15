# Contributing

## Development Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Project Standards

- Keep modules small and task-focused.
- Prefer typed models over loose dictionaries.
- Use deterministic logic where possible so tests stay stable.
- Every automated decision should include explicit structured reasoning.
- Avoid hardcoding repository-specific assumptions into agents or workflows.

## Common Commands

```bash
pytest
ruff check .
omc triage-issue --input tests/fixtures/issues/simple_docs_issue.json
omc summarize-pr --input tests/fixtures/pulls/sample_pr.json
omc generate-release-notes --input tests/fixtures/releases/release_window_mixed.json
```

## Pull Request Expectations

- Add or update tests with behavior changes.
- Update documentation when workflows, schemas, or CLI behavior changes.
- Keep public outputs stable unless there is a clear migration reason.
- Prefer additive schema evolution over breaking field renames.

## Extending the Project

When adding a new agent:

1. add or extend the relevant Pydantic schemas in `src/oss_maintainer_copilot/schemas`
2. implement task logic in `src/oss_maintainer_copilot/agents`
3. add or update prompt templates in `src/oss_maintainer_copilot/prompts` if the module will later support LLM-backed execution
4. provide representative fixtures in `tests/fixtures`
5. add focused pytest coverage before wiring the feature into GitHub Actions
