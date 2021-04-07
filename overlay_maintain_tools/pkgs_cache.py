from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from functools import total_ordering
from multiprocessing import Pool
from toolz import merge_with, compose, filter
from sys import stderr

from overlay_maintain_tools.fs_utils import *


@dataclass
class Remote:
    type: str  # corresponds to 'type' value of metadata.xml
    target: str  # corresponds to the value of remote-id tag

    def remote_link(self) -> str:
        """Produces a link to the remote."""
        if self.type == "github":
            return f"https://github.com/{self.target}"
        elif self.type == "pypi":
            return f"https://pypi.org/project/{self.target}"
        else:
            raise NotImplementedError(f"Remote {self.type} is not implemented")


@total_ordering
@dataclass
class Package:
    """Contains parsed information from an atom directory"""

    directory: Path
    atomname: str
    versions: List[str]  # parsed version strings from ebuild filenames
    remotes: List[Remote]
    description: str  # short description from ebuild file
    longdescription: str  # corresponds to longdescription from metadata.xml

    def __hash__(self):
        return hash(self.atomname)

    def __lt__(self, other):
        return self.atomname < other.atomname


def process_directory(directory: Path) -> Package:
    if contains_ebuild_files(directory):
        try:
            return Package(
                directory=directory,
                atomname=get_atomname(directory),
                versions=sorted(get_versions(directory)),
                remotes=[
                    Remote(target=_[0], type=_[1])
                    for _ in get_upstreams(directory)
                    if len(_) == 2
                ],
                description=get_short_description(directory),
                longdescription=get_long_description(directory),
            )
        except Exception as e:
            print(f"Could not process {directory}", file=stderr)
            print(f"Error: {e}", file=stderr)


def compact(_iter):
    return filter(None, _iter)


def build_pkgs_cache(
    overlay_dir: Path,
    worker_count=8,
) -> List[Package]:
    pkg_subdirs = overlay_dir.glob("*/*")
    p = Pool(worker_count)
    return sorted(list(compact(p.map(process_directory, pkg_subdirs))))
