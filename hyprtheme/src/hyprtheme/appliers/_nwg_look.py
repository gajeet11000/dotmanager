"""Shared plumbing for the built-in `gtk` and `icon` plugins: both patch
fields into an nwg-look-managed gsettings file, then need exactly one
shared "push it live" step afterwards -- not one each, since nwg-look's own
-a/-x both re-read and re-export *everything*, not just the fields that
changed. `ThemeManager` handles the batching (see manager.py's `live_push`
grouping); this module owns the two primitives it calls.
"""

import subprocess
from pathlib import Path


def patch_fields(gsettings_file: Path, **fields: str) -> None:
    """Rewrite the given `key=value` lines in nwg-look's gsettings file.

    Doesn't apply anything live -- ThemeManager calls apply_live() once
    after every app sharing this live_push group has patched its fields.
    """
    lines = gsettings_file.read_text().splitlines()
    remaining = dict(fields)
    new_lines = []
    for line in lines:
        key = line.split("=", 1)[0]
        if key in remaining:
            new_lines.append(f"{key}={remaining.pop(key)}")
        else:
            new_lines.append(line)
    if remaining:
        raise ValueError(
            f"field(s) {sorted(remaining)} not found in {gsettings_file} "
            "(nwg-look must -x export it at least once first)"
        )
    gsettings_file.write_text("\n".join(new_lines) + "\n")


def apply_live() -> None:
    """Push the patched file into gsettings/dconf (-a) and regenerate
    settings.ini/gtkrc-2.0/xsettingsd.conf (-x). No logout needed, as long
    as GTK_THEME is never exported by your compositor config.

    nwg-look's own INFO/WARN log lines are captured rather than streamed --
    they're noisy (every gsettings key, every run) and its logger doesn't
    play well piped through a non-tty subprocess. Silent on success; on
    failure the captured output is dumped so nothing goes missing.
    """
    for cmd in (["nwg-look", "-a"], ["nwg-look", "-x"]):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {' '.join(cmd)}")
            print(result.stdout, end="")
            print(result.stderr, end="")
            raise SystemExit(result.returncode)
