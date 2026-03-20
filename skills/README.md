# Skills

This directory contains reusable maintainer workflow definitions for the core
`OSS Maintainer Copilot` tasks.

Each skill is designed to be portable across local CLI runs, GitHub Action
automation, and future agent-driven workflows. The checked-in skills focus on:

- `triage-issue`
- `prepare-pr-review`
- `draft-release-notes`
- `onboard-contributor`

Every skill definition includes:

- the workflow purpose
- required inputs
- step-by-step instructions
- output contract expectations
- validation guidance tied to the CLI and fixtures in this repository
