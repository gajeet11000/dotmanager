import click

from core import installer


@click.command(
    name="install",
    help="Install packages",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument(
    "scope",
    type=click.Choice(["all", "essentials"], case_sensitive=False),
)
def install_cmd(scope: str) -> None:
    """Install packages by scope ('all' or 'essentials')."""
    if scope == "all":
        installer.install_all()
    elif scope == "essentials":
        installer.install_essentials()
