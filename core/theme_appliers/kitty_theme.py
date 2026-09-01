"""Applies a theme profile's kitty terminal colorscheme.

Colors live in themes/<name>/kitty/theme.conf, one file per theme. kitty's
own kitty.conf just does `include current-theme.conf` -- this rewrites
that one-line pointer file to include the theme's file by absolute path
(kitty's `include` accepts either, and the source file lives outside
kitty's own dotfiles/ package, so relative won't reach it), then reloads
every running kitty instance with SIGUSR1 (kitty reloads its config on
that signal by itself; no remote-control socket needed, no restart, no
logout).

current-theme.conf itself is written straight to the live
~/.config/kitty/ -- it's not part of dotfiles/kitty/'s stow package, so
switching a theme never touches anything git-tracked (see _livefile.py).
"""

import subprocess
from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_THEME_FILE = Path.home() / ".config" / "kitty" / "current-theme.conf"


def apply(profile: dict) -> bool:
    kitty_theme = profile.get("kitty_theme")
    theme_dir = profile.get("theme_dir")
    if not kitty_theme or theme_dir is None:
        return False

    theme_file = theme_dir / "kitty" / "theme.conf"
    if not theme_file.exists():
        print(f"[kitty] no theme file at {theme_file}, skipping")
        return False

    print(f"[kitty] kitty_theme={kitty_theme}")
    _livefile.write(CURRENT_THEME_FILE, f"include {theme_file}\n")

    # Exit code 1 just means no kitty process was running to reload -- fine.
    result = subprocess.run(["pkill", "-USR1", "-x", "kitty"])
    if result.returncode not in (0, 1):
        print(f"[kitty] pkill -USR1 kitty exited {result.returncode}")

    return True
