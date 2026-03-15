# Roadmap

## Current Milestone

- [x] Repository scaffold
- [x] Shared Pydantic schemas
- [x] Issue triage agent
- [x] Dedicated good-first-issue classifier
- [x] PR summarizer with reviewer-focused output
- [x] Release notes generator grouped by change type
- [x] Contributor guidance generation
- [x] CLI entrypoints for issue triage, PR summary, and release notes
- [x] GitHub Actions for issue triage, PR summary, and release drafts
- [x] Test fixtures and unit tests for issue, PR, and release flows

## Next Milestones

- [ ] Richer GitHub API collection and pagination support for large repositories
- [ ] End-to-end workflow tests against GitHub Actions runner behavior

## Design Principles

- Keep the core package repo-agnostic.
- Make every decision inspectable and testable.
- Optimize for contributor readability over clever abstractions.
- Prefer explicit schemas to ad hoc payload handling.
