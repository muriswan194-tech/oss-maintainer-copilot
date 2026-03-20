from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.github.events import (
    load_issue_envelope,
    load_pull_request_envelope,
    load_pull_request_summary_input,
    load_release_notes_input,
)


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def _load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_loads_plain_issue_payload(fixture_root: Path) -> None:
    envelope = load_issue_envelope(_fixture(fixture_root, "issues/simple_docs_issue.json"))

    assert envelope.issue.number == 14
    assert envelope.issue.title == "Clarify README setup steps for Windows contributors"
    assert envelope.action is None


def test_loads_github_issue_event_payload(fixture_root: Path) -> None:
    envelope = load_issue_envelope(_fixture(fixture_root, "issues/complex_migration_event.json"))

    assert envelope.action == "opened"
    assert envelope.repository is not None
    assert envelope.repository.full_name == "octo-org/oss-maintainer-copilot"
    assert envelope.issue.number == 87


def test_loads_pull_request_event_payload(fixture_root: Path) -> None:
    envelope = load_pull_request_envelope(_fixture(fixture_root, "pulls/pr_event_payload.json"))

    assert envelope.action == "opened"
    assert envelope.pull_request.number == 42
    assert envelope.repository is not None
    assert envelope.repository.full_name == "octo-org/oss-maintainer-copilot"


def test_loads_pull_request_summary_input_from_event_payload(fixture_root: Path) -> None:
    summary_input = load_pull_request_summary_input(_fixture(fixture_root, "pulls/pr_event_payload.json"))

    assert summary_input.title == "Add structured issue triage output models"
    assert summary_input.labels == ["automation", "triage"]
    assert len(summary_input.changed_file_paths) == 3
    assert len(summary_input.commit_messages) == 2


def test_loads_release_notes_input(fixture_root: Path) -> None:
    release_input = load_release_notes_input(_fixture(fixture_root, "releases/release_window_mixed.json"))

    assert release_input.version_range.previous == "v0.2.0"
    assert release_input.version_range.current == "v0.3.0"
    assert len(release_input.merged_pull_requests) == 5
