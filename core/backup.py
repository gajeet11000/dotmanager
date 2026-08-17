import json
import sys
from pathlib import Path

from config import (
    BACKUP_EXCLUDE_FILE,
    BW_RCLONE_CONFIG_ITEM_NAME,
    BW_RESTIC_ITEM_NAME,
    RCLONE_CONFIG_PATH,
    RCLONE_REMOTE,
    RCLONE_REPO_PATH,
    RESTORE_STAGING_DIR,
)
from core import backup_store, shell

EXCLUDE_FILE_PATH = Path(__file__).resolve().parent.parent / BACKUP_EXCLUDE_FILE


def _repo() -> str:
    return f"rclone:{RCLONE_REMOTE}:{RCLONE_REPO_PATH}"


def _env() -> dict:
    return {
        "RESTIC_REPOSITORY": _repo(),
        "RESTIC_PASSWORD_COMMAND": f'bw get password "{BW_RESTIC_ITEM_NAME}"',
    }


def _bw_unlocked() -> bool:
    result = shell.run_capture(["bw", "status"], check=False)
    return '"status":"unlocked"' in result.stdout


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


def check() -> bool:
    ok = True

    if shell.command_exists("restic"):
        print("[ok]   restic is installed")
    else:
        print(
            "[MISSING] restic is not installed. Install it with:\n"
            "          python3 main.py manage add restic\n"
            "          python3 main.py install essentials"
        )
        ok = False

    if shell.command_exists("rclone"):
        print("[ok]   rclone is installed")
        result = shell.run_capture(["rclone", "listremotes"], check=False)
        remotes = result.stdout.split()
        if f"{RCLONE_REMOTE}:" in remotes:
            print(f"[ok]   rclone remote '{RCLONE_REMOTE}' is configured")
        else:
            print(
                f"[MISSING] rclone remote '{RCLONE_REMOTE}' is not configured.\n"
                f"          Run 'python3 main.py backup bootstrap' to restore it from\n"
                f"          Bitwarden, or 'rclone config' to authorize it fresh."
            )
            ok = False
    else:
        print(
            "[MISSING] rclone is not installed. Install it with:\n"
            "          python3 main.py manage add rclone\n"
            "          python3 main.py install essentials"
        )
        ok = False

    if shell.command_exists("bw"):
        print("[ok]   bitwarden-cli (bw) is installed")
        if _bw_unlocked():
            print("[ok]   bitwarden vault is unlocked")
        else:
            print(
                "[MISSING] bitwarden vault isn't unlocked in this shell. Run:\n"
                "          bw login          (first time only on this machine)\n"
                '          export BW_SESSION="$(bw unlock --raw)"'
            )
            ok = False
    else:
        print(
            "[MISSING] bitwarden-cli (bw) is not installed. Install it with:\n"
            "          python3 main.py manage add bitwarden-cli/aur\n"
            "          python3 main.py install essentials"
        )
        ok = False

    return ok


def bootstrap() -> None:
    if not shell.command_exists("bw"):
        print(
            "[MISSING] bitwarden-cli (bw) is not installed. Install it with:\n"
            "          python3 main.py manage add bitwarden-cli/aur\n"
            "          python3 main.py install essentials"
        )
        return

    if not _bw_unlocked():
        print(
            "Bitwarden vault isn't unlocked yet. Run:\n"
            "  bw login          (first time only on this machine)\n"
            '  export BW_SESSION="$(bw unlock --raw)"\n'
            "then re-run 'backup bootstrap'."
        )
        return

    rclone_conf_path = Path(RCLONE_CONFIG_PATH).expanduser()
    if rclone_conf_path.exists():
        print(f"[ok]   {rclone_conf_path} already exists, leaving it as-is")
    else:
        note = shell.run_capture(
            ["bw", "get", "notes", BW_RCLONE_CONFIG_ITEM_NAME], check=False
        )
        if note.returncode != 0 or not note.stdout.strip():
            print(
                f"[MISSING] No Bitwarden secure note named '{BW_RCLONE_CONFIG_ITEM_NAME}'.\n"
                f"          One-time setup: run 'rclone authorize \"dropbox\"' on any device\n"
                f"          with a browser (e.g. your phone), finish 'rclone config' on this\n"
                f"          machine, then save ~/.config/rclone/rclone.conf's contents as a\n"
                f"          Bitwarden secure note under that exact name."
            )
            return
        rclone_conf_path.parent.mkdir(parents=True, exist_ok=True)
        rclone_conf_path.write_text(note.stdout)
        rclone_conf_path.chmod(0o600)
        print(f"[ok]   restored rclone config to {rclone_conf_path}")

    if not check():
        print("\nFix the items above, then re-run 'backup bootstrap'.", file=sys.stderr)
        return

    init()

    print("\nRestoring every configured target to its original location...")
    restore_all()

    print("\nDone.")


def restore_all(target: str = "/") -> None:
    targets = backup_store.load()
    if not targets:
        print("No backup targets configured.")
        return
    for t in targets:
        print(f"\nRestoring latest snapshot of '{t['name']}'...")
        result = shell.run(
            ["restic", "restore", "latest", "--tag", t["name"], "--target", target],
            check=False,
            env=_env(),
        )
        if result.returncode != 0:
            print(f"  (no snapshot found for '{t['name']}' yet, skipping)")


