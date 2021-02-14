# Description

Provides certain tools to be run on the overlay directory. See individual commands help for details.

This is a small collection of tools to help automate some tasks related to Gentoo overlay maintenance.

It can:

* Generate a README like this.
* Look up a package in remotes and tell if a new version is available.

# Getting started

## Installation

Install the project from PyPI:

```console
$ pip install --user overlay-maintain-tools
```

Or from nitratesky overlay:

```console
$ eselect repository enable nitratesky && emerge -a1 app-portage/overlay-maintain-tools
```

## Sample usage

The overlay directory is at `/srv/overlay`. To generate a README with the badges, create a skeleton template
(like [the one in repo](https://raw.githubusercontent.com/VTimofeenko/overlay-maintain-tools/master/docs/templates/skeleton.jinja2)) and run:

```
$ overlay_maintain_tools --overlay-dir /srv/overlay mkreadme --skeleton-file /path/to/readme.template
```

To generate a report on packages versions in overlay, make sure that [`metadata.xml`](https://devmanual.gentoo.org/ebuild-writing/misc-files/metadata/index.html) file has remotes set and run:

```
$ overlay_maintain_tools --overlay-dir /srv/overlay check-remote-versions
```


# Details

**Usage**:

```console
$ overlay_maintain_tools [OPTIONS] COMMAND [ARGS]...
```

**General Options**:

* `--version`: Show version and exit.
* `--overlay-dir PATH`: Specify location for overlay.  [default: .]
* `--worker-count INTEGER RANGE`: Number of workers for creating package cache.  [default: 8]
* `--quiet`: Suppresses output.  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

These options can be specified for any `COMMAND` except for  `create-config` which ignores these options.

**Commands**:

* `check-remote-versions`: Prints report on the versions of packages.
* `mkreadme`: Creates a README for an overlay.

# Commands
## `overlay_maintain_tools mkreadme`

Creates a README for an overlay. The generated README can utilize data on packages
available in the overlay and their versions. For sample template, see the documentation.

**Usage**:

```console
$ overlay_maintain_tools mkreadme [OPTIONS]
```

**Options**:

* `--skeleton-file PATH`: The file containing README template. Should be inside the template directory.
* `--template-dir DIRECTORY`: Template directory. Can be specified if more complex jinja2 templates will be used.
* `--output PATH`: Where to save the resulting README. If not supplied - print to stdout.
* `--help`: Show this message and exit.

## `overlay_maintain_tools check-remote-versions`

Prints report on the versions of packages. Checks versions available upstream.
Pulls the data from remotes specified inside <upstream> tag in metadata.xml

**Usage**:

```console
$ overlay_maintain_tools check-remote-versions [OPTIONS]
```

**Options**:

* `--show-updates-only`: Shows only packages that have updates with links to remotes_with_new_versions.
* `--background`: Suppress output of this subcommand completely. Exit code = 100 denotes that there are updates in remotes
* `--color`: Enable/disable color in output
* `--help`: Show this message and exit.

# Contrib directory

There are shell completions for bash and zsh (generated through [typer](typer.tiangolo.com/)).
