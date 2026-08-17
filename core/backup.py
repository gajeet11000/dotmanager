import json
import sys
from pathlib import Path

from config import (
    BACKUP_COLLAPSE_DIRS_FILE,
    BACKUP_EXCLUDE_FILE,
    BW_RCLONE_CONFIG_ITEM_NAME,
    BW_RESTIC_ITEM_NAME,
    PREVIEW_SCRATCH_REPO,
    RCLONE_CONFIG_PATH,
    RCLONE_REMOTE,
    RCLONE_REPO_PATH,
    RESTORE_STAGING_DIR,
)
from core import backup_store, shell

# Module-level so tests can point these elsewhere, same pattern as
# fstab.FSTAB_PATH / sddm.SDDM_CONF_PATH.
EXCLUDE_FILE_PATH = Path(__file__).resolve().parent.parent / BACKUP_EXCLUDE_FILE

COLLAPSE_DIRS_PATH = Path(__file__).resolve().parent.parent / BACKUP_COLLAPSE_DIRS_FILE

ALWAYS_COLLAPSE = {".git"}


def _load_collapse_dirs() -> set[str]:
    if not COLLAPSE_DIRS_PATH.exists():
        return set(ALWAYS_COLLAPSE)
    names = {
        line.strip()
        for line in COLLAPSE_DIRS_PATH.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    return names | ALWAYS_COLLAPSE


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


def _preview_env() -> dict:
    return {
        "RESTIC_REPOSITORY": str(Path(PREVIEW_SCRATCH_REPO).expanduser()),
        "RESTIC_PASSWORD": "dotmanager-local-preview-scratch-not-a-real-secret",
    }


def _ensure_preview_repo() -> None:
    repo_path = Path(PREVIEW_SCRATCH_REPO).expanduser()
    if (repo_path / "config").exists():
        return
    repo_path.mkdir(parents=True, exist_ok=True)
    shell.run(["restic", "init"], env=_preview_env(), check=False)


def _bw_unlocked() -> bool:
    result = shell.run_capture(["bw", "status"], check=False)
    return '"status":"unlocked"' in result.stdout


def _supports_skip_if_unchanged() -> bool:
    # --skip-if-unchanged was added in restic 0.17.0. Older versions reject
    # the flag outright ("unknown flag"), so detect support rather than
    # assuming it - this keeps `run()` working on whatever restic version
    # happens to be installed.
    result = shell.run_capture(["restic", "backup", "--help"], check=False)
    return "--skip-if-unchanged" in result.stdout


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


# ---- fresh-machine bootstrap ---------------------------------------------


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


def bootstrap() -> None:
    """For a freshly installed machine: pulls the already-authorized rclone
    Dropbox config out of Bitwarden (so there's no OAuth/browser step),
    then inits (if needed) and restores every configured target to its
    real original location.

    Requires 'bw login' + 'export BW_SESSION=...' to have been run already
    in this shell - that's the one unavoidable manual step, since only you
    can type your master password.
    """
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
    restore_all(original=True)

    print("\nDone.")


# ---- repo lifecycle -------------------------------------------------------


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


# ---- backup / restore ------------------------------------------------------


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


def changes(names: list[str], paths: list[str] | None = None) -> None:
    """Shows exactly which files are NEW or CHANGED compared to the latest
    snapshot for each target's tag - i.e. what `backup run` would actually
    upload right now. This is a different question from `preview` (which
    ignores snapshot history entirely and just answers "what survives
    exclusion") - this one genuinely needs your real Dropbox-backed repo,
    since it's comparing against actual history, so it requires internet
    and bw unlocked, unlike `preview`.

    Trusts restic's own per-file size here (unlike preview/_included_paths)
    since restic DOES report real data_size for 'new' and 'changed' files -
    the zeroed-out-size quirk only affects already-'unchanged' files, which
    this command isn't interested in anyway.

    `paths`, if given, restricts this to specific subpaths within each
    target, same as `du`/`preview`.
    """
    if not check():
        print("\nFix the items above before checking for changes.", file=sys.stderr)
        return

    targets = _resolve_targets(names)
    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return

    exclude_args = []
    if EXCLUDE_FILE_PATH.exists():
        exclude_args = ["--exclude-file", str(EXCLUDE_FILE_PATH)]

    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(f"\n{t['name']} ({resolved}): doesn't exist, skipping")
            continue

        scan_targets = paths if paths else ["."]
        result = shell.run_capture(
            [
                "restic",
                "backup",
                *scan_targets,
                "--tag",
                t["name"],
                "--dry-run",
                "--json",
                "--verbose=2",
                *exclude_args,
            ],
            check=False,
            env=_env(),
            cwd=str(resolved),
        )

        new_files, changed_files = [], []
        for line in result.stdout.splitlines():
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("message_type") != "verbose_status":
                continue
            item = msg.get("item", "")
            if not item or item.endswith("/"):
                continue  # directories and the scan_finished marker - files only
            action = msg.get("action")
            size = msg.get("data_size", 0)
            if action == "new":
                new_files.append((size, item.lstrip("/")))
            elif action in ("changed", "modified"):
                # restic's JSON action naming for "content differs from the
                # parent snapshot" isn't stable across versions - 0.16.x
                # reports "modified", 0.19.x reports "changed" (confirmed
                # by testing both directly). Accept either so this doesn't
                # silently miss edited files depending on restic version.
                changed_files.append((size, item.lstrip("/")))

        print(f"\n{t['name']} ({resolved}):")
        if not new_files and not changed_files:
            print("  No changes since the last snapshot.")
            continue

        if new_files:
            print(f"  New ({len(new_files)}):")
            for size, item in sorted(new_files, reverse=True):
                print(f"    {_human_size(size):<8} {item}")
        if changed_files:
            print(f"  Changed ({len(changed_files)}):")
            for size, item in sorted(changed_files, reverse=True):
                print(f"    {_human_size(size):<8} {item}")

        total = sum(s for s, _ in new_files) + sum(s for s, _ in changed_files)
        print(
            f"  Total to upload: {_human_size(total)} "
            f"({len(new_files)} new, {len(changed_files)} changed)"
        )


def _human_size(n: int) -> str:
    """Rough du -h equivalent for a raw byte count."""
    size = float(n)
    for unit in ["B", "K", "M", "G", "T"]:
        if size < 1024 or unit == "T":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}{unit}"
        size /= 1024
    return f"{size:.1f}T"


