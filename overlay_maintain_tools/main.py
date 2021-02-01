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
from overlay_maintain_tools.main_helpers import State

__version__ = "1.0"
app = typer.Typer()
state = State()
print_stdout = typer.echo
print_stderr = partial(typer.echo, err=True)


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
            exists=True
        ),
        readme: Optional[Path] = typer.Option(
            None,
            "--readme-output",
            help="Where to save the resulting README. If not supplied - print to stdout."
        )
):
    template = setup_template(skeleton_template_name=str(skeleton_file), search_path=str(template_dir))
    text = render_template(packages_stash=state.pkg_cache, template=template)
    if readme.is_file():
        readme.write_text(text)
    else:
        print_stdout(text)


# noinspection PyUnusedLocal
@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", help="Show version and exit.", callback=version_callback, is_eager=True
    ),
    overlay_dir: Optional[Path] = typer.Option(
        '.', "--overlay-dir", help="Specify location for overlay."
    ),
    worker_count: int = typer.Option(8, min=1, help="Number of workers for creating package cache.")
):
    if overlay_dir != '.':
        state.overlay_dir = Path(overlay_dir).absolute()

    state.pkg_cache = build_pkgs_cache(overlay_dir=overlay_dir)


if __name__ == "__main__":
    app()
