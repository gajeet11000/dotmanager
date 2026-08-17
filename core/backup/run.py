import sys
from pathlib import Path

from core import shell

from .check import check
from .env import (
    EXCLUDE_FILE_PATH,
    _env,
    _repo,
    _resolve_targets,
    _supports_skip_if_unchanged,
)


def init() -> None:
    if not check():
        print("\nFix the items above, then re-run 'backup init'.", file=sys.stderr)
        return

    # `restic snapshots` fails cleanly if the repo doesn't exist/isn't
    # initialized yet — use that to make init idempotent rather than
    # tracking init state ourselves.
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

    exclude_args = ["--exclude-file", str(EXCLUDE_FILE_PATH)]

    skip_flag = ["--skip-if-unchanged"] if _supports_skip_if_unchanged() else []
    if not skip_flag:
        print(
            "Note: this restic version predates --skip-if-unchanged (added in 0.17) -\n"
            "      every run will create a snapshot even when nothing changed. Consider\n"
            "      upgrading restic to skip no-op snapshots automatically."
        )

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
        # Run FROM the target directory and back up '.' rather than passing
        # the absolute path directly. restic still records (and restores
        # to) the correct absolute location either way - confirmed by
        # testing - but --skip-if-unchanged has a known bug where it
        # doesn't ignore metadata changes on ANCESTOR directories when
        # given an absolute path (e.g. an unrelated mtime change on ~ or
        # ~/Pictures would still trigger a new snapshot even though
        # nothing inside the actual target changed). Running relative to
        # the target itself sidesteps that entirely - verified this
        # actually prevents the false-positive snapshots.
        cmd = ["restic", "backup", ".", "--tag", t["name"], *exclude_args, *skip_flag]
        shell.run(cmd, env=_env(), cwd=str(resolved))