def _included_paths(resolved: Path, scan_paths: list[str] | None = None) -> list[Path]:
    """Ask restic itself (via --dry-run) which files under `resolved` would
    actually be included in a backup right now, respecting
    backup_excludes.txt exactly as `run()` applies it - including negation
    rules, which we couldn't safely reimplement ourselves without risking
    a subtly different result from what a real `backup run` would do.

    Runs against a throwaway LOCAL scratch repo (see _preview_env), not
    your real Dropbox-backed one - confirmed by testing that a completely
    empty, brand-new local repo still applies exclude patterns correctly,
    since that matching is purely a function of the files on disk and the
    exclude file, independent of snapshot history. This is what makes
    `preview` work fully offline: it was never actually asking "what's
    different from my last Dropbox snapshot", only "what would exclusion
    leave behind" - so it has no business needing Dropbox/bw at all.

    `scan_paths`, if given, restricts the scan to specific subpaths
    (relative to `resolved`) instead of the whole target - e.g. only
    'stow-dotfiles/' and 'some_project/' rather than all of ~/Documents.

    Deliberately does NOT trust restic's own per-file size in this output:
    for files restic considers already-unchanged, the real size just isn't
    present in the dry-run JSON stream - only an aggregate total is. So we
    use this purely to get the INCLUDED path list, then stat() each file
    ourselves for a reliable size regardless of new/changed/unchanged.
    """
    _ensure_preview_repo()
    exclude_args = []
    if EXCLUDE_FILE_PATH.exists():
        exclude_args = ["--exclude-file", str(EXCLUDE_FILE_PATH)]
    targets_arg = scan_paths if scan_paths else ["."]
    result = shell.run_capture(
        [
            "restic",
            "backup",
            *targets_arg,
            "--dry-run",
            "--json",
            "--verbose=2",
            *exclude_args,
        ],
        check=False,
        env=_preview_env(),
        cwd=str(resolved),
    )
    paths = []
    for line in result.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("message_type") != "verbose_status":
            continue
        item = msg.get("item", "")
        if not item or item.endswith("/"):
            continue  # directory entries and the scan_finished marker - files only
        paths.append(resolved / item.lstrip("/"))
    return paths


def _build_size_tree(base: Path, paths: list[Path], depth: int) -> dict:
    """`depth` counts total nesting levels shown, directories AND files
    together - once a directory has no more subdirectories to descend
    into (e.g. a flat folder of scripts), the individual files themselves
    become the next level, rather than the breakdown just stopping at an
    opaque directory-total with leftover depth budget unused.
    """
    root = {"size": 0, "children": {}}
    for p in paths:
        try:
            size = p.stat().st_size
        except OSError:
            continue
        root["size"] += size
        node = root
        rel_parts = p.relative_to(base).parts
        for part in rel_parts[:depth]:
            node = node["children"].setdefault(part, {"size": 0, "children": {}})
            node["size"] += size
            if part in ALWAYS_COLLAPSE:
                break
    return root


def _print_included_tree(node: dict, level: int = 0) -> None:
    items = sorted(node["children"].items(), key=lambda kv: kv[1]["size"], reverse=True)
    for name, child in items:
        print(f"  {'  ' * level}{_human_size(child['size']):<8} {name}")
        _print_included_tree(child, level + 1)
    if level == 0 and items:
        print()


