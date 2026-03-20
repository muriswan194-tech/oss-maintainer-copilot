# onboard-contributor

## Purpose

Convert repository intelligence into a contributor onboarding map with setup
checkpoints, reading order, starter tasks, and escalation guidance that matches
the repo shape.

## Required Inputs

- Repository name and description
- README and CONTRIBUTING text, if available
- Setup files
- Top-level paths

## Workflow

1. Build repository intelligence from normalized repo metadata.
2. Infer repository shape and maintainer workflow surfaces.
3. Create a first-session goal tailored to the repo type.
4. Build setup checkpoints, reading order, contributor tracks, and
   `starter_tasks`.
5. Render markdown suitable for contributor handoff or maintainer review.

## Output Contract

- `repository_summary`
- `first_session_goal`
- `setup_checkpoints`
- `reading_order`
- `contributor_tracks`
- `starter_tasks`
- `escalation_notes`
- `confidence`

## Guardrails

- Keep onboarding advice grounded in the actual repo layout.
- Prefer specific paths and first tasks over generic contributor advice.
- Provide safe fallbacks for sparse repos instead of fabricating detail.

## Validation

- Run `omc onboarding-map --input <payload.json> --output <out.json> --markdown <out.md>`
- Compare results against `tests/fixtures/repos/`
- Confirm the markdown includes the `oss-maintainer-copilot:onboarding-map`
  marker
