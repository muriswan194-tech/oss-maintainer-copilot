# triage-issue

## Purpose

Classify a GitHub issue into a maintainer-friendly triage result with
deterministic labels, missing-context notes, and contributor guidance.

## Required Inputs

- Issue title
- Issue body
- Existing labels, if available
- Repository metadata, if available

## Workflow

1. Normalize the issue payload into the `IssueTriageInput` shape.
2. Collect issue signals from the title, body, labels, and repository context.
3. Score category, difficulty, missing context, and `good_first_issue`.
4. Produce JSON output and maintainer-facing markdown.
5. Generate recommended labels from the final triage result.

## Output Contract

- `category`
- `difficulty`
- `good_first_issue`
- `confidence`
- `missing_context`
- `reasoning`
- `recommended_labels`

## Guardrails

- Prefer deterministic heuristics over speculative repo-specific assumptions.
- Keep `good_first_issue` conservative when the issue touches risky or unclear
  areas.
- Mark missing context explicitly instead of guessing.

## Validation

- Run `omc triage-issue --input <payload.json> --output <out.json> --markdown <out.md>`
- Compare results against `tests/fixtures/issues/triage/`
- Confirm the markdown includes the `oss-maintainer-copilot:issue-triage`
  marker
