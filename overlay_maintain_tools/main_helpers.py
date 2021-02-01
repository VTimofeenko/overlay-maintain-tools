from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

from overlay_maintain_tools.pkgs_cache import Package


@dataclass
class State:
    overlay_dir: Path = Path.cwd()
    pkg_cache: List[Package] = field(default_factory=list)


# noinspection PyUnusedLocal
def no_write(*args, **kwargs):
    """Function that suppresses writing altogether"""
    pass
