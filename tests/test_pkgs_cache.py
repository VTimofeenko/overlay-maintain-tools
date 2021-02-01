import pytest
from tests.utils import create_ebuild

import overlay_maintain_tools.pkgs_cache as pc


@pytest.mark.parametrize("has_ebuild,result", ((True, ""), (False, None)))
def test_process_directory(has_ebuild, result, monkeypatch, create_pkgdir):
    if has_ebuild:
        create_ebuild(create_pkgdir)
    if result is not None:
        result = pc.Package(create_pkgdir, '', ['1'], [], '', '')
    monkeypatch.setattr(pc, 'get_atomname', lambda _: "")
    monkeypatch.setattr(pc, 'get_versions', lambda _: ["1"])
    monkeypatch.setattr(pc, 'get_upstreams', lambda _: ("", ""))
    monkeypatch.setattr(pc, 'get_short_description', lambda _: "")
    monkeypatch.setattr(pc, 'get_long_description', lambda _: "")
    assert pc.process_directory(create_pkgdir) == result


@pytest.mark.parametrize("iterable,result", (([0, 1, 2, None, 3, False], [1, 2, 3]),))
def test_compact(iterable, result):
    assert list(pc.compact(iterable)) == result


def mock_process_directory(_):
    """To be used for multiprocessing, requires to be defined on module level"""
    return "pkg"


def test_build_pkgs_cache(tmp_path, monkeypatch, create_pkgdir):
    monkeypatch.setattr(pc, 'process_directory', mock_process_directory)
    assert pc.build_pkgs_cache(tmp_path) == ["pkg"]
