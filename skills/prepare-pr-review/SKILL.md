# prepare-pr-review

## Purpose

Turn a pull request payload into a review brief that helps maintainers assess
scope, risk, changed areas, and reviewer focus before detailed file-by-file
inspection.

## Required Inputs

- PR title
- PR description
- Labels, if available
- Changed file paths
- Commit messages

## Workflow

1. Normalize the pull request payload into the `PullRequestSummaryInput` shape.
2. Detect changed areas from file paths.
3. Identify broad or noisy PR context from file count, commit count, and
   description quality.
4. Produce the review summary, risk flags, reviewer checklist, and release note
   snippet.
5. Render markdown suitable for a GitHub PR comment.

## Output Contract

- `short_summary`
- `technical_summary`
- `risk_assessment`
- `changed_areas`
- `review_focus`
- `input_warnings`
- `reviewer_checklist`
- `release_note_snippet`

## Guardrails

- Call out broad or noisy PR context instead of compressing it into a false
  sense of certainty.
- Treat automation, configuration, dependency, and breaking-change signals as
  higher risk.
- Keep the checklist review-oriented rather than implementation-oriented.

## Validation

- Run `omc summarize-pr --input <payload.json> --output <out.json> --markdown <out.md>`
- Compare results against `tests/fixtures/pulls/`
- Confirm the markdown includes the `oss-maintainer-copilot:pr-summary` marker
