from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union, Callable
from typer import echo
from functools import partial

from overlay_maintain_tools.pkgs_cache import Package


@dataclass
class State:
    overlay_dir: Path = Path.cwd()
    pkg_cache: List[Package] = field(default_factory=list)
    worker_count: int = 8
    quiet: bool = False

    @property
    def print_stdout(self) -> Callable:
        """Prints something if quiet is not set"""
        if self.quiet:
            # noinspection PyUnusedLocal
            def _quiet_func(*args, **kwargs):
                pass

            return _quiet_func
        else:
            return echo

    @property
    def print_stderr(self) -> Callable:
        return partial(echo, err=True)


# noinspection PyUnusedLocal
def no_write(*args, **kwargs):
    """Function that suppresses writing altogether"""
    pass
