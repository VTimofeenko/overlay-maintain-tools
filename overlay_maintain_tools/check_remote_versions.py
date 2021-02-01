from typer import secho, colors, style
from typing import Tuple, Callable

from overlay_maintain_tools.main_helpers import no_write
from overlay_maintain_tools.pkgs_cache import Package, Remote
from overlay_maintain_tools.main import print_stdout


def print_remote(tup: Tuple[Remote, str]):
    """Checks a tuple with remote and version and produces it in a printable format"""
    return f"Version {tup[1]} available in remote {tup[0].type}:{tup[0].target}\nLink: {tup[0].remote_link()}"


def print_package(
    pkg: Package,
    remotes: Tuple[Tuple[Remote, str], ...],
    color: bool,
) -> str:

    new_version_available = "New version available"
    no_new_version = "No newer versions available"

    if color:
        pkg_name = style(pkg.atomname, bold=True)
        new_version_available = style(new_version_available, fg=colors.RED)
        no_new_version = style(no_new_version, fg=colors.GREEN)
    else:
        pkg_name = pkg.atomname

    if len(remotes) >= 1:
        remotes_output = "\n".join(list(map(print_remote, remotes)))
        pkg_postfix = new_version_available
    else:
        pkg_postfix = no_new_version
        remotes_output = ""

    existing_versions_string = f"Versions on overlay: {', '.join(pkg.versions)}"

    return f"""{pkg_name}: {pkg_postfix}{remotes_output}
{existing_versions_string}"""
