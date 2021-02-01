from pathlib import Path

import overlay_maintain_tools.main_helpers as mh


def test_state():
    s = mh.State()
    assert s.overlay_dir == Path.cwd()
    assert s.pkg_cache == []


def test_no_write(capsys):
    """Checks that there is no output for no write function. It should mimic the typer.echo"""
    mh.no_write("Some output")
    mh.no_write("Some output", err=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
