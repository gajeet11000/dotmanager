import json
import sys
from pathlib import Path

from config import RESTORE_STAGING_DIR
from core import backup_store, shell

from .env import _env


def _staging_dest(tag: str) -> Path:
    """~/restic-restore/<tag>/<basename-of-original-path> - flattened, not
    the full original absolute path. If the tag has no matching entry left
    in backup_targets.json (e.g. removed after backing up), falls back to
    using the tag itself as the folder name.
    """
    targets = backup_store.load()
    match = next((t for t in targets if t["name"] == tag), None)
    basename = Path(match["path"]).name if match else tag
    return Path(RESTORE_STAGING_DIR).expanduser() / tag / basename


def _original_dest(tag: str) -> Path | None:
    targets = backup_store.load()
    match = next((t for t in targets if t["name"] == tag), None)
    if not match:
        return None
    return Path(match["path"]).expanduser()


def restore_tag(tag: str, original: bool = False) -> bool:
    """Restore the LATEST snapshot for one tag. Returns True on success.

    Since `run()` backs up via `cd <target> && restic backup .`, a
    snapshot's root IS the target directory's own contents directly (no
    ancestor path components) - so `--target <dir>` places files straight
    into <dir>, not into <dir>/home/you/original/path. That's what makes
    both the flattened staging layout and "restore to original path" work
    simply: staging targets a synthetic <tag>/<basename> dir, "original"
    targets the real configured path directly - confirmed by testing.
    """
    if original:
        dest = _original_dest(tag)
        if dest is None:
            print(
                f"No target named '{tag}' in backup_targets.json - can't determine its\n"
                f"original path. Use the non-'-original' restore command instead, or run\n"
                f"'backup add {tag} <path>' first if you want it tracked again.",
                file=sys.stderr,
            )
            return False
        print(
            f"Restoring latest '{tag}' snapshot to its ORIGINAL location: {dest}\n"
            f"This overwrites any existing files there."
        )
    else:
        dest = _staging_dest(tag)
        print(f"Restoring latest '{tag}' snapshot to staging: {dest}")

    dest.mkdir(parents=True, exist_ok=True)
    result = shell.run(
        ["restic", "restore", "latest", "--tag", tag, "--target", str(dest)],
        check=False,
        env=_env(),
    )
    if result.returncode != 0:
        print(f"  (no snapshot found for '{tag}' yet, skipping)")
        return False
    return True


def restore_snapshot(snapshot_id: str) -> bool:
    """Restore an ARBITRARY snapshot (not necessarily the latest) into
    ~/restic-restore/<tag>-<snapshot_id>/ - flattened, just like
    restore_tag's staging mode, but for a specific snapshot ID from
    `backup snapshots` rather than always "whatever's newest". Looks up
    the snapshot's own tag automatically so you only need the ID.
    """
    result = shell.run_capture(
        ["restic", "snapshots", snapshot_id, "--json"], check=False, env=_env()
    )
    if result.returncode != 0:
        print(f"Could not find snapshot '{snapshot_id}'.", file=sys.stderr)
        return False

    snaps = json.loads(result.stdout or "[]")
    if not snaps:
        print(f"No snapshot found matching '{snapshot_id}'.")
        return False

    snap = snaps[0]
    tags = snap.get("tags") or []
    tag_label = "+".join(tags) if tags else "untagged"
    short_id = snap.get("short_id", snapshot_id)

    dest = Path(RESTORE_STAGING_DIR).expanduser() / f"{tag_label}-{short_id}"
    print(f"Restoring snapshot '{short_id}' (tag: {tag_label}) to staging: {dest}")

    dest.mkdir(parents=True, exist_ok=True)
    result = shell.run(
        ["restic", "restore", snapshot_id, "--target", str(dest)],
        check=False,
        env=_env(),
    )
    if result.returncode != 0:
        print(f"  restore failed for snapshot '{snapshot_id}'")
        return False
    return True


def restore_all(original: bool = False) -> None:
    """Restore the latest snapshot of EVERY configured target - each into
    its own <tag>/<basename> staging folder, or each into its own real
    original path, per `original`. Never a single shared destination -
    that would either collide different targets' files together (staging)
    or scatter them across the filesystem incorrectly (original, given how
    restic restore --target actually behaves - see restore_tag docstring).
    """
    targets = backup_store.load()
    if not targets:
        print("No backup targets configured.")
        return
    for t in targets:
        print()
        restore_tag(t["name"], original=original)
