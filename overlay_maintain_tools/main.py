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
from overlay_maintain_tools.version_utils import process_pkgs
from overlay_maintain_tools.main_helpers import State, no_write
from overlay_maintain_tools.check_remote_versions import (
    print_package,
    check_versions_short_circuit,
)

__version__ = "1.0"
app = typer.Typer()
state = State()


def version_callback(value: bool):
    if value:
        typer.echo(f"Overlay maintain tools version: {__version__}")
        raise typer.Exit()


@app.command()
def mkreadme(
    skeleton_file: Path = typer.Option(
        default="readme.skel.jinja2",
        help="The file containing README template. Should be inside the template directory.",
    ),
    template_dir: Path = typer.Option(
        default=".dev/docs",
        help="Template directory. Required by Jinja loader.",
        file_okay=False,
        dir_okay=True,
        exists=True,
    ),
    readme: Optional[Path] = typer.Option(
        None,
        "--readme-output",
        help="Where to save the resulting README. If not supplied - print to stdout.",
    ),
):
    template = setup_template(
        skeleton_template_name=str(skeleton_file), search_path=str(template_dir)
    )
    text = render_template(packages_stash=state.pkg_cache, template=template)
    if readme.is_file():
        readme.write_text(text)
    else:
        print_stdout(text)


@app.command()
def check_remote_versions(
    show_updates_only: Optional[bool] = typer.Option(
        False,
        help="Shows only packages that have updates with links to remotes_with_new_versions.",
    ),
    background: Optional[bool] = typer.Option(
        False,
        help="Suppress output completely. Exit code = 1 denotes that there are updates in remotes_with_new_versions",
    ),
    color: Optional[bool] = typer.Option(True, help="Enable/disable color in output"),
):
    pkgs_with_versions = process_pkgs(
        packages_stash=state.pkg_cache, worker_count=state.worker_count
    )
    if background:
        raise typer.Exit(check_versions_short_circuit(pkgs_with_versions))

    for pkg, remote_versions in pkgs_with_versions.items():
        print_func = print_stdout
        if show_updates_only and len(remote_versions) == 0:
            print_func = no_write

        print_func(
            print_package(
                pkg=pkg, remotes_with_new_versions=remote_versions, color=color
            )
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
    quiet: Optional[bool] = typer.Option(False, "--quiet", help="Suppresses output."),
):
    if overlay_dir != ".":
        state.overlay_dir = Path(overlay_dir).absolute()

    state.quiet = quiet
    state.print_stdout("Starting overlay-maintain-tools CLI")

    state.print_stdout(f"Building package cache from {str(overlay_dir)}.")
    state.pkg_cache = build_pkgs_cache(
        overlay_dir=overlay_dir, worker_count=worker_count
    )
    state.print_stdout(f"Package cache built.")
    state.worker_count = worker_count


if __name__ == "__main__":
    app()
