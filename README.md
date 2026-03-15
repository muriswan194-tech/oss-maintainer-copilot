# OSS Maintainer Copilot

OSS Maintainer Copilot is a modular Python toolkit for maintainers who want structured, contributor-friendly GitHub automation without building a full SaaS product. It is designed around typed schemas, deterministic core logic, and GitHub Actions workflows that can be adapted to different repositories.

This repository is being built in milestones. The current milestone includes:

- repository scaffolding for an open-source Python project
- shared Pydantic schemas for GitHub payloads and triage outputs
- an issue triage agent with structured reasoning
- a dedicated good-first-issue classifier for safe contributor onboarding
- a pull request summarizer with typed outputs for reviewer workflows
- a release notes generator that produces polished draft-ready markdown
- contributor guidance generation for triaged issues
- CLI entrypoints for issue triage, PR summaries, and release notes
- pytest fixtures and unit tests
- GitHub Actions workflows for issue triage, PR summaries, and release drafts

## Problem

Maintainers spend repeated effort on the same operational tasks:

- deciding issue difficulty
- identifying likely good first issues
- turning vague tickets into contributor guidance
- summarizing pull requests
- assembling release notes from merged work

Most automation in this space is either repo-specific, opaque, or too tightly coupled. This project aims to keep the architecture small, typed, and easy for contributors to extend.

## Architecture

```text
src/oss_maintainer_copilot/
  agents/      Issue triage, good-first-issue, PR summary, and release note agents
  github/      GitHub payload readers and API-facing wrappers
  prompts/     Task-specific prompt templates for future LLM-backed flows
  schemas/     Shared Pydantic models for inputs and outputs
tests/
  fixtures/    Sample GitHub issue, PR, and release payloads
.github/workflows/
  issue-triage.yml
  pr-summary.yml
  release-notes.yml
```

The current implementation favors deterministic heuristics so outputs are stable and testable. Each decision is accompanied by structured reasoning that downstream automation can consume.

## Issue Triage

The issue triage agent accepts an issue title, body, labels, and optional repository metadata. It produces:

- category
- difficulty
- good first issue boolean
- confidence
- missing context fields
- structured reasoning

The separate good-first-issue agent sits on top of triage output and applies stricter onboarding rules before recommending that a maintainer apply a newcomer-friendly label.

## PR Summaries

The PR summarizer accepts a PR title, description, changed file paths, and commit messages. It produces:

- a short summary for status updates
- a technical summary oriented toward reviewers
- a structured risk assessment
- a reviewer checklist
- a release note snippet

It currently includes focused heuristics for docs-only PRs, risky workflow or runtime changes, and explicit breaking changes.

## Release Notes

The release notes generator accepts merged PR metadata across a version range and produces:

- a release title
- release highlights
- grouped markdown sections for features, fixes, documentation, and refactors
- a dedicated breaking changes section
- contributor acknowledgments

The rendered markdown is designed to be pasted directly into a GitHub release draft with minimal cleanup.

## Issue Triage Output

The issue triage agent currently classifies:

- difficulty: `beginner`, `intermediate`, `advanced`, or `maintainer_only`
- scope: `narrow`, `moderate`, or `broad`
- risk: `low`, `medium`, or `high`
- context: `low`, `medium`, or `high`
- good first issue candidate: `true` only when scope is narrow, risk is low, and context is low

It also drafts contributor guidance with:

- likely files or directories to inspect
- local setup steps
- acceptance criteria
- follow-up questions when the issue description is underspecified

## Getting Started

```bash
python -m venv .venv
. .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
pytest
```

Run issue triage against a GitHub issue payload or issue event payload:

```bash
omc triage-issue --input tests/fixtures/issues/simple_docs_issue.json
```

Run PR summarization against a normalized PR payload or GitHub PR event payload:

```bash
omc summarize-pr --input tests/fixtures/pulls/pr_event_payload.json
```

Generate release notes from merged PR metadata:

```bash
omc generate-release-notes --input tests/fixtures/releases/release_window_mixed.json
```

Write machine-readable and markdown output:

```bash
omc triage-issue \
  --input tests/fixtures/issues/simple_docs_issue.json \
  --output triage.json \
  --markdown triage.md
```

```bash
omc summarize-pr \
  --input tests/fixtures/pulls/sample_pr.json \
  --output pr-summary.json \
  --markdown pr-summary.md
```

```bash
omc generate-release-notes \
  --input tests/fixtures/releases/release_window_mixed.json \
  --output release-notes.json \
  --markdown release-notes.md
```

## GitHub Actions

The included [issue-triage workflow](./.github/workflows/issue-triage.yml) runs on opened, edited, and reopened issues. It:

1. installs the package
2. runs the triage CLI against the GitHub event payload
3. creates missing automation labels if needed
4. applies recommended labels
5. posts or updates a triage comment with structured guidance

The included [pr-summary workflow](./.github/workflows/pr-summary.yml) runs on pull request activity. It collects changed files and commit subjects, runs the PR summarizer, and posts or updates a summary comment on the PR.

The included [release-notes workflow](./.github/workflows/release-notes.yml) is triggered manually with a previous and current version tag. It gathers merged pull requests across that range, generates polished markdown, and creates or updates a draft GitHub release.

## Roadmap

The next milestones add:

- richer GitHub API collection and pagination support
- broader workflow integration tests

See [ROADMAP.md](./ROADMAP.md) for the planned sequence.
