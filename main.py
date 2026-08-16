#!/usr/bin/env python3
import argparse
import sys

from core import installer, package_manager, stow_manager
from core.setups import docker as docker_setup
from core.setups import fish_shell as fish_setup
from core.setups import fstab as fstab_setup
from core.setups import sddm as sddm_setup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dotmanager",
        description="Unified dotfile & system manager",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="Install packages")
    install_parser.add_argument(
        "scope",
        choices=["all", "essentials"],
        help="Which set of packages to install",
    )

    manage_parser = subparsers.add_parser("manage", help="Manage the package lists")
    manage_sub = manage_parser.add_subparsers(dest="action", required=True)

    add_parser = manage_sub.add_parser(
        "add", help="Add package(s): name | name/aur | name/flatpak"
    )
    add_parser.add_argument(
        "packages", nargs="+", help="e.g. htop yay/aur obsidian/flatpak"
    )

    remove_parser = manage_sub.add_parser("remove", help="Remove package(s) by name")
    remove_parser.add_argument(
        "packages", nargs="+", help="Space separated package names"
    )

    stow_parser = subparsers.add_parser("stow", help="Manage GNU Stow dotfile packages")
    stow_sub = stow_parser.add_subparsers(dest="action", required=True)

    stow_action = stow_sub.add_parser("stow", help="Stow package(s), or 'all'")
    stow_action.add_argument("packages", nargs="+")

    restow_action = stow_sub.add_parser("restow", help="Restow package(s), or 'all'")
    restow_action.add_argument("packages", nargs="+")

    unstow_action = stow_sub.add_parser("unstow", help="Unstow package(s), or 'all'")
    unstow_action.add_argument("packages", nargs="+")

    new_action = stow_sub.add_parser(
        "new", help="Create a stow package from an existing path"
    )
    new_action.add_argument("path", help="e.g. ~/.config/nvim or ~/.zshrc")
    new_action.add_argument(
        "--name", help="Package name (default: basename, dot stripped)"
    )

    delete_action = stow_sub.add_parser(
        "delete", help="Unstow and delete a stow package"
    )
    delete_action.add_argument("package")
    delete_action.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )

    setup_parser = subparsers.add_parser(
        "setup", help="Run program-specific setup routines"
    )
    setup_sub = setup_parser.add_subparsers(dest="target", required=True)

    setup_sub.add_parser(
        "docker", help="Enable docker service, group, add current user"
    )
    setup_sub.add_parser("fstab", help="Interactively add partitions to /etc/fstab")
    setup_sub.add_parser(
        "fish", help="Set fish as default shell and apply Catppuccin Mocha theme"
    )

    sddm_parser = setup_sub.add_parser(
        "sddm", help="SDDM theme, session, and cursor setup"
    )
    sddm_sub = sddm_parser.add_subparsers(dest="action", required=True)
    sddm_sub.add_parser(
        "install", help="Clone the astronaut theme, install its fonts, pick a style"
    )
    sddm_sub.add_parser("theme", help="Set the active SDDM theme")
    sddm_sub.add_parser(
        "display-server",
        help="Pick the SDDM greeter's display server mode (wayland/x11-user/x11)",
    )
    sddm_sub.add_parser("cursor-theme", help="Set the greeter cursor theme")
    sddm_sub.add_parser("cursor-size", help="Set the greeter cursor size")
    sddm_sub.add_parser(
        "virtual-keyboard", help="Enable the theme's on-screen keyboard toggle"
    )
    sddm_sub.add_parser(
        "all", help="Run install, theme, session, cursor-theme, cursor-size in order"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "install":
        if args.scope == "all":
            installer.install_all()
        elif args.scope == "essentials":
            installer.install_essentials()

    elif args.command == "manage":
        if args.action == "add":
            try:
                package_manager.add_packages(args.packages)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.action == "remove":
            package_manager.remove_packages(args.packages)

    elif args.command == "stow":
        try:
            if args.action == "stow":
                stow_manager.stow_packages(args.packages)
            elif args.action == "restow":
                stow_manager.restow_packages(args.packages)
            elif args.action == "unstow":
                stow_manager.unstow_packages(args.packages)
            elif args.action == "new":
                stow_manager.create_package(args.path, args.name)
            elif args.action == "delete":
                stow_manager.delete_package(args.package, args.force)
        except (FileNotFoundError, FileExistsError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "setup":
        if args.target == "docker":
            docker_setup.setup()
        elif args.target == "fstab":
            fstab_setup.setup()
        elif args.target == "fish":
            fish_setup.setup()
        elif args.target == "sddm":
            if args.action == "install":
                sddm_setup.install_theme()
            elif args.action == "theme":
                sddm_setup.set_theme()
            elif args.action == "display-server":
                sddm_setup.set_display_server()
            elif args.action == "cursor-theme":
                sddm_setup.set_cursor_theme()
            elif args.action == "cursor-size":
                sddm_setup.set_cursor_size()
            elif args.action == "virtual-keyboard":
                sddm_setup.set_virtual_keyboard()
            elif args.action == "all":
                sddm_setup.run_all()


if __name__ == "__main__":
    main()
