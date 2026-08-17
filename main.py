#!/usr/bin/env python3
import argparse
import sys

from core import backup, backup_manager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dotmanager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser(
        "backup", help="Encrypted backup & sync via restic + rclone"
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

    bootstrap_action = backup_sub.add_parser(
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
        "changes", help="Show new/changed files vs. the latest snapshot (needs Dropbox connectivity)"
    )
    changes_action.add_argument("targets", nargs="*", default=["all"], help="Target name(s), default: all")
    changes_action.add_argument("--path", nargs="*", default=None, help="Restrict to specific subpath(s) within the target")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "backup":
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
        elif args.action == "changes":
            backup.changes(args.targets, paths=args.path)


if __name__ == "__main__":
    main()
