from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()
github_url = "https://github.com/VTimofeenko/overlay-maintain-tools"

setup(
    name="overlay_maintain_tools",
    version="1.0.0",
    description="A set of utilities to maintain Gentoo overlay",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url=github_url,
    license="GPL",
    author="Vladimir Timofeenko",
    author_email="overlay.tools.maintain@vtimofeenko.com",
    include_package_data=True,
    packages=find_packages(exclude=("tests", "docs")),
    package_dir={"overlay_maintain_tools": "overlay_maintain_tools"},
    entry_points={
        "console_scripts": ["overlay_maintain_tools = overlay_maintain_tools.main:app"]
    },
    install_requires=[
        "python-dotenv~=0.15.0",
        "requests~=2.25.1",
        "typer~=0.3.2",
        "toolz~=0.11.1",
        "jinja2",
        "portage",
    ],
    python_requires=">=3.8, <4",
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    extras_require={"docs": ["jinja2", "typer-cli"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    keywords="gentoo overlay",
    project_urls={"Bug Reports": github_url + "/issues", "Source": github_url},
)
