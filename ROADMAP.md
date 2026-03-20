# Roadmap

## Current Milestone

- [x] Repository scaffold
- [x] Shared Pydantic schemas
- [x] Issue triage agent
- [x] Dedicated good-first-issue classifier
- [x] PR summarizer with reviewer-focused output
- [x] Release notes generator grouped by change type
- [x] Initial repository intelligence workflow
- [x] CLI entrypoints for issue triage, PR summary, release notes, and repository intelligence
- [x] GitHub Actions for issue triage, PR summary, and release drafts
- [x] Test fixtures and unit tests for issue, PR, and release flows

## Next Milestone: v0.2 Maintainer Workspace Foundation

- [ ] Expand the shared repository intelligence module with deeper repo parsing and onboarding guidance
- [ ] Build an onboarding map output on top of repository intelligence for contributor-friendly repo orientation
- [ ] Refactor issue triage into clearer signal, scoring, and rendering layers for easier extension
- [ ] Improve PR briefs with richer changed-area detection and better support for large or noisy pull requests
- [ ] Improve release drafting inputs with stronger GitHub data collection and pagination support
- [ ] Add evaluation fixtures and regression-style tests for triage, PR brief, and release outputs
- [ ] Add end-to-end workflow contract tests for GitHub Actions behavior
- [ ] Define skill boundaries for recurring maintainer workflows so automation can stay reusable across surfaces

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
