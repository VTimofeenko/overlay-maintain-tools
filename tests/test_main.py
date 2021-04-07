from typer.testing import Result, CliRunner
from itertools import product
import pytest

from overlay_maintain_tools.main import app
from overlay_maintain_tools.main_helpers import State

from tests.utils import create_ebuild, tmp_package

"""Main file for testing commands defined in main"""

runner = CliRunner(mix_stderr=False)


@pytest.fixture(scope="function")
def setup_overlay(create_pkgdir, setup_metadata):
    ebuild = create_ebuild(create_pkgdir, "1")
    ebuild.write_text("DESCRIPTION='SOME DESC'")
    return create_pkgdir.parent.parent


@pytest.fixture(scope="function")
def setup_repology_cache(tmp_path):
    cache_file = tmp_path / "repology_cache"
    cache_file.write_text(f"{tmp_package} repology_pkgname")
    return cache_file


def test_version_callback():
    """Makes sure that the version and only the version is printed with --version"""
    result = runner.invoke(app, ("--version",))
    assert result.exit_code == 0
    assert "version" in result.stdout
    assert len(result.stdout.split("\n")) == 2  # version line + next line


@pytest.mark.parametrize(
    "param_combo",
    tuple(product((True, False), (True, False), (True, False), (True, False))),
    ids=lambda tup: f"New version: {tup[0]}, check-remote-versions{' --show-updates-only' * tup[1]}"
    f"{' --background' * tup[2]}{' --color'*tup[3]}",
)
def test_check_remote_versions(setup_overlay, monkeypatch, param_combo):
    import overlay_maintain_tools.version_utils as vu

    new_version_present, show_updates_only, background, color = param_combo

    overlay_dir = setup_overlay

    # monkeypatch the stuff that pulls information from remote
    monkeypatch.setitem(
        vu.version_getter,
        "github",
        lambda _: "9999" * new_version_present,
    )
    monkeypatch.setitem(vu.version_getter, "pypi", lambda _: "")
    params = (
        ("--overlay-dir", str(overlay_dir), "check-remote-versions")
        + ("--show-updates-only",) * show_updates_only
        + ("--background",) * background
        + ("--color",) * color
    )

    result = runner.invoke(app, params)

    if background:
        split_result = result.stdout.split("\n")
        main_done = split_result.index("Package cache built.")
        stdout_after_main = split_result[main_done + 1 :]
        assert len(stdout_after_main) == 1  # +1 for extra \n
        if new_version_present:
            assert result.exit_code == 100
        else:
            assert result.exit_code == 0
    else:
        assert result.exit_code == 0
        assert len(result.stdout) >= 0
    assert len(result.stderr) == 0


@pytest.mark.parametrize(
    "template_dir_supplied",
    (True, False),
    ids=lambda _: f"Template dir was supplied: {_}",
)
@pytest.mark.parametrize(
    "to_stdout", (True, False), ids=lambda _: f"Print result to stdout: {_}"
)
def test_mkreadme(tmp_path, setup_overlay, to_stdout, template_dir_supplied):
    output_path = tmp_path / "output"
    overlay_dir = setup_overlay
    template_dir = tmp_path / "docs"
    template_dir.mkdir()
    skeleton_file = template_dir / "readme"
    template_content = "Hello world"
    skeleton_file.write_text(template_content)

    params = (
        [
            "--overlay-dir",
            overlay_dir,
            "mkreadme",
            "--skeleton-file",
            skeleton_file,
        ]
        + [
            "--template-dir",
            template_dir,
        ]
        * template_dir_supplied
        + ["--output", output_path] * (not to_stdout),
    )

    result = runner.invoke(app, params[0])
    assert result.exit_code == 0
    if to_stdout:
        assert template_content in result.stdout
    else:
        assert template_content in output_path.read_text()


@pytest.mark.parametrize(
    "param_combo",
    tuple(product((True, False), (True, False))),
    ids=lambda tup: f"New version in repology: {tup[0]}{', --quiet' * tup[1]}",
)
def test_check_repology(setup_overlay, setup_repology_cache, monkeypatch, param_combo):
    import overlay_maintain_tools.repology.main as om

    newer_version_in_repology, quiet = param_combo

    # noinspection PyUnusedLocal
    def repology_func(*args, **kwargs):
        if newer_version_in_repology:
            return {"2"}
        else:
            return set()

    monkeypatch.setattr(om, "_get_versions_from_repology_repos", repology_func)

    overlay_dir = setup_overlay
    params = (
        (
            "--overlay-dir",
            str(overlay_dir),
        )
        + ("--quiet",) * quiet
        + ("check-repology",)
        + (
            "--repology-cache-location",
            str(setup_repology_cache),
        )
    )
    result = runner.invoke(app, params)

    if quiet:
        if newer_version_in_repology:
            assert result.exit_code == 100
        else:
            assert result.exit_code == 0
    else:
        assert result.exit_code == 0
        if newer_version_in_repology:
            assert (
                "Versions in repology greater than ones in overlay: 2" in result.stdout
            )


def test_check_repology_no_name(setup_overlay, tmp_path, monkeypatch):
    """Checks that repology check passes if there is no mapping for the package in the repology cache"""
    repology_cache = tmp_path / "repology_cache"
    repology_cache.touch()
    overlay_dir = setup_overlay
    params = (
        (
            "--overlay-dir",
            str(overlay_dir),
        )
        + ("check-repology",)
        + (
            "--repology-cache-location",
            str(repology_cache),
        )
    )
    result = runner.invoke(app, params)
    assert result.exit_code == 0
