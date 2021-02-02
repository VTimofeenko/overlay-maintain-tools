import pytest
from tests.utils import tmp_repo, tmp_package


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


@pytest.fixture(scope="function")
def create_pkgdir(tmp_path):
    pkg_dir = tmp_path / f"{tmp_repo}/{tmp_package}"
    pkg_dir.mkdir(parents=True)
    return pkg_dir


@pytest.fixture(scope="function")
def setup_metadata(create_pkgdir):
    metadata = create_pkgdir / "metadata.xml"
    metadata.write_text(test_metadata)
    return metadata
