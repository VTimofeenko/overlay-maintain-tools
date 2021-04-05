import pytest
import requests

import overlay_maintain_tools.repology.main as rm

my_test_atom = "app-misc/test"
my_test_project_name = "repo_test"


@pytest.fixture(scope="function")
def setup_cache(tmp_path):
    cache_path = tmp_path / "repology_cache"
    cache_path.write_text(f"{my_test_atom} {my_test_project_name}")
    return cache_path


@pytest.fixture(scope="function")
def create_cache(setup_cache):
    return rm.load_repology_cache(setup_cache)


def test_load_repology_cache(setup_cache):
    _ = rm.load_repology_cache(setup_cache)
    assert my_test_atom in _


def test_load_repology_cache_failure(tmp_path):
    cache_path = tmp_path / "repology_cache"
    cache_path.write_text("app-misc/test_repo_test")
    with pytest.raises(ValueError):
        _ = rm.load_repology_cache(cache_path)


def test__get_repology_name_for_pkg(create_cache):
    assert (
        rm._get_repology_name_for_pkg(my_test_atom, create_cache)
        == my_test_project_name
    )


@pytest.fixture(scope="function")
def monkeypatch_repology(monkeypatch):
    class MockRepologyResponse:
        def __init__(self, versions):
            self.raise_for_status = lambda: ""
            self.json = lambda: [{"version": _, "status": "newest"} for _ in versions]

    def f(versions):
        # noinspection PyUnusedLocal
        def mock_get(*args, **kwargs):
            return MockRepologyResponse(versions=versions)

        monkeypatch.setattr(requests, "get", mock_get)

    return f


def test__get_versions_from_repology_repos(monkeypatch_repology):
    my_versions = ["1", "2"]
    monkeypatch_repology(my_versions)
    assert rm._get_versions_from_repology_repos(my_test_atom) == set(my_versions)


@pytest.mark.parametrize("pkgname", [my_test_atom, "nonexistent_package"])
def test_get_higher_versions_in_repology_general(
    pkgname, create_cache, monkeypatch_repology
):
    """Tests that the function runs in general"""

    monkeypatch_repology(
        [
            "1",
        ]
    )

    class Package:
        def __init__(self, atomname):
            self.atomname = atomname
            self.versions = ["1"]

    rm.get_higher_versions_in_repology(Package(pkgname), create_cache)


@pytest.mark.parametrize(
    "versions",
    [
        (("1", "2-r1", "9999"), ("3",)),
        (("9999",), ("1", "2", "3")),
        (("2",), ("3",)),
        (("3",), tuple()),
    ],
    ids=(
        "Real package",
        "Only live version",
        "Only one version, there are updates in remotes",
        "Only one version, no updates in remotes",
    ),
)
def test_get_higher_versions_in_repology_versions(
    versions, monkeypatch_repology, create_cache
):
    package_versions, remote_versions = versions

    monkeypatch_repology(map(str, range(1, 4)))

    class Package:
        def __init__(self):
            self.atomname = my_test_atom
            self.versions = package_versions

    _ = rm.get_higher_versions_in_repology(Package(), create_cache)
    assert sorted(_) == sorted(remote_versions)
