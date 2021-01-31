from typing import List, Union
import re
import requests
from enum import Enum
from operator import methodcaller

from overlay_maintain_tools.pkgs_cache import Package, Remote

live_version = re.compile(r"^9999+$")


def _cleanup_version(version: str) -> str:
    """Does some primitive cleanup of version string
    :type version: str, a version string from upstream
    :return version normalized to ebuild file name convention
    """
    return version[1:] if version.startswith("v") else version


def _is_live_version(version: str) -> bool:
    return bool(live_version.match(version))


def _get_latest_version_from_github(target: str) -> Union[str, None]:
    reply = requests.get(f"https://github.com/{target}/releases/latest")
    reply.raise_for_status()
    version_reply = reply.url.split("/")[-1]
    if version_reply == "releases":
        return None
    elif version_reply == "latest":
        raise Exception(
            "Does not look like a GitHub repository. Please check the project name."
        )
    else:
        return _cleanup_version(version_reply)


def _get_latest_version_from_pypi(pkgname: str) -> Union[str, None]:
    reply = requests.get(f"https://pypi.org/pypi/{pkgname}/json")
    reply.raise_for_status()
    return reply.json()["info"]["version"]


version_getter = {
    "github": _get_latest_version_from_github,
    "pypi": _get_latest_version_from_pypi,
}


def get_latest_version_from_remote(r: Remote) -> str:
    version = version_getter[r.type](r.target)
    return _cleanup_version(version)


def process_list(packages_stash: List[Package]):
    # versions list
    for pkg in packages_stash:
        versions_local = filter(_is_live_version, pkg.versions)
        versions_in_remotes = map(get_latest_version_from_remote, pkg.remotes)
    pass
