import sys

import click

from core import theme_manager


@click.group(
    name="theme",
    help="Switch the active theme (GTK, icons, ...) live, no logout needed",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def theme_group() -> None:
    pass


@theme_group.command(
    name="set",
    help="Set and live-apply a theme across all its supported apps",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("name")
def set_theme(name: str) -> None:
    try:
        theme_manager.set_theme(name)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@theme_group.command(
    name="list",
    help="List available theme names",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def list_themes() -> None:
    for name in theme_manager.list_themes():
        click.echo(f"  {name}")
