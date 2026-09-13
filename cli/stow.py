import sys

import click

from core import stow_manager


@click.group(
    name="stow",
    help="Manage GNU Stow dotfile packages",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def stow_group() -> None:
    pass


@stow_group.command(
    name="stow",
    help="Stow package(s), or 'all'",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("packages", nargs=-1, required=True)
def stow(packages: tuple[str, ...]) -> None:
    try:
        stow_manager.stow_packages(list(packages))
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@stow_group.command(
    name="restow",
    help="Restow package(s), or 'all'",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("packages", nargs=-1, required=True)
def restow(packages: tuple[str, ...]) -> None:
    try:
        stow_manager.restow_packages(list(packages))
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@stow_group.command(
    name="unstow",
    help="Unstow package(s), or 'all'",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("packages", nargs=-1, required=True)
def unstow(packages: tuple[str, ...]) -> None:
    try:
        stow_manager.unstow_packages(list(packages))
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@stow_group.command(
    name="new",
    help="Create a stow package from an existing path",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("path")
@click.option(
    "--name",
    default=None,
    help="Package name (default: basename, dot stripped)",
)
def new(path: str, name: str | None) -> None:
    try:
        stow_manager.create_package(path, name)
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@stow_group.command(
    name="delete",
    help="Unstow and delete a stow package",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("package")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete(package: str, force: bool) -> None:
    try:
        stow_manager.delete_package(package, force)
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
