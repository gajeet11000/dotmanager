"""Applies a theme profile's kitty terminal colorscheme.

Colors live in dotfiles/kitty/.config/kitty/themes/<name>.conf, one file
per theme. kitty.conf itself just does `include current-theme.conf` --
this rewrites that one-line pointer file to include the profile's theme,
then reloads every running kitty instance with SIGUSR1 (kitty reloads its
config on that signal by itself; no remote-control socket needed, no
restart, no logout).
"""

import subprocess
from pathlib import Path

KITTY_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "kitty"
    / ".config"
    / "kitty"
)
CURRENT_THEME_FILE = KITTY_DIR / "current-theme.conf"
THEMES_DIR = KITTY_DIR / "themes"


def apply(profile: dict) -> bool:
    kitty_theme = profile.get("kitty_theme")
    if not kitty_theme:
        return False

    theme_file = THEMES_DIR / f"{kitty_theme}.conf"
    if not theme_file.exists():
        print(f"[kitty] no theme file at {theme_file}, skipping")
        return False

    print(f"[kitty] kitty_theme={kitty_theme}")
    CURRENT_THEME_FILE.write_text(f"include themes/{kitty_theme}.conf\n")

    # Exit code 1 just means no kitty process was running to reload -- fine.
    result = subprocess.run(["pkill", "-USR1", "-x", "kitty"])
    if result.returncode not in (0, 1):
        print(f"[kitty] pkill -USR1 kitty exited {result.returncode}")

    return True
