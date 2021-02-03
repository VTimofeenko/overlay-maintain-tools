from jinja2 import Environment, FileSystemLoader, Template
from typing import Union
from pathlib import Path


def _get_template_path(skeleton_template_name: Path) -> Path:
    """To be used if the template dir is not specified. Returns some directory to make Jinja template loader work"""
    return skeleton_template_name.parent


def setup_template(
    skeleton_template: Path, search_path: Union[Path, None] = None
) -> Template:
    # guess search_path
    if search_path is None:
        search_path = _get_template_path(skeleton_template)

    # If the template path was provided as absolute - make it not so.
    if str(skeleton_template).startswith(str(search_path)):
        skeleton_template = skeleton_template.relative_to(search_path)

    env = Environment(loader=FileSystemLoader(search_path))
    env.lstrip_blocks = True
    env.trim_blocks = True
    return env.get_template(str(skeleton_template))


def render_template(packages_stash, template: Template) -> str:
    return template.render(packages=packages_stash)
