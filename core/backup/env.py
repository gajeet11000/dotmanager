import sys
from pathlib import Path

from config import (
    BACKUP_COLLAPSE_DIRS_FILE,
    BACKUP_EXCLUDE_FILE,
    BW_RESTIC_ITEM_NAME,
    RCLONE_REMOTE,
    RCLONE_REPO_PATH,
)
from core import backup_store, shell

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

EXCLUDE_FILE_PATH = PROJECT_ROOT / BACKUP_EXCLUDE_FILE
COLLAPSE_DIRS_PATH = PROJECT_ROOT / BACKUP_COLLAPSE_DIRS_FILE

ALWAYS_COLLAPSE = {".git"}

if not EXCLUDE_FILE_PATH.exists():
    raise FileNotFoundError(
        f"backup_excludes.txt not found at {EXCLUDE_FILE_PATH}\n"
        f"This file is required - it controls what actually leaves your machine, "
        f"so a missing file is treated as a hard error rather than 'no excludes'. "
        f"It's fine for it to be empty, it just has to exist:\n"
        f"  touch {EXCLUDE_FILE_PATH}"
    )

def _bw_unlocked() -> bool:
    result = shell.run_capture(["bw", "status"], check=False)
    return '"status":"unlocked"' in result.stdout


def _repo() -> str:
    # restic's native rclone backend: restic drives rclone itself, so there's
    # no separate "sync" step — `backup run` IS the sync.
    return f"rclone:{RCLONE_REMOTE}:{RCLONE_REPO_PATH}"


def _env() -> dict:
    return {
        "RESTIC_REPOSITORY": _repo(),
        # `bw` is a standalone terminal tool (email + master password + 2FA,
        # all typed directly into the shell) - it does NOT need the browser
        # extension. This is what makes the whole chain work from a bare
        # fresh-install TTY: nothing here requires a browser to exist.
        "RESTIC_PASSWORD_COMMAND": f'bw get password "{BW_RESTIC_ITEM_NAME}"',
    }


def _supports_skip_if_unchanged() -> bool:
    # --skip-if-unchanged was added in restic 0.17.0. Older versions reject
    # the flag outright ("unknown flag"), so detect support rather than
    # assuming it - this keeps `run()` working on whatever restic version
    # happens to be installed.
    result = shell.run_capture(["restic", "backup", "--help"], check=False)
    return "--skip-if-unchanged" in result.stdout


def _human_size(n: int) -> str:
    """Rough du -h equivalent for a raw byte count."""
    size = float(n)
    for unit in ["B", "K", "M", "G", "T"]:
        if size < 1024 or unit == "T":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}{unit}"
        size /= 1024
    return f"{size:.1f}T"


def _resolve_targets(names: list[str]) -> list[dict]:
    all_targets = backup_store.load()
    if not all_targets:
        return []
    if names == ["all"]:
        return all_targets
    by_name = {t["name"]: t for t in all_targets}
    resolved = []
    for name in names:
        if name not in by_name:
            print(
                f"Warning: no backup target named '{name}', skipping", file=sys.stderr
            )
            continue
        resolved.append(by_name[name])
    return resolved
