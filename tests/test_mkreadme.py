from jinja2 import Template
from pathlib import Path
import pytest

import overlay_maintain_tools.mkreadme as mr


@pytest.fixture(scope="function")
def setup_template(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    main_template_file = template_dir / "readme.skel.jinja2"
    main_template_file.write_text(
        """{% for pkg in packages -%}
{{ pkg }}
{% endfor -%}
Some line"""
    )
    return template_dir, main_template_file


@pytest.mark.parametrize("template_path_is_relative", (True, False))
def test_setup_template(setup_template, template_path_is_relative):
    template_dir: Path
    main_template_file: Path
    template_dir, main_template_file = setup_template
    abs_template_path = main_template_file

    if template_path_is_relative:
        main_template_file = main_template_file.relative_to(template_dir)

    assert (
        mr.setup_template(main_template_file, template_dir).render()
        == Template(abs_template_path.read_text()).render()
    )


def test_render_template(setup_template):
    _, template_file = setup_template
    assert (
        mr.render_template(
            packages_stash=["pkg"], template=Template(template_file.read_text())
        )
        == """pkg
Some line"""
    )


def test__get_template_path(tmp_path):
    readme_path = tmp_path / "skeleton"
    assert mr._get_template_path(readme_path) == tmp_path
