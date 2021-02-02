import pytest
from itertools import product
from typer import Exit

import overlay_maintain_tools.check_remote_versions as crv
from overlay_maintain_tools.pkgs_cache import Remote

r_type = "github"
r_target = "gentoo"
r = Remote(r_type, r_target)


class Package:
    def __init__(self):
        self.atomname = "package"
        self.versions = ["1", "2"]
        self.remotes = (r,)


def test_print_remote():
    remote_print = crv.print_remote((r, "1"))
    assert all([_ in remote_print for _ in [r_type, r_target]])


@pytest.mark.parametrize(
    "param_combo",
    tuple(product((True, False), (True, False), (True, False))),
    ids=lambda tup: f"Running print_package on package with new version in remotes: {tup[0]}, color: {tup[1]}",
)
def test_print_package(param_combo):
    new_version = param_combo[0]
    color = param_combo[1]
    if new_version:
        remotes = ((Remote("github", "user/package"), "1"),)
    else:
        remotes = ()

    output = crv.print_package(Package(), remotes, color)

    assert ("New version available" in output) == new_version
    assert ("[" in output) == color


def test_print_one_package_remote():
    assert all([_ in crv.print_one_package_remote(r) for _ in [r_type, r_target]])


@pytest.mark.parametrize(
    "with_remotes",
    (True, False),
    ids=lambda t: f"Package with{'out' * t} remotes gets printed",
)
def test_print_all_package_remotes(with_remotes, monkeypatch):
    some_unique_test_string = "61d4f74c-6f0a-494f-be1e-20fab4177fcd"
    monkeypatch.setattr(
        crv, "print_one_package_remote", lambda *args, **kwargs: some_unique_test_string
    )
    p = Package()
    if with_remotes:
        p.remotes = (r,)
        assert some_unique_test_string in crv.print_all_package_remotes(p)
    else:
        p.remotes = ()
        assert "No remotes" in crv.print_all_package_remotes(p)


@pytest.mark.parametrize(
    "param_combo",
    tuple(product((True, False), (True, False), (True, False))),
    ids=lambda tup: f"Running print_package on package with new version in remotes: {tup[0]}, color: {tup[1]}",
)
def test_print_version_header(param_combo):
    new_version = param_combo[0]
    color = param_combo[1]
    if new_version:
        remotes = ((Remote("github", "user/package"), "1"),)
    else:
        remotes = ()
    output = crv.print_version_header(color, remotes)

    assert ("New version available" in output) == new_version
    assert ("[" in output) == color


@pytest.mark.parametrize(
    "with_remotes,result",
    ((True, 1), (False, 0)),
    ids=(
        "Package with remotes - exit code = 0",
        "Package without remotes - exit code = 1",
    ),
)
def test_check_versions_short_circuit(with_remotes, result):
    if with_remotes:
        remotes = ((r, "1"),)
    else:
        remotes = ()

    output = crv.check_versions_short_circuit({"pkg": remotes})
    assert isinstance(output, Exit)
    assert output.exit_code == result