def init() -> None:
    if not check():
        print("\nFix the items above, then re-run 'backup init'.", file=sys.stderr)
        return
    probe = shell.run(["restic", "snapshots"], check=False, env=_env())
    if probe.returncode == 0:
        print(f"Repo '{_repo()}' is already initialized.")
        return
    print(f"Initializing restic repo at '{_repo()}'...")
    shell.run(["restic", "init"], env=_env())


def run(names: list[str]) -> None:
    if not check():
        print("\nFix the items above before running a backup.", file=sys.stderr)
        return

    targets = _resolve_targets(names)

    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return

    exclude_args = []
    if EXCLUDE_FILE_PATH.exists():
        exclude_args = ["--exclude-file", str(EXCLUDE_FILE_PATH)]

    skip_flag = ["--skip-if-unchanged"] if _supports_skip_if_unchanged() else []
    if not skip_flag:
        print(
            "Note: this restic version predates --skip-if-unchanged (added in 0.17) -\n"
            "      every run will create a snapshot even when nothing changed. Consider\n"
            "      upgrading restic to skip no-op snapshots automatically."
        )

    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(
                f"Warning: target '{t['name']}' path '{resolved}' doesn't exist, skipping"
            )
            continue
        # Run FROM the target directory and back up '.' rather than passing
        # the absolute path directly. restic still records (and restores
        # to) the correct absolute location either way - confirmed by
        # testing - but --skip-if-unchanged has a known bug where it
        # doesn't ignore metadata changes on ANCESTOR directories when
        # given an absolute path. Running relative to the target itself
        # sidesteps that entirely.
        cmd = ["restic", "backup", ".", "--tag", t["name"], *exclude_args, *skip_flag]
        shell.run(cmd, env=_env(), cwd=str(resolved))


def _supports_skip_if_unchanged() -> bool:
    # --skip-if-unchanged was added in restic 0.17.0. Older versions reject
    # the flag outright ("unknown flag"), so detect support rather than
    # assuming it - this keeps `run()` working on whatever restic version
    # happens to be installed.
    result = shell.run_capture(["restic", "backup", "--help"], check=False)
    return "--skip-if-unchanged" in result.stdout


def forget_tag(tag: str) -> None:
    """Wipes EVERY snapshot for a given tag (target name) entirely - not
    "keep the last N", all of them, gone. Doesn't touch backup_targets.json
    - the target itself still exists and 'backup run <tag>' will happily
    start a fresh history for it. Use 'backup remove' separately if you
    also want to stop tracking the target going forward.

    Deliberately doesn't use `restic forget --tag X --keep-last 0` - restic
    treats 0 as "no policy given" and silently does nothing (confirmed by
    testing), which would make this function a dangerous no-op. Instead we
    list the exact matching snapshot IDs ourselves and forget them by ID,
    which has no such ambiguity.
    """
    result = shell.run_capture(
        ["restic", "snapshots", "--tag", tag, "--json"], check=False, env=_env()
    )
    if result.returncode != 0:
        print(f"Could not list snapshots for tag '{tag}'.", file=sys.stderr)
        return

    snaps = json.loads(result.stdout or "[]")
    if not snaps:
        print(f"No snapshots found with tag '{tag}'.")
        return

    ids = [s["short_id"] for s in snaps]
    print(f"Forgetting {len(ids)} snapshot(s) tagged '{tag}': {', '.join(ids)}")
    shell.run(["restic", "forget", *ids], env=_env())

    print("\nPruning now-unreferenced data (this can take a while)...")
    shell.run(["restic", "prune"], env=_env())


def sizes(names: list[str], depth: int = 1) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return
    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(f"\n{t['name']} ({resolved}): doesn't exist, skipping")
            continue
        print(f"\n{t['name']} ({resolved}):")
        result = shell.run_capture(
            [
                "bash",
                "-c",
                f'du -h --max-depth={depth} -- "{resolved}" 2>/dev/null | sort -rh',
            ],
            check=False,
        )
        for line in result.stdout.splitlines():
            size, _, path = line.partition("\t")
            print(f"  {size:<8} {path}")


def snapshots() -> None:
    shell.run(["restic", "snapshots"], env=_env())


def stats() -> None:
    shell.run(["restic", "stats", "--mode", "raw-data"], env=_env())


def forget(keep_last: int) -> None:
    shell.run(
        ["restic", "forget", "--keep-last", str(keep_last), "--group-by", "host,tags"],
        env=_env(),
    )
    print("\nPruning now-unreferenced data (this can take a while)...")
    shell.run(["restic", "prune"], env=_env())


def restore(snapshot: str, target: str | None) -> None:
    dest = Path(target or RESTORE_STAGING_DIR).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    print(
        f"Restoring snapshot '{snapshot}' into '{dest}' "
        f"(original paths are recreated underneath it)..."
    )
    shell.run(["restic", "restore", snapshot, "--target", str(dest)], env=_env())
