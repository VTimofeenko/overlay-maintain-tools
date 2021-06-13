from pathlib import Path
from typing import Optional, List, Dict
import typer
import re
from pprint import pprint
from dotenv import dotenv_values
import logging
import requests
from functools import partial

from overlay_maintain_tools.mkreadme import setup_template, render_template
from overlay_maintain_tools.pkgs_cache import build_pkgs_cache
from overlay_maintain_tools.version_utils import check_pkg_remotes
from overlay_maintain_tools.main_helpers import State, no_write
from overlay_maintain_tools.check_remote_versions import (
    print_package,
    check_versions_short_circuit,
)

__version__ = "1.2.0"
app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(f"Overlay maintain tools version: {__version__}")
        raise typer.Exit()


@app.command()
def mkreadme(
    ctx: typer.Context,
    skeleton_file: Path = typer.Option(
        None,
        help="The file containing README template. Should be inside the template directory.",
    ),
    template_dir: Optional[Path] = typer.Option(
        None,
        help="Template directory. Can be specified if more complex jinja2 templates will be used.",
        file_okay=False,
        dir_okay=True,
        exists=True,
    ),
    readme: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the resulting README. If not supplied - print to stdout.",
    ),
):
    """Creates a README for an overlay. The generated README can utilize data on packages
    available in the overlay and their versions. For sample template, see the documentation."""
    template = setup_template(skeleton_template=skeleton_file, search_path=template_dir)
    text = render_template(packages_stash=ctx.obj.pkg_cache, template=template)
    if readme is None:
        typer.echo(text)
    else:
        readme.write_text(text)


@app.command()
def check_remote_versions(
    ctx: typer.Context,
    show_updates_only: Optional[bool] = typer.Option(
        False,
        "--show-updates-only",
        help="Shows only packages that have updates with links to remotes_with_new_versions.",
        show_default=False,
    ),
    background: Optional[bool] = typer.Option(
        False,
        "--background",
        help="Suppress output of this subcommand completely. Exit code = 100 denotes that there are updates in remotes",
        show_default=False,
        show_choices=False,
    ),
    color: Optional[bool] = typer.Option(
        True, "--color", help="Enable/disable color in output", show_default=False
    ),
):
    """Prints report on the versions of packages. Checks versions available upstream.
    Pulls the data from remotes specified inside <upstream> tag in metadata.xml"""
    pkg_cache = ctx.obj.pkg_cache
    _check_pkg_remotes = partial(check_pkg_remotes, worker_count=ctx.obj.worker_count)

    for (pkg, remote_versions) in zip(pkg_cache, map(_check_pkg_remotes, pkg_cache)):
        # short-circuit if background and remote versions exist
        if remote_versions and background:
            raise typer.Exit(100)

        if (show_updates_only and len(remote_versions) == 0) or background:
            print_func = no_write
        else:
            print_func = ctx.obj.print_stdout

        print_func(
            print_package(
                pkg=pkg, remotes_with_new_versions=remote_versions, color=color
            )
        )


@app.command()
def check_repology(
    ctx: typer.Context,
    repology_cache_location: Optional[Path] = typer.Option(
        None,
        help="Path to file with the mappings between overlay package and repology project",
        file_okay=True,
        dir_okay=True,
        exists=True,
    ),
):
    """Returns versions known to repology. Reported versions will be newer than ones in overlay."""
    from overlay_maintain_tools.repology import (
        get_higher_versions_in_repology,
        load_repology_cache,
    )

    print_func = ctx.obj.print_stdout
    get_higher_versions_in_repology = partial(
        get_higher_versions_in_repology,
        repology_cache=load_repology_cache(repology_cache_location),
    )

    print_func("Repology report:")

    pkg_cache = ctx.obj.pkg_cache
    for (pkg, reply) in zip(pkg_cache, map(get_higher_versions_in_repology, pkg_cache)):
        if reply:
            reply_i = tuple(reply)
            if reply_i and ctx.obj.quiet:
                raise typer.Exit(100)
            print_func(
                f"{pkg.atomname}:\nHave locally: {', '.join(pkg.versions)}\n"
                f"Versions in repology greater than ones in overlay: {''.join(reply_i)}"
            )


# noinspection PyUnusedLocal
@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    overlay_dir: Optional[Path] = typer.Option(
        ".", "--overlay-dir", help="Specify location for overlay."
    ),
    worker_count: int = typer.Option(
        8, min=1, help="Number of workers for creating package cache."
    ),
    quiet: Optional[bool] = typer.Option(
        False,
        "--quiet",
        help="Suppresses output. For commands checking versions exit code 100 means newer versions are available.",
    ),
):
    """Provides certain tools to be run on the overlay directory. See individual commands help for details."""
    state = State()
    ctx.obj = state
    if overlay_dir != ".":
        state.overlay_dir = Path(overlay_dir).absolute()

    state.quiet = quiet or (ctx.invoked_subcommand == "mkreadme")

    state.print_stdout("Starting overlay-maintain-tools CLI")

    state.print_stdout(f"Building package cache from {str(overlay_dir)}.")
    state.pkg_cache = sorted(
        build_pkgs_cache(overlay_dir=overlay_dir, worker_count=worker_count),
        key=lambda _: _.atomname,
    )
    state.print_stdout(f"Package cache built.")
    state.worker_count = worker_count


if __name__ == "__main__":
    app()  # pragma: no cover
