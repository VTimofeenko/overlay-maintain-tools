from typing import List, Union, Tuple, Dict, Iterable
from collections.abc import Collection
import re
import requests
from enum import Enum
from operator import methodcaller, attrgetter
from toolz import complement, groupby, compose
from toolz.curried import get, pluck
from multiprocessing import Pool

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


def strip_revision(version: str) -> str:
    """Turns 2-r1 > 2, 2 > 2"""
    return re.sub(r"-r\d+", "", version)


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
    if version is None:
        version = ""
    return _cleanup_version(version)


def process_remotes_list(
    remotes: Iterable[Remote], worker_count: int
) -> Tuple[Tuple[Remote, str], ...]:
    """Retrieves the versions from remotes_with_new_versions"""
    p = Pool(worker_count)
    remote_versions = p.map(get_latest_version_from_remote, remotes)
    return tuple(zip(remotes, remote_versions))


def compare_local_remote_versions(
    local_versions: Iterable[str],
    remotes: Iterable[Remote],
    worker_count: int,
) -> Tuple[Tuple[Remote, str]]:
    """Returns the list of remotes_with_new_versions with versions greater than the maximum local one"""
    max_version_local = max(
        set(filter(complement(_is_live_version), local_versions)), default=""
    )
    return tuple(
        filter(
            lambda _: _[1] > max_version_local,
            process_remotes_list(remotes, worker_count=worker_count),
        )
    )


def check_pkg_remotes(pkg: Package, worker_count: int = 8):
    try:
        return compare_local_remote_versions(pkg.versions, pkg.remotes, worker_count)
    except Exception as e:
        print(
            f"Could not process package '{pkg.atomname}', caught exception. This may be a bug.",
        )
        raise e
