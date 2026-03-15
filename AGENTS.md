# AGENTS.md

## Repository Intent

This repository implements a modular maintainer assistant for GitHub workflows. Contributors should preserve a small-core architecture, typed boundaries, and deterministic behavior where possible.

## Engineering Rules

- Use Python 3.11+.
- Keep source code under `src/oss_maintainer_copilot`.
- Put task logic in `agents`, payload readers in `github`, prompt templates in `prompts`, and typed models in `schemas`.
- Use Pydantic models for structured inputs and outputs.
- Prefer pure functions and small classes that are easy to test.
- Every automated classification or recommendation must include structured reasoning.
- Avoid repository-specific rules or labels unless they are clearly namespaced and documented.

## Testing Rules

- Add pytest coverage for every new agent or schema change.
- Store realistic sample payloads in `tests/fixtures`.
- Favor deterministic tests over mock-heavy tests.

## Documentation Rules

- Keep `README.md` aligned with the implemented feature set.
- Update `ROADMAP.md` when milestone scope changes.
- Add usage examples for new CLI commands or workflows.
