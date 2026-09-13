import sys

import click

from core import package_manager


@click.group(
    name="manage",
    help="Manage the package lists",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def manage_group() -> None:
    pass


@manage_group.command(
    name="add",
    help="Add package(s): name | name/aur | name/flatpak",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("packages", nargs=-1, required=True)
def add(packages: tuple[str, ...]) -> None:
    try:
        package_manager.add_packages(list(packages))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@manage_group.command(
    name="remove",
    help="Remove package(s) by name",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("packages", nargs=-1, required=True)
def remove(packages: tuple[str, ...]) -> None:
    package_manager.remove_packages(list(packages))
