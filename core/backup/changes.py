import json
import sys
from pathlib import Path

from core import shell

from .check import check
from .env import EXCLUDE_FILE_PATH, _env, _resolve_targets
from .preview import _human_size


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
