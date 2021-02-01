from pathlib import Path

from overlay_maintain_tools.main_helpers import State


def test_state():
    s = State()
    assert s.overlay_dir == Path.cwd()
    assert s.pkg_cache == []
