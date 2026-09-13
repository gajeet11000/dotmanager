import click

from cli.backup import backup_group
from cli.install import install_cmd
from cli.manage import manage_group
from cli.setup import setup_group
from cli.stow import stow_group
from cli.theme import theme_group


@click.group(
    name="dotmanager",
    help="Unified dotfile & system manager",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cli() -> None:
    pass


cli.add_command(install_cmd)
cli.add_command(manage_group)
cli.add_command(stow_group)
cli.add_command(theme_group)
cli.add_command(setup_group)
cli.add_command(backup_group)

__all__ = ["cli"]
