import pytest
import requests
from toolz.curried import get, pluck
from toolz import pipe, complement

import overlay_maintain_tools.version_utils as vu
from overlay_maintain_tools.pkgs_cache import Remote


class MockGitHubResponse:
    def __init__(self, target, version=None):
        self.raise_for_status = lambda: ""
        if "no-release" in target:
            self.url = f"https://github.com/{target}/releases"
        elif "no-project" in target:
            self.url = f"https://github.com/{target}/releases/latest"
        else:
            self.url = f"https://github.com/{target}/releases/tag/{version}"


class MockPyPiResponse:
    @staticmethod
    def _raise():
        raise requests.HTTPError

    def __init__(self, target, version=None):
        self.json = lambda: {"info": {"version": version}}
        self.raise_for_status = lambda: ""

        if "bad-url" in target:
            self.raise_for_status = self._raise


@pytest.fixture(scope="function")
def monkeypatch_github_response(monkeypatch):
    def f(target, version):
        # noinspection PyUnusedLocal
        def mock_get(*args, **kwargs):
            return MockGitHubResponse(target=target, version=version)

        monkeypatch.setattr(requests, "get", mock_get)

    return f


@pytest.fixture(scope="function")
def monkeypatch_pypi_response(monkeypatch):
    def f(target, version):
        # noinspection PyUnusedLocal
        def mock_get(*args, **kwargs):
            return MockPyPiResponse(target=target, version=version)

        monkeypatch.setattr(requests, "get", mock_get)

    return f


def test__is_live_version():
    assert vu._is_live_version("1") is False
    assert vu._is_live_version("9999")


@pytest.mark.parametrize("version_string", ["v1", "1"])
def test__cleanup_version(version_string):
    assert vu._cleanup_version(version_string) == "1"


@pytest.mark.parametrize(
    "target,version",
    [("user/some-package", "1"), ("user/no-release-package", None)],
)
def test__get_latest_version_from_github(target, version, monkeypatch_github_response):
    monkeypatch_github_response(target, version)
    assert vu._get_latest_version_from_github(target) == version


def test__get_latest_version_from_github_bad(monkeypatch_github_response):
    target = "no-project"
    monkeypatch_github_response(target, 1)
    with pytest.raises(Exception):
        vu._get_latest_version_from_github(target)


@pytest.mark.parametrize(
    "target,version,result",
    [("user/some-package", "1", "1"), ("no-release-package", None, "")],
)
def test_get_latest_version_from_remote(
    target, version, result, monkeypatch_github_response
):
    monkeypatch_github_response(target, version)
    r = Remote(type="github", target=target)
    assert vu.get_latest_version_from_remote(r) == result


@pytest.mark.parametrize(
    "target,version",
    [("some-package", "1"), ("bad-url-package", None)],
)
def test__get_latest_version_from_pypi(target, version, monkeypatch_pypi_response):
    monkeypatch_pypi_response(target, version)
    if "bad-url" in target:
        with pytest.raises(requests.HTTPError):
            vu._get_latest_version_from_pypi("confluence_poster")
    else:
        assert vu._get_latest_version_from_pypi(target) == version


@pytest.mark.parametrize("target,version", [("user/some-package", "1")])
def test_process_remotes_list(target, version, monkeypatch_github_response):
    monkeypatch_github_response(target, version)
    r = Remote(type="github", target=target)
    assert vu.process_remotes_list((r,), 8) == ((r, version),)


@pytest.mark.parametrize(
    "local_versions,remotes,result",
    (
        (
            ("0.1", "0.2", "9999"),
            ((Remote("github", "user/some-package"), "1"),),
            ((Remote("github", "user/some-package"), "1"),),
        ),
        (
            ("0.1", "0.2", "9999"),
            (
                (Remote("github", "user/some-package"), "1"),
                (Remote("pypi", "some-package"), "1"),
            ),
            (
                (Remote("github", "user/some-package"), "1"),
                (Remote("pypi", "some-package"), "1"),
            ),
        ),
        (
            ("1", "9999"),
            (
                (Remote("github", "user/some-package"), "1"),
                (Remote("pypi", "some-package"), "1"),
            ),
            (),
        ),
    ),
    ids=(
        "Version 1 available in github, higher than the ones in overlay",
        "Version 1 available in both github and pypi, higher than the ones in overlay",
        "The latest version from both github and pypi are available in overlay",
    ),
)
def test_compare_local_remote_versions(local_versions, remotes, result, monkeypatch):
    for remote in remotes:
        monkeypatch.setitem(
            vu.version_getter,
            remote[0].type,
            lambda _: remote[1],
        )

    assert (
        vu.compare_local_remote_versions(
            local_versions=local_versions,
            remotes=tuple(pipe(remotes, pluck(0))),
            worker_count=8,
        )
        == result
    )


@pytest.mark.parametrize(
    "local_versions,remote_versions,result",
    (
        (
            {"pkg1": ("0.1", "0.2", "9999"), "pkg2": ("1",)},
            {"pkg1": ((Remote("github", "user/some-package"), "1"),), "pkg2": ()},
            {"pkg1": ((Remote("github", "user/some-package"), "1"),), "pkg2": ()},
        ),
        (
            {"pkg1": ("1", "9999"), "pkg2": ("1",)},
            {
                "pkg1": ((Remote("github", "user/some-package"), "2"),),
                "pkg2": ((Remote("github", "user/some-package"), "2"),),
            },
            {
                "pkg1": ((Remote("github", "user/some-package"), "2"),),
                "pkg2": ((Remote("github", "user/some-package"), "2"),),
            },
        ),
        (
            {"pkg1": ("1", "9999"), "pkg2": ("1",)},
            {"pkg1": ((Remote("github", "user/some-package"), "1"),), "pkg2": ()},
            {"pkg1": (), "pkg2": ()},
        ),
    ),
    ids=(
        "One package has a newer version, other does not",
        "Both packages have a newer version",
        "Neither packages have a newer version",
    ),
)
def test_process_pkgs(local_versions, remote_versions, result, monkeypatch):
    # noinspection PyUnusedLocal
    def _compare(versions, remotes, count):
        versions = set(filter(complement(vu._is_live_version), versions))
        if remotes == () or (max(versions) >= max(pipe(remotes, pluck(1), tuple))):
            return ()
        else:
            return remotes

    monkeypatch.setattr(vu, "compare_local_remote_versions", _compare)

    class Package:
        def __init__(self, atomname, versions, remotes):
            self.atomname = atomname
            self.versions = versions
            self.remotes = remotes

        def __hash__(self):
            return hash(self.atomname)

        def __eq__(self, other):
            return hash(self) == hash(other)

    pkg_stash = [
        Package(_, local_versions[_], remote_versions[_]) for _ in local_versions.keys()
    ]

    assert vu.process_pkgs(pkg_stash) == result
