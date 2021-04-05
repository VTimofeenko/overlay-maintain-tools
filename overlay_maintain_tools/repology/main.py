import requests
from typing import Optional, Callable, Tuple, Iterable
from libversion import Version, version_compare
from functools import partial
from toolz import complement, compose
from toolz.curried import pluck
from pathlib import Path

from overlay_maintain_tools.pkgs_cache import Package, Remote
from overlay_maintain_tools.version_utils import _is_live_version, strip_revision


def load_repology_cache(file: Path) -> dict:
    result = {}
    with open(str(file), "r") as f:
        for line in f:
            try:
                key, val = line.split()
            except ValueError as e:
                import sys

                if "not enough values to unpack" in str(e):
                    raise ValueError(
                        str(e) + f". Line {line} does not have space"
                    ).with_traceback(sys.exc_info()[2])
                else:
                    raise e  # pragma: no cover

            result.update({key: val})

    return result


def _get_repology_name_for_pkg(atomname: str, cache: dict) -> Optional[str]:
    return cache.get(atomname, None)


def _get_versions_from_repology_repos(project: str) -> set:
    """Returns set of versions available in other repos of repology"""
    reply = requests.get(f"https://repology.org/api/v1/project/{project}")
    reply.raise_for_status()
    return set(
        pluck("version")(filter(lambda _: _["status"] == "newest", reply.json()))
    )


def get_higher_versions_in_repology(
    package: Package, repology_cache: dict
) -> Optional[Iterable]:
    """Returns all versions from repology which are higher than the ones in package.

    If the package is not in repology cache - returns None"""
    repology_name = _get_repology_name_for_pkg(
        atomname=package.atomname, cache=repology_cache
    )
    if repology_name is None:
        return None

    my_versions = tuple(
        map(
            compose(Version, strip_revision),
            filter(complement(_is_live_version), package.versions),
        )
    )
    if my_versions:
        max_version = max(my_versions).value
        op = compose(lambda x: x < 0, partial(version_compare, max_version))
        return filter(op, _get_versions_from_repology_repos(repology_name))
    else:
        return _get_versions_from_repology_repos(repology_name)
