import json
import sys

from core import shell

from .env import _env


def snapshots() -> None:
    shell.run(["restic", "snapshots"], env=_env())


def stats() -> None:
    # raw-data mode = actual bytes stored in the repo across all snapshots,
    # post-dedup and post-compression - this is what counts against your
    # Dropbox quota, unlike the per-snapshot numbers `backup run` prints.
    shell.run(["restic", "stats", "--mode", "raw-data"], env=_env())


def forget(keep_last: int) -> None:
    # Excludes only affect FUTURE backups. Old snapshots taken before you
    # added an exclude pattern still reference the old (larger) data, so
    # `backup stats` won't shrink until you both forget the snapshots you
    # no longer need AND prune - forget alone just drops the snapshot
    # record, prune is the step that actually deletes now-unreferenced
    # data from the repo (and therefore from Dropbox).
    #
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
