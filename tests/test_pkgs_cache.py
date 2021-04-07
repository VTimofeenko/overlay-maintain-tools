import pytest
from tests.utils import create_ebuild
from pathlib import Path

import overlay_maintain_tools.pkgs_cache as pc


@pytest.mark.parametrize("has_ebuild,result", ((True, ""), (False, None)))
def test_process_directory(has_ebuild, result, monkeypatch, create_pkgdir):
    if has_ebuild:
        create_ebuild(create_pkgdir)
    if result is not None:
        result = pc.Package(create_pkgdir, "", ["1"], [], "", "")

    monkeypatch.setattr(pc, "get_atomname", lambda _: "")
    monkeypatch.setattr(pc, "get_versions", lambda _: ["1"])
    monkeypatch.setattr(pc, "get_upstreams", lambda _: ("", ""))
    monkeypatch.setattr(pc, "get_short_description", lambda _: "")
    monkeypatch.setattr(pc, "get_long_description", lambda _: "")
    assert pc.process_directory(create_pkgdir) == result

    if result is not None:
        # check exception handling
        def _raise(_):
            raise Exception

        monkeypatch.setattr(pc, "get_atomname", _raise)

        # Suppress stderr printing
        class NullWriter:
            def write(self, s):
                pass

        monkeypatch.setattr(pc, "stderr", NullWriter())
        # Make sure that no exception is raised, None is returned.
        assert pc.process_directory(create_pkgdir) is None


@pytest.mark.parametrize("iterable,result", (([0, 1, 2, None, 3, False], [1, 2, 3]),))
def test_compact(iterable, result):
    assert list(pc.compact(iterable)) == result


def mock_process_directory(directory: Path):
    """To be used for multiprocessing, requires to be defined on module level"""
    return f"{directory.parent.name}/{directory.name}"


def test_build_pkgs_cache(tmp_path, monkeypatch, create_pkgdir):
    monkeypatch.setattr(pc, "process_directory", mock_process_directory)
    assert pc.build_pkgs_cache(tmp_path / "repo") == ["app-misc/pkgname"]


def test_build_pkgs_cache_alphabetical(tmp_path, monkeypatch, create_pkgdir):
    monkeypatch.setattr(pc, "process_directory", mock_process_directory)
    (tmp_path / "repo/app-misc/zzz_pkgname").mkdir(parents=True)
    (tmp_path / "repo/zzz-app/zzz_pkgname").mkdir(parents=True)
    assert pc.build_pkgs_cache(tmp_path / "repo") == [
        "app-misc/pkgname",
        "app-misc/zzz_pkgname",
        "zzz-app/zzz_pkgname",
    ]


def test_remote_link():
    r = pc.Remote("github", "gentoo-mirror/gentoo")
    assert r.remote_link() == "https://github.com/gentoo-mirror/gentoo"
    r = pc.Remote("pypi", "typer")
    assert r.remote_link() == "https://pypi.org/project/typer"
    r = pc.Remote("something else", "typer")
    with pytest.raises(NotImplementedError):
        r.remote_link()


def test_package(tmp_path):
    p = pc.Package(
        directory=tmp_path,
        atomname="app-misc/someatomname",
        versions=["1"],
        remotes=[],
        description="short desc",
        longdescription="some long desc",
    )

    # Just check that it exists
    assert hash(p)
