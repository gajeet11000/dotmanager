import click

from core.setups import cursor_theme as cursor_theme_setup
from core.setups import docker as docker_setup
from core.setups import fish_shell as fish_setup
from core.setups import fstab as fstab_setup
from core.setups import gtk_theme as gtk_theme_setup
from core.setups import nwg_look as nwg_look_setup
from core.setups import papirus_folders as papirus_folders_setup
from core.setups.sddm import sddm as sddm_setup
from core.setups import yazi_theme as yazi_theme_setup


@click.group(
    name="setup",
    help="Run program-specific setup routines",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def setup_group() -> None:
    pass


@setup_group.command(
    name="docker",
    help="Enable docker service, group, add current user",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def docker() -> None:
    docker_setup.setup()


@setup_group.command(
    name="fstab",
    help="Interactively add partitions to /etc/fstab",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def fstab() -> None:
    fstab_setup.setup()


@setup_group.command(
    name="fish",
    help="Set fish as default shell and apply Catppuccin Mocha theme",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def fish() -> None:
    fish_setup.setup()


@setup_group.command(
    name="nwg_look",
    help="Apply current gsettings and export config files (nwg-look -a -x)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def nwg_look() -> None:
    nwg_look_setup.setup()


@setup_group.command(name="nwg-look", hidden=True)
def nwg_look_alias() -> None:
    nwg_look_setup.setup()


@setup_group.command(
    name="gtk_theme",
    help="Install all bundled GTK themes (themes/*/gtk/*.zip) system-wide (no AUR rebuild)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def gtk_theme() -> None:
    gtk_theme_setup.setup()


@setup_group.command(name="gtk-theme", hidden=True)
def gtk_theme_alias() -> None:
    gtk_theme_setup.setup()


@setup_group.command(
    name="cursor_theme",
    help="Install Bibata-Rainbow-Modern cursor theme system-wide from the bundled tar.gz (no AUR rebuild)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cursor_theme() -> None:
    cursor_theme_setup.setup()


@setup_group.command(name="cursor-theme", hidden=True)
def cursor_theme_alias() -> None:
    cursor_theme_setup.setup()


@setup_group.command(
    name="papirus_folders",
    help="Install the papirus-folders CLI + Catppuccin colored folder icons (no AUR rebuild)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def papirus_folders() -> None:
    papirus_folders_setup.setup()


@setup_group.command(name="papirus-folders", hidden=True)
def papirus_folders_alias() -> None:
    papirus_folders_setup.setup()


@setup_group.command(
    name="yazi_theme",
    help="Install all bundled yazi flavors (assets/yazi-flavors/*.yazi) to ~/.config/yazi/flavors/",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def yazi_theme() -> None:
    yazi_theme_setup.setup()


@setup_group.command(name="yazi-theme", hidden=True)
def yazi_theme_alias() -> None:
    yazi_theme_setup.setup()


@setup_group.group(
    name="sddm",
    invoke_without_command=True,
    help="SDDM theme, session, and cursor setup",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def sddm(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        sddm_setup.run_all()


@sddm.command(
    name="all",
    help="Run install (theme & fonts) and conf in order",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def sddm_all() -> None:
    sddm_setup.run_all()


@sddm.command(
    name="install",
    help="Clone the astronaut theme, install its fonts, pick a style",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def sddm_install() -> None:
    sddm_setup.install_theme()


@sddm.command(
    name="theme",
    help="Alias for install (clone theme, install fonts, pick style)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def sddm_theme() -> None:
    sddm_setup.install_theme()


@sddm.command(
    name="conf",
    help="Install SDDM configuration (/etc/sddm.conf)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def sddm_conf() -> None:
    sddm_setup.install_conf()


@sddm.command(
    name="config",
    hidden=True,
    help="Alias for conf",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def sddm_config() -> None:
    sddm_setup.install_conf()
