import sys
from pathlib import Path

from config import (
    BACKUP_EXCLUDE_FILE,
    RCLONE_REMOTE,
    RCLONE_REPO_PATH,
    RESTORE_STAGING_DIR,
)
from core import backup_store, shell

# Module-level so tests can point these elsewhere, same pattern as
# fstab.FSTAB_PATH / sddm.SDDM_CONF_PATH.
EXCLUDE_FILE_PATH = Path(__file__).resolve().parent.parent / BACKUP_EXCLUDE_FILE

PASSWORD_NOTE = (
    "restic will prompt you for the repository password on the terminal —\n"
    "paste it in from wherever you keep it (e.g. Bitwarden's browser extension).\n"
    "To avoid re-entering it for every command in this session, you can instead:\n"
    "  export RESTIC_PASSWORD='...'\n"
    "dotmanager never reads, stores, or auto-fetches this password itself."
)


def _repo() -> str:
    # restic's native rclone backend: restic drives rclone itself, so there's
    # no separate "sync" step — `backup run` IS the sync.
    return f"rclone:{RCLONE_REMOTE}:{RCLONE_REPO_PATH}"


def _env() -> dict:
    # Deliberately just the repo location. Password comes from restic's own
    # interactive prompt, or from RESTIC_PASSWORD if the user exported it
    # themselves — never handled by dotmanager.
    return {"RESTIC_REPOSITORY": _repo()}


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


# ---- prerequisite checks ------------------------------------------------


def check() -> bool:
    """Prints exactly what's missing/needed before init/run will work.

    Returns True only if everything required is actually ready to go.
    """
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
                f"          This needs a browser once per machine: run 'rclone config'\n"
                f"          and create a remote named '{RCLONE_REMOTE}' (type: dropbox)."
            )
            ok = False
    else:
        print(
            "[MISSING] rclone is not installed. Install it with:\n"
            "          python3 main.py manage add rclone\n"
            "          python3 main.py install essentials"
        )
        ok = False

    print(f"[info] {PASSWORD_NOTE}")

    return ok


# ---- repo lifecycle -------------------------------------------------------


def init() -> None:
    if not check():
        print("\nFix the items above, then re-run 'backup init'.", file=sys.stderr)
        return

    # `restic snapshots` fails cleanly if the repo doesn't exist/isn't
    # initialized yet — use that to make init idempotent rather than
    # tracking init state ourselves. This will prompt for the password.
    probe = shell.run(["restic", "snapshots"], check=False, env=_env())
    if probe.returncode == 0:
        print(f"Repo '{_repo()}' is already initialized.")
        return

    print(f"Initializing restic repo at '{_repo()}'...")
    shell.run(["restic", "init"], env=_env())


# ---- backup / restore ------------------------------------------------------


def run(names: list[str]) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return

    exclude_args = []
    if EXCLUDE_FILE_PATH.exists():
        exclude_args = ["--exclude-file", str(EXCLUDE_FILE_PATH)]

    # One restic invocation PER target, each tagged with the target name,
    # rather than one invocation covering whatever subset of targets you
    # passed in. This keeps every target's snapshot history independent -
    # `backup run zen-profile` today and `backup run` (all) tomorrow no
    # longer produce snapshots restic sees as unrelated histories, which is
    # what silently broke `backup forget`'s retention policy.
    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(
                f"Warning: target '{t['name']}' path '{resolved}' doesn't exist, skipping"
            )
            continue
        cmd = ["restic", "backup", str(resolved), "--tag", t["name"], *exclude_args]
        shell.run(cmd, env=_env())


def snapshots() -> None:
    shell.run(["restic", "snapshots"], env=_env())


def stats() -> None:
    shell.run(["restic", "stats", "--mode", "raw-data"], env=_env())


def forget(keep_last: int) -> None:
    # --group-by host,tags: since each target now gets its own tagged
    # snapshot (see run()), grouping by tag means retention is per-target -
    # keep-last N keeps the N most recent snapshots of EACH target
    # independently, so backing up only 'screenshots' today can't cause an
    # older but only-existing 'zen-profile' snapshot to be forgotten.
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


def sizes(names: list[str]) -> None:
    """Per-target, per-subdirectory size breakdown (via `du`) so you can see
    exactly what's eating space before deciding what to add to the exclude
    file. Doesn't touch restic/rclone at all — pure local disk inspection.
    """
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
        # Biggest-first breakdown of immediate children.
        result = shell.run_capture(
            [
                "bash",
                "-c",
                f'du -h --max-depth=1 -- "{resolved}" 2>/dev/null | sort -rh',
            ],
            check=False,
        )
        for line in result.stdout.splitlines():
            size, _, path = line.partition("\t")
            print(f"  {size:<8} {path}")
