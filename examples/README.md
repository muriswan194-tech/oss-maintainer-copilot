# Examples

This directory contains checked-in sample inputs and outputs for the current maintainer workflows.

The examples are based on repository fixtures so evaluators and contributors can understand the product quickly without running GitHub Actions first.

## Included Flows

- [Issue triage](./issue-triage/) shows the structured JSON result, recommended labels, and maintainer-facing markdown comment.
- [PR brief](./pr-brief/) shows the reviewer summary, risk flags, checklist, and release note snippet.
- [Release draft](./release-draft/) shows the markdown and JSON artifacts used to build a draft GitHub release.
- [Repository intelligence](./repo-intel/) shows the contributor-facing repository summary, setup path, major areas, and starting points.

## Reproducing The Examples

```bash
omc triage-issue --input tests/fixtures/issues/triage/docs_windows_setup.json --output examples/issue-triage/output.json --markdown examples/issue-triage/output.md
omc summarize-pr --input tests/fixtures/pulls/sample_pr.json --output examples/pr-brief/output.json --markdown examples/pr-brief/output.md
omc generate-release-notes --input tests/fixtures/releases/release_window_mixed.json --output examples/release-draft/output.json --markdown examples/release-draft/output.md
omc repo-intel --input tests/fixtures/repos/repo_intel_python_toolkit.json --output examples/repo-intel/output.json --markdown examples/repo-intel/output.md
```

The release example in this repository uses the March 20, 2026 render date so the checked-in output stays stable.
