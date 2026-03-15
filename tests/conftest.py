from __future__ import annotations

import json
from pathlib import Path

import pytest


FIXTURE_ROOT = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_root() -> Path:
    return FIXTURE_ROOT


def load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
