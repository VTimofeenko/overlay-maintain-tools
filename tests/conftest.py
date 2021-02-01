import pytest
from tests.utils import tmp_repo, tmp_package


@pytest.fixture(scope="function")
def create_pkgdir(tmp_path):
    pkg_dir = tmp_path / f"{tmp_repo}/{tmp_package}"
    pkg_dir.mkdir(parents=True)
    return pkg_dir
