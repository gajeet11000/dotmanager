import json
import sys
from pathlib import Path

from config import PREVIEW_SCRATCH_REPO
from core import shell

from .env import ALWAYS_COLLAPSE, EXCLUDE_FILE_PATH, _human_size, _resolve_targets


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
