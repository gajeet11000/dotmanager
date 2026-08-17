#!/usr/bin/env python3
import argparse
import sys

from core import (
    backup,
    backup_manager,
    installer,
    package_manager,
    stow_manager,
)
from core.setups import docker as docker_setup
from core.setups import fish_shell as fish_setup
from core.setups import fstab as fstab_setup
from core.setups import nwg_look as nwg_look_setup
from core.setups import sddm as sddm_setup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dotmanager",
        description="Unified dotfile & system manager",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- install ----
    install_parser = subparsers.add_parser("install", help="Install packages")
    install_parser.add_argument(
        "scope",
        choices=["all", "essentials"],
        help="Which set of packages to install",
    )

    # ---- manage ----
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

    # ---- stow ----
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

    # ---- setup ----
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
    setup_sub.add_parser("nwg_look", help="Apply current gsettings via nwg-look -a")

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

    # ---- backup ----
    backup_parser = subparsers.add_parser(
        "backup", help="Encrypted backup via restic + rclone"
    )
    backup_sub = backup_parser.add_subparsers(dest="action", required=True)

    add_action = backup_sub.add_parser(
        "add", help="Add a folder to the backup target list"
    )
    add_action.add_argument("name", help="Short identifier, e.g. zen-profile")
    add_action.add_argument("path", help="Path to back up, e.g. ~/.zen")

    remove_action = backup_sub.add_parser("remove", help="Remove a target by name")
    remove_action.add_argument("name")

    backup_sub.add_parser("list", help="List configured backup targets")
    backup_sub.add_parser("check", help="Verify restic/rclone/bw prerequisites")
    backup_sub.add_parser("init", help="Initialize the restic repository (idempotent)")
    backup_sub.add_parser(
        "bootstrap",
        help="Fresh-machine setup: pull rclone config from Bitwarden, init, restore everything to original locations",
    )

    run_action = backup_sub.add_parser("run", help="Run a backup snapshot")
    run_action.add_argument(
        "targets", nargs="*", default=["all"], help="Target name(s), default: all"
    )

    du_action = backup_sub.add_parser(
        "du", help="Show size breakdown per target (no restic/rclone involved)"
    )
    du_action.add_argument(
        "targets", nargs="*", default=["all"], help="Target name(s), default: all"
    )
    du_action.add_argument(
        "--depth",
        type=int,
        default=1,
        help="How many directory levels deep to break down (default: 1)",
    )
    du_action.add_argument(
        "--path",
        nargs="*",
        default=None,
        help="Restrict to specific subpath(s) within the target, e.g. --path stow-dotfiles/ some_project/",
    )

    backup_sub.add_parser("snapshots", help="List existing snapshots")
    backup_sub.add_parser(
        "stats", help="Show total repo size on Dropbox (post-dedup, post-compression)"
    )

    forget_action = backup_sub.add_parser(
        "forget", help="Drop old snapshots and reclaim their space (forget + prune)"
    )
    forget_action.add_argument(
        "--keep-last",
        type=int,
        default=1,
        help="How many most-recent snapshots to keep (default: 1)",
    )

    forget_tag_action = backup_sub.add_parser(
        "forget-tag",
        help="Wipe ALL snapshots for one tag/target entirely (forget + prune)",
    )
    forget_tag_action.add_argument("tag", help="Tag name (matches a target name)")

    restore_action = backup_sub.add_parser(
        "restore",
        help="Restore latest snapshot for one tag into ~/restic-restore/<tag>/<basename> (safe test restore)",
    )
    restore_action.add_argument("tag", help="Tag name (matches a target name)")

    restore_original_action = backup_sub.add_parser(
        "restore-original",
        help="Restore latest snapshot for one tag to its ORIGINAL location (overwrites)",
    )
    restore_original_action.add_argument("tag", help="Tag name (matches a target name)")

    backup_sub.add_parser(
        "restore-all",
        help="Restore latest snapshot of EVERY target into ~/restic-restore/<tag>/<basename> each",
    )

    backup_sub.add_parser(
        "restore-all-original",
        help="Restore latest snapshot of EVERY target to its ORIGINAL location (overwrites)",
    )

    restore_snapshot_action = backup_sub.add_parser(
        "restore-snapshot",
        help="Restore a SPECIFIC snapshot (any ID, not just latest) into ~/restic-restore/<tag>-<id>",
    )
    restore_snapshot_action.add_argument(
        "snapshot_id", help="Snapshot ID, from 'backup snapshots'"
    )

    preview_action = backup_sub.add_parser(
        "preview",
        help="Show exactly what backup run would upload right now, AFTER exclusions, with real sizes",
    )
    preview_action.add_argument(
        "targets", nargs="*", default=["all"], help="Target name(s), default: all"
    )
    preview_action.add_argument(
        "--depth",
        type=int,
        default=2,
        help="How many directory levels deep to break down (default: 2)",
    )
    preview_action.add_argument(
        "--path",
        nargs="*",
        default=None,
        help="Restrict to specific subpath(s) within the target, e.g. --path stow-dotfiles/ some_project/",
    )

    changes_action = backup_sub.add_parser(
        "changes",
        help="Show new/changed files vs. the latest snapshot (needs Dropbox connectivity)",
    )
    changes_action.add_argument(
        "targets", nargs="*", default=["all"], help="Target name(s), default: all"
    )
    changes_action.add_argument(
        "--path",
        nargs="*",
        default=None,
        help="Restrict to specific subpath(s) within the target",
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
        elif args.target == "nwg_look":
            nwg_look_setup.setup()
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

    elif args.command == "backup":
        if args.action == "add":
            try:
                backup_manager.add_target(args.name, args.path)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.action == "remove":
            backup_manager.remove_target(args.name)
        elif args.action == "list":
            targets = backup_manager.list_targets()
            if not targets:
                print("No backup targets configured.")
            for t in targets:
                print(f"  {t['name']:<15} {t['path']}")
        elif args.action == "check":
            backup.check()
        elif args.action == "init":
            backup.init()
        elif args.action == "bootstrap":
            backup.bootstrap()
        elif args.action == "run":
            backup.run(args.targets)
        elif args.action == "du":
            backup.sizes(args.targets, depth=args.depth, paths=args.path)
        elif args.action == "snapshots":
            backup.snapshots()
        elif args.action == "stats":
            backup.stats()
        elif args.action == "preview":
            backup.preview(args.targets, depth=args.depth, paths=args.path)
        elif args.action == "changes":
            backup.changes(args.targets, paths=args.path)
        elif args.action == "forget":
            backup.forget(args.keep_last)
        elif args.action == "forget-tag":
            backup.forget_tag(args.tag)
        elif args.action == "restore":
            backup.restore_tag(args.tag, original=False)
        elif args.action == "restore-original":
            backup.restore_tag(args.tag, original=True)
        elif args.action == "restore-all":
            backup.restore_all(original=False)
        elif args.action == "restore-all-original":
            backup.restore_all(original=True)
        elif args.action == "restore-snapshot":
            backup.restore_snapshot(args.snapshot_id)


if __name__ == "__main__":
    main()
