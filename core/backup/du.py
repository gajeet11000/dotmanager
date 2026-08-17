from pathlib import Path

from core import shell

from .env import ALWAYS_COLLAPSE, COLLAPSE_DIRS_PATH, _resolve_targets


def _load_collapse_dirs() -> set[str]:
    if not COLLAPSE_DIRS_PATH.exists():
        return set(ALWAYS_COLLAPSE)
    names = {
        line.strip()
        for line in COLLAPSE_DIRS_PATH.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    return names | ALWAYS_COLLAPSE


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
