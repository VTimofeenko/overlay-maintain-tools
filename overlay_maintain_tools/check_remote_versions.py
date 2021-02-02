from typer import secho, colors, style, Exit
from typing import Tuple, Callable, Dict

from overlay_maintain_tools.main_helpers import no_write
from overlay_maintain_tools.pkgs_cache import Package, Remote


def print_remote(tup: Tuple[Remote, str]) -> str:
    """Checks a tuple with remote and version and produces it in a printable format"""
    return f"Version {tup[1]} available in remote {tup[0].type}:{tup[0].target}\nLink: {tup[0].remote_link()}"


def print_one_package_remote(remote: Remote) -> str:
    return f"Remote in metadata: {remote.type}: {remote.remote_link()}"


def print_all_package_remotes(pkg: Package) -> str:
    if len(pkg.remotes) > 0:
        return "\n".join(tuple(map(print_one_package_remote, pkg.remotes)))
    else:
        return "No remotes specified. Consider adding them in metadata.xml"


def print_version_header(
    color: bool, remotes_with_new_versions: Tuple[Tuple[Remote, str], ...]
) -> str:
    new_version_available = "New version available"
    no_new_version = "No newer versions available"
    if color:
        new_version_available = style(new_version_available, fg=colors.RED)
        no_new_version = style(no_new_version, fg=colors.GREEN)

    if len(remotes_with_new_versions) >= 1:
        remotes_with_versions = "\n".join(
            list(map(print_remote, remotes_with_new_versions))
        )
        return f"{new_version_available}\n{remotes_with_versions}"
    else:
        return f"{no_new_version}"


def print_package(
    pkg: Package,
    remotes_with_new_versions: Tuple[Tuple[Remote, str], ...],
    color: bool,
) -> str:
    """Produces a printable version of a Package with remotes_with_new_versions"""

    if color:
        pkg_name = style(pkg.atomname, bold=True)
    else:
        pkg_name = pkg.atomname

    existing_versions_string = f"Versions in overlay: {', '.join(pkg.versions)}"

    return f"""{pkg_name}: {print_version_header(color, remotes_with_new_versions)}
{existing_versions_string}
{print_all_package_remotes(pkg)}"""


def check_versions_short_circuit(
    pkgs_with_versions: Dict[Package, Tuple[Tuple[Remote, str], ...]]
) -> Exit:
    """Checks if there are any non-empty remotes, and returns the exit code status"""
    if any(map(lambda _: len(_) > 0, pkgs_with_versions.values())):
        return Exit(100)
    else:
        return Exit(0)
