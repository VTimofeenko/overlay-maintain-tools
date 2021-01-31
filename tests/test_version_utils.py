import pytest
import requests

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
    # noinspection PyUnusedLocal
    def f(target, version):
        def mock_get(*args, **kwargs):
            return MockGitHubResponse(target=target, version=version)

        monkeypatch.setattr(requests, "get", mock_get)

    return f


@pytest.fixture(scope="function")
def monkeypatch_pypi_response(monkeypatch):
    # noinspection PyUnusedLocal
    def f(target, version):
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


@pytest.mark.parametrize("target,version", [("user/some-package", "1")])
def test_get_latest_version_from_remote(target, version, monkeypatch_github_response):
    monkeypatch_github_response(target, version)
    r = Remote(type="github", target=target)
    assert vu.get_latest_version_from_remote(r) == version


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
