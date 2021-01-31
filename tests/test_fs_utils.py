from overlay_maintain_tools.fs_utils import *
from pathlib import Path
import pytest

overlay_dir = Path("/var/db/repos/gentoo")
test_atom = 'sys-apps/portage'
tmp_repo = 'repo'
tmp_package = 'app-misc/pkgname'
test_metadata = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE pkgmetadata SYSTEM "http://www.gentoo.org/dtd/metadata.dtd">
<pkgmetadata>
<maintainer type="person">
    <email>someone@example.org</email>
    <description>Example overlay</description>
</maintainer>
    <longdescription lang="en">
        Long description line 1.
        
        Long description line 2.
    </longdescription>
    <upstream>
        <remote-id type="github">account/reponame</remote-id>
        <remote-id type="pypi">somepypi</remote-id>
    </upstream>
<use>
</use>
</pkgmetadata>"""


def test_get_atomname():
    assert get_atomname(overlay_dir / test_atom) == test_atom


def test_get_pkg_name_from_atom():
    assert get_pkg_name_from_atom(test_atom) == 'portage'


def test_contains_ebuild_files():
    assert contains_ebuild_files(overlay_dir / test_atom)
    assert not contains_ebuild_files(overlay_dir / 'profiles')


@pytest.fixture(scope="function")
def create_pkgdir(tmp_path):
    pkg_dir = tmp_path / f"{tmp_repo}/{tmp_package}"
    pkg_dir.mkdir(parents=True)
    return pkg_dir


def create_ebuild(pkgdir: Path, version: str = '1') -> Path:
    filename = (pkgdir / f'pkgname-{version}.ebuild')
    filename.touch()
    return filename


def test_get_versions(tmp_path, create_pkgdir):
    tested_versions = ["1", "9999"]
    for ver in tested_versions:
        create_ebuild(create_pkgdir, ver)

    assert sorted(get_versions(create_pkgdir)) == sorted(tested_versions)


@pytest.mark.parametrize('ver', ["1", "1-r1"])
def test_get_version_from_file(create_pkgdir, ver):
    filename = create_ebuild(create_pkgdir, ver)
    assert get_version_from_file(filename) == "1"


def test_find_ebuilds_in_dir(create_pkgdir):
    filename = create_ebuild(create_pkgdir, '1')
    assert find_ebuilds_in_dir(create_pkgdir) == [filename]


def test_get_short_description(create_pkgdir):
    filename = create_ebuild(create_pkgdir)
    test_desc = "Some description"
    filename.write_text(f"DESCRIPTION={test_desc}")
    assert get_short_description(create_pkgdir) == test_desc


def test_get_long_description(create_pkgdir):
    metadata = create_pkgdir / "metadata.xml"
    metadata.write_text(test_metadata)
    assert get_long_description(create_pkgdir) == "Long description line 1.\nLong description line 2."


def test_get_upstreams(create_pkgdir):
    metadata = create_pkgdir / "metadata.xml"
    metadata.write_text(test_metadata)
    assert get_upstreams(create_pkgdir) == [('account/reponame', 'github'), ('somepypi', 'pypi')]
