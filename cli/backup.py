import sys

import click

from core import backup, backup_manager


def _parse_paths(paths: tuple[str, ...]) -> list[str] | None:
    if not paths:
        return None
    res: list[str] = []
    for p in paths:
        res.extend(p.split())
    return res if res else None


@click.group(
    name="backup",
    help="Encrypted backup via restic + rclone",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def backup_group() -> None:
    pass


@backup_group.command(
    name="add",
    help="Add a folder to the backup target list",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("name")
@click.argument("path")
def add(name: str, path: str) -> None:
    try:
        backup_manager.add_target(name, path)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@backup_group.command(
    name="remove",
    help="Remove a target by name",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("name")
def remove(name: str) -> None:
    backup_manager.remove_target(name)


@backup_group.command(
    name="list",
    help="List configured backup targets",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def list_targets() -> None:
    targets = backup_manager.list_targets()
    if not targets:
        click.echo("No backup targets configured.")
    for t in targets:
        click.echo(f"  {t['name']:<15} {t['path']}")


@backup_group.command(
    name="check",
    help="Verify restic/rclone/bw prerequisites",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def check() -> None:
    backup.check()


@backup_group.command(
    name="init",
    help="Initialize the restic repository (idempotent)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def init() -> None:
    backup.init()


@backup_group.command(
    name="bootstrap",
    help="Fresh-machine setup: pull rclone config from Bitwarden, init, restore everything to original locations",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def bootstrap() -> None:
    backup.bootstrap()


@backup_group.command(
    name="run",
    help="Run a backup snapshot",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("targets", nargs=-1)
def run(targets: tuple[str, ...]) -> None:
    target_list = list(targets) if targets else ["all"]
    backup.run(target_list)


@backup_group.command(
    name="du",
    help="Show size breakdown per target (no restic/rclone involved)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("targets", nargs=-1)
@click.option(
    "--depth",
    type=int,
    default=1,
    show_default=True,
    help="How many directory levels deep to break down",
)
@click.option(
    "--path",
    "paths",
    multiple=True,
    help="Restrict to specific subpath(s) within the target, e.g. --path stow-dotfiles/",
)
def du(targets: tuple[str, ...], depth: int, paths: tuple[str, ...]) -> None:
    target_list = list(targets) if targets else ["all"]
    backup.sizes(target_list, depth=depth, paths=_parse_paths(paths))


@backup_group.command(
    name="snapshots",
    help="List existing snapshots",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def snapshots() -> None:
    backup.snapshots()


@backup_group.command(
    name="stats",
    help="Show total repo size on Dropbox (post-dedup, post-compression)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def stats() -> None:
    backup.stats()


@backup_group.command(
    name="forget",
    help="Drop old snapshots and reclaim their space (forget + prune)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--keep-last",
    type=int,
    default=1,
    show_default=True,
    help="How many most-recent snapshots to keep",
)
def forget(keep_last: int) -> None:
    backup.forget(keep_last)


@backup_group.command(
    name="forget-tag",
    help="Wipe ALL snapshots for one tag/target entirely (forget + prune)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("tag")
def forget_tag(tag: str) -> None:
    backup.forget_tag(tag)


@backup_group.command(
    name="restore",
    help="Restore latest snapshot for one tag into ~/restic-restore/<tag>/<basename> (safe test restore)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("tag")
def restore(tag: str) -> None:
    backup.restore_tag(tag, original=False)


@backup_group.command(
    name="restore-original",
    help="Restore latest snapshot for one tag to its ORIGINAL location (overwrites)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("tag")
def restore_original(tag: str) -> None:
    backup.restore_tag(tag, original=True)


@backup_group.command(
    name="restore-all",
    help="Restore latest snapshot of EVERY target into ~/restic-restore/<tag>/<basename> each",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def restore_all() -> None:
    backup.restore_all(original=False)


@backup_group.command(
    name="restore-all-original",
    help="Restore latest snapshot of EVERY target to its ORIGINAL location (overwrites)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def restore_all_original() -> None:
    backup.restore_all(original=True)


@backup_group.command(
    name="restore-snapshot",
    help="Restore a SPECIFIC snapshot (any ID, not just latest) into ~/restic-restore/<tag>-<id>",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("snapshot_id")
def restore_snapshot(snapshot_id: str) -> None:
    backup.restore_snapshot(snapshot_id)


@backup_group.command(
    name="preview",
    help="Show exactly what backup run would upload right now, AFTER exclusions, with real sizes",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("targets", nargs=-1)
@click.option(
    "--depth",
    type=int,
    default=2,
    show_default=True,
    help="How many directory levels deep to break down",
)
@click.option(
    "--path",
    "paths",
    multiple=True,
    help="Restrict to specific subpath(s) within the target, e.g. --path stow-dotfiles/",
)
def preview(targets: tuple[str, ...], depth: int, paths: tuple[str, ...]) -> None:
    target_list = list(targets) if targets else ["all"]
    backup.preview(target_list, depth=depth, paths=_parse_paths(paths))


@backup_group.command(
    name="changes",
    help="Show new/changed files vs. the latest snapshot (needs Dropbox connectivity)",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("targets", nargs=-1)
@click.option(
    "--path",
    "paths",
    multiple=True,
    help="Restrict to specific subpath(s) within the target",
)
def changes(targets: tuple[str, ...], paths: tuple[str, ...]) -> None:
    target_list = list(targets) if targets else ["all"]
    backup.changes(target_list, paths=_parse_paths(paths))
