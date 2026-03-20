<!-- oss-maintainer-copilot:pr-summary -->
## OSS Maintainer Copilot PR Summary

**Title:** Restructure maintainer workflows, release flow, and docs examples

### Short Summary
Broad change across automation, application code, tests, documentation, configuration touching 9 files.

### Technical Summary
The PR spans 9 files across automation, application code, tests, documentation, configuration. Reviewers should confirm that the stated scope matches the actual change surface before going file by file. Commits mention: refactor: reorganize maintainer workflow summaries; feat: harden release note grouping; docs: refresh examples and maintainer docs.

### Changed Areas
- `automation`
- `application code`
- `tests`
- `documentation`
- `configuration`

### Input Warnings
- Broad PR context: 9 files, 5 commits, 5 changed areas.

### Risk Assessment
- Level: `high`
- Summary: High risk because the PR touches sensitive runtime or automation areas.

Flags:
- `risky-file-paths`
- `risky-commit-context`
- `broad-change-surface`
- `noisy-pr-context`

### Review Focus
- Validate workflow triggers, permission scopes, and comment or artifact handling.
- Review runtime behavior, compatibility, and error handling in the touched code.
- Confirm tests still reflect the intended workflow contract.
- Check contributor-facing instructions, wording, and links for accuracy.
- Check defaults, environment assumptions, and deployment impact.
- Review in passes: high-risk areas first, then representative files from each remaining area.

### Reviewer Checklist
- Verify the summary matches the actual code and commit intent.
- Confirm the changed-area labels match the touched files.
- Start by checking whether the PR title and description understate the actual scope.
- Review high-risk or high-churn areas first before doing a line-by-line pass.
- Review the touched files for unintended scope expansion.
- Focus review on: Validate workflow triggers, permission scopes, and comment or artifact handling.
- Focus review on: Review runtime behavior, compatibility, and error handling in the touched code.
- Focus review on: Confirm tests still reflect the intended workflow contract.
- Confirm tests cover the changed runtime behavior.

### Release Note Snippet
Updated: Restructure maintainer workflows, release flow, and docs examples
