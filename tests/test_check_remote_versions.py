import pytest
from itertools import product

import overlay_maintain_tools.check_remote_versions as crv
from overlay_maintain_tools.pkgs_cache import Remote


def test_print_remote():
    r_type = "github"
    r_target = "gentoo"
    r = Remote(r_type, r_target)
    remote_print = crv.print_remote((r, "1"))
    assert all([_ in remote_print for _ in [r_type, r_target]])


@pytest.mark.parametrize(
    "param_combo",
    tuple(product((True, False), (True, False), (True, False))),
    ids=lambda tup: f"Running print_package on package with new version in remotes: {tup[0]}, color: {tup[1]}",
)
def test_print_package(param_combo):
    class Package:
        def __init__(self):
            self.atomname = "package"
            self.versions = ["1", "2"]

    new_version = param_combo[0]
    color = param_combo[1]
    if new_version:
        remotes = ((Remote("github", "user/package"), "1"),)
    else:
        remotes = ()

    output = crv.print_package(Package(), remotes, color)

    assert ("New version available" in output) == new_version
    assert ("[" in output) == color
