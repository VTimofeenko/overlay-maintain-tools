from pathlib import Path
from portage.xml.metadata import MetaDataXML
from typing import List, Tuple
import logging
from dotenv import dotenv_values
import re


def get_atomname(pkg_dir: Path) -> str:
    """Takes full path to pkg_dir and returns two last parents"""
    return str(pkg_dir.relative_to(pkg_dir.parent.parent))


def get_pkg_name_from_atom(atom_name: str) -> str:
    return atom_name.split("/")[-1]


def contains_ebuild_files(pkg_dir: Path) -> bool:
    return any(map(lambda obj: obj.exists(), pkg_dir.glob("*.ebuild")))


def get_version_from_file(ebuild_file: Path) -> str:
    """Gets version from ebuild files passed as relative path"""
    atom_name = str(ebuild_file.parent)
    pkg_name = get_pkg_name_from_atom(atom_name)

    # get X.X.X-rX version
    _version = (
        str(ebuild_file).replace(f"{atom_name}/{pkg_name}-", "").replace(".ebuild", "")
    )
    # strip -rX revision
    return re.sub("-r[0-9]+$", "", _version)


def find_ebuilds_in_dir(pkg_dir: Path) -> List[Path]:
    return list(pkg_dir.glob("*.ebuild"))


def get_versions(pkg_dir: Path) -> List[str]:
    return [
        get_version_from_file(ebuild_file)
        for ebuild_file in find_ebuilds_in_dir(pkg_dir)
    ]


def get_short_description(pkg_dir: Path) -> str:
    # Note: assumes all descriptions are the same
    ebuild_file = find_ebuilds_in_dir(pkg_dir)[0]
    # suppress warnings for "Could not read the file". Ugly but works.
    logging.getLogger("dotenv").setLevel(logging.ERROR)
    return dotenv_values(ebuild_file)["DESCRIPTION"]


def get_long_description(pkg_dir: Path) -> str:
    pkg_md = MetaDataXML(str(pkg_dir / "metadata.xml"), "")
    longdescription = ""
    for desc in pkg_md.descriptions():
        longdescription += (
            "".join(list(map(lambda s: s.strip() + " ", desc.split("\n"))))
              .strip()
              .replace("  ", "\n")
        )
    return longdescription


def get_upstreams(pkg_dir: Path) -> List[Tuple]:
    pkg_md = MetaDataXML(str(pkg_dir / "metadata.xml"), "")
    result = []
    if upstream := pkg_md.upstream():
        for remote in upstream[0].remoteids:
            result += [remote]
    return result
