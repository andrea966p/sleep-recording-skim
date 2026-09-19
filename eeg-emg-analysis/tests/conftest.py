"""Let pytest run the suites that were written as standalone scripts.

Every test file here has a `main()` and is normally run directly:

    PYTHONPATH=. python3 tests/test_strip_channels.py

`test_strip_channels.py` additionally names its cases `test_*`, so pytest
collects them -- and then fails all twelve with `fixture 'tmp' not found`,
because `main()` passes that directory in by hand. The suite is fine; only the
pytest view of it was broken, and a collection error looks exactly like a broken
stripper to anyone who runs `pytest tests/`. That misread cost real time on
2026-09-19.

This supplies the missing fixture so BOTH invocations work and agree.
"""
from pathlib import Path

import pytest


@pytest.fixture
def tmp(tmp_path: Path) -> Path:
    """The scratch directory the script runner builds with tempfile.mkdtemp."""
    return tmp_path
