from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path


def setup_template(skeleton_template_name: str = "readme.skel.jinja2",
                   search_path: str = ".dev/docs") -> Template:
    # If the template path was provided as absolute - make it not so.
    if skeleton_template_name.startswith(search_path):
        skeleton_template_name = skeleton_template_name[len(search_path):]

    env = Environment(loader=FileSystemLoader(Path.cwd() / search_path))
    env.lstrip_blocks = True
    env.trim_blocks = True
    return env.get_template(skeleton_template_name)


def render_template(packages_stash, template: Template) -> str:
    return template.render(packages=packages_stash)
