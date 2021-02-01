from pathlib import Path

tmp_repo = "repo"
tmp_package = "app-misc/pkgname"


def create_ebuild(pkgdir: Path, version: str = "1") -> Path:
    filename = pkgdir / f"pkgname-{version}.ebuild"
    filename.touch()
    return filename