def preview(names: list[str], depth: int = 2, paths: list[str] | None = None) -> None:
    """Shows exactly what WOULD be uploaded by `backup run` right now -
    after backup_excludes.txt is applied - with real sizes, grouped by
    directory. Unlike `backup du` (raw disk usage, no exclusions), this
    reflects the actual post-exclusion picture.

    Fully offline/local: it only needs restic itself (to apply the exclude
    patterns via a throwaway local scratch repo) and local disk access -
    no rclone remote, no bw unlock, no Dropbox connectivity, unlike every
    other backup subcommand. See _included_paths for why that's safe.

    `paths`, if given, restricts this to specific subpaths within each
    target (e.g. --path stow-dotfiles/ some_project/) instead of the
    target's entire tree.
    """
    if not shell.command_exists("restic"):
        print(
            "[MISSING] restic is not installed. Install it with:\n"
            "          python3 main.py manage add restic\n"
            "          python3 main.py install essentials",
            file=sys.stderr,
        )
        return

    targets = _resolve_targets(names)
    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return

    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(f"\n{t['name']} ({resolved}): doesn't exist, skipping")
            continue
        print(f"\n{t['name']} ({resolved}) - would back up:")

        if paths:
            for rel in paths:
                sub = resolved / rel
                if not sub.exists():
                    print(f"\n  {rel}: doesn't exist, skipping")
                    continue
                print(f"\n  -- {rel} --")
                included = _included_paths(resolved, scan_paths=[rel])
                tree = _build_size_tree(sub, included, depth)
                print(
                    f"    {_human_size(tree['size']):<8} (total, {len(included)} files, after exclusions)"
                )
                _print_included_tree(tree, level=1)
        else:
            included = _included_paths(resolved)
            tree = _build_size_tree(resolved, included, depth)
            print(
                f"  {_human_size(tree['size']):<8} (total, {len(included)} files, after exclusions)"
            )
            _print_included_tree(tree)


def _du_children(path: str) -> list[tuple[str, str]]:
    """Immediate children of `path` with their sizes (via `du`), sorted
    biggest-first. Excludes the self-total line `du` also reports.

    Uses -a so this returns individual FILES as well as subdirectories -
    matching `preview`'s behavior (see _build_size_tree): once a directory
    has no further subdirectories to descend into, its individual files
    become the next level shown instead of the breakdown just stopping at
    an opaque total. Recursion in _print_size_tree naturally only descends
    further into entries that ARE directories - a file returned here is
    already a leaf, `du` won't return further "children" for it.
    """
    result = shell.run_capture(
        ["bash", "-c", f'du -ah --max-depth=1 -- "{path}" 2>/dev/null | sort -rh'],
        check=False,
    )
    children = []
    for line in result.stdout.splitlines():
        size, _, p = line.partition("\t")
        if p.rstrip("/") == path.rstrip("/"):
            continue
        children.append((size, p))
    return children


def _print_size_tree(
    path: str, max_depth: int, level: int = 0, collapse: set[str] | None = None
) -> None:
    """Depth-first, indented breakdown: every subdirectory's own children
    print immediately underneath it (sorted biggest-first among siblings).
    Shows only each entry's own name, not the full path repeated at every
    level - that's what actually caused long lines to wrap on narrow
    terminals before; indentation itself is only a couple characters per
    level and isn't the problem once the redundant path prefix is gone.
    """
    children = _du_children(path)
    for size, child in children:
        name = Path(child).name
        print(f"  {'  ' * level}{size:<8} {name}")
        if collapse and name in collapse:
            continue
        if level + 1 < max_depth:
            _print_size_tree(child, max_depth, level + 1, collapse)
    if level == 0 and children:
        print()


def sizes(names: list[str], depth: int = 1, paths: list[str] | None = None) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No matching backup targets. Use 'backup add <name> <path>' first.")
        return

    collapse = _load_collapse_dirs()

    for t in targets:
        resolved = Path(t["path"]).expanduser()
        if not resolved.exists():
            print(f"\n{t['name']} ({resolved}): doesn't exist, skipping")
            continue
        print(f"\n{t['name']} ({resolved}):")

        if paths:
            for rel in paths:
                sub = resolved / rel
                if not sub.exists():
                    print(f"\n  {rel}: doesn't exist, skipping")
                    continue
                print(f"\n  -- {rel} --")
                total = shell.run_capture(
                    ["bash", "-c", f'du -sh -- "{sub}" 2>/dev/null'], check=False
                ).stdout
                size, _, _ = total.partition("\t")
                print(f"    {size.strip():<8} (total)")
                _print_size_tree(str(sub), depth, level=1, collapse=collapse)
        else:
            total = shell.run_capture(
                ["bash", "-c", f'du -sh -- "{resolved}" 2>/dev/null'], check=False
            ).stdout
            size, _, _ = total.partition("\t")
            print(f"  {size.strip():<8} (total)")
            _print_size_tree(str(resolved), depth, collapse=collapse)


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
