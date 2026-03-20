from __future__ import annotations

from oss_maintainer_copilot.schemas.triage import IssueTriageInput, IssueTriageResult


def build_triage_labels(result: IssueTriageResult) -> list[str]:
    labels = [
        f"triage:category:{result.category.value}",
        f"difficulty:{result.difficulty.value}",
    ]
    if result.good_first_issue:
        labels.append("triage:good-first-issue")
    if result.missing_context:
        labels.append("triage:missing-context")
    return labels


def render_triage_markdown(issue: IssueTriageInput, triage: IssueTriageResult) -> str:
    reasoning_lines = "\n".join(
        f"- **{item.category}**: `{item.decision}` ({'; '.join(item.evidence)})"
        for item in triage.reasoning
    )
    missing_context_lines = (
        "\n".join(f"- `{item}`" for item in triage.missing_context) or "- None."
    )

    return f"""<!-- oss-maintainer-copilot:issue-triage -->
## OSS Maintainer Copilot Triage

**Issue:** {issue.title}

### Classification

- Category: `{triage.category.value}`
- Difficulty: `{triage.difficulty.value}`
- Good first issue: `{str(triage.good_first_issue).lower()}`
- Confidence: `{triage.confidence:.2f}`

### Missing Context

{missing_context_lines}

### Structured Reasoning

{reasoning_lines}
"""
