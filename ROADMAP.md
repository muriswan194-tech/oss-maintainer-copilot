# Roadmap

## Current Milestone

- [x] Repository scaffold
- [x] Shared Pydantic schemas
- [x] Issue triage agent
- [x] Dedicated good-first-issue classifier
- [x] PR summarizer with reviewer-focused output
- [x] Release notes generator grouped by change type
- [x] Initial repository intelligence workflow
- [x] Contributor onboarding map output built on top of repository intelligence
- [x] CLI entrypoints for issue triage, PR summary, release notes, repository intelligence, and onboarding maps
- [x] GitHub Actions for issue triage, PR summary, and release drafts
- [x] Test fixtures and unit tests for issue, PR, and release flows

## Next Milestone: v0.2 Maintainer Workspace Foundation

- [x] Expand the shared repository intelligence module with deeper repo parsing and more tailored onboarding guidance
- [x] Refactor issue triage into clearer signal, scoring, and rendering layers for easier extension
- [x] Improve PR briefs with richer changed-area detection and better support for large or noisy pull requests
- [x] Improve release drafting inputs with stronger GitHub data collection and safer draft generation before a new tag exists
- [x] Add evaluation fixtures and regression-style tests for triage, PR brief, release, repo intelligence, and onboarding outputs
- [x] Add end-to-end workflow contract tests for GitHub Actions behavior
- [x] Define reusable skill boundaries for recurring maintainer workflows so automation can stay portable across surfaces

Detailed implementation plan: [docs/v0.2-maintainer-workspace-plan.md](./docs/v0.2-maintainer-workspace-plan.md)

## Later Milestones

- [ ] Add repository intelligence summaries for maintainers who need fast repo context
- [ ] Add maintainer-facing documentation for extending heuristics and schemas safely
- [ ] Explore a small web or dashboard layer only after the automation core is proven useful

## Design Principles

- Keep the core package repo-agnostic.
- Make every decision inspectable and testable.
- Optimize for contributor readability over clever abstractions.
- Prefer explicit schemas to ad hoc payload handling.
- Strengthen shared maintainer workflows before adding a hosted UI layer.
