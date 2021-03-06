from overlay_maintain_tools.fs_utils import *
from tests.utils import create_ebuild
from pathlib import Path
import pytest

overlay_dir = Path("/var/db/repos/gentoo")
test_atom = "sys-apps/portage"


def test_get_atomname():
    assert get_atomname(overlay_dir / test_atom) == test_atom


def test_get_pkg_name_from_atom():
    assert get_pkg_name_from_atom(test_atom) == "portage"


def test_contains_ebuild_files():
    assert contains_ebuild_files(overlay_dir / test_atom)
    assert not contains_ebuild_files(overlay_dir / "profiles")


def test_get_versions(tmp_path, create_pkgdir):
    tested_versions = ["1", "9999"]
    for ver in tested_versions:
        create_ebuild(create_pkgdir, ver)

    assert sorted(get_versions(create_pkgdir)) == sorted(tested_versions)


@pytest.mark.parametrize("ver", ["1", "1-r1"])
def test_get_version_from_file(create_pkgdir, ver):
    filename = create_ebuild(create_pkgdir, ver)
    assert get_version_from_file(filename) == "1"


def test_find_ebuilds_in_dir(create_pkgdir):
    filename = create_ebuild(create_pkgdir, "1")
    assert find_ebuilds_in_dir(create_pkgdir) == [filename]


def test_get_short_description(create_pkgdir):
    filename = create_ebuild(create_pkgdir)
    test_desc = "Some description"
    filename.write_text(f"DESCRIPTION={test_desc}")
    assert get_short_description(create_pkgdir) == test_desc


def test_get_long_description(create_pkgdir, setup_metadata):
    assert (
        get_long_description(create_pkgdir)
        == "Long description line 1.\nLong description line 2."
    )


def test_get_upstreams(create_pkgdir, setup_metadata):
    assert get_upstreams(create_pkgdir) == [
        ("account/reponame", "github"),
        ("somepypi", "pypi"),
    ]
