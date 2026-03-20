# draft-release-notes

## Purpose

Build a draft GitHub release from merged pull request metadata with grouped
sections, highlights, contributor acknowledgments, and explicit
`data_quality_notes` when metadata is incomplete.

## Required Inputs

- Previous version tag
- Current version tag
- Merged pull request metadata in the `ReleaseNotesInput` shape
- PR labels, authors, merge dates, and bodies when available

## Workflow

1. Normalize merged PR metadata into `ReleaseNotesInput`.
2. Deduplicate repeated PR entries.
3. Group PRs into release sections using labels, titles, and bodies.
4. Build highlights, breaking changes, and contributor acknowledgments.
5. Surface `data_quality_notes` for unlabeled, duplicate, or weakly described
   entries.
6. Render markdown suitable for a draft GitHub release body.

## Output Contract

- `release_title`
- `highlights`
- `grouped_markdown_sections`
- `breaking_changes_section`
- `data_quality_notes`
- `contributor_acknowledgments`

## Guardrails

- Prefer honest data quality notes over pretending incomplete metadata is
  complete.
- Keep breaking changes and upgrade notes explicit.
- Avoid duplicate contributor counts when PR metadata repeats across commits.

## Validation

- Run `omc generate-release-notes --input <payload.json> --output <out.json> --markdown <out.md>`
- Compare results against `tests/fixtures/releases/`
- Confirm release markdown contains `Highlights`, `Breaking Changes`, and
  `Thanks`
