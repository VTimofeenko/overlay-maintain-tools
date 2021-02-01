from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from multiprocessing import Pool
from overlay_maintain_tools.fs_utils import *
from toolz import merge_with, compose, filter


@dataclass
class Remote:
    type: str  # corresponds to 'type' value of metadata.xml
    target: str  # corresponds to the value of remote-id tag


@dataclass
class Package:
    """Contains parsed information from an atom directory"""
    directory: Path
    atomname: str
    versions: List[str]  # parsed version strings from ebuild filenames
    remotes: List[Remote]
    description: str  # short description from ebuild file
    longdescription: str  # corresponds to longdescription from metadata.xml


def process_directory(directory: Path):
    if contains_ebuild_files(directory):
        return Package(
            directory=directory,
            atomname=get_atomname(directory),
            versions=sorted(get_versions(directory)),
            remotes=[Remote(target=_[0], type=_[1]) for _ in get_upstreams(directory) if len(_) == 2],
            description=get_short_description(directory),
            longdescription=get_long_description(directory)
        )


def compact(_iter):
    return filter(None, _iter)


def build_pkgs_cache(overlay_dir: Path, worker_count=8,) -> List[Package]:
    pkg_subdirs = overlay_dir.glob("*/*")
    p = Pool(worker_count)
    return list(compact(p.map(process_directory, pkg_subdirs)))
