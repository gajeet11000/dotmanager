"""Applies a theme profile's waybar colors.

Rewrites dotfiles/waybar/.config/waybar/colors/current.css (what
style.css `@import`s) with the contents of the profile's
colors/<name>.css, then reloads waybar with SIGUSR2 (its default
"reload" action -- see `man waybar`). style.css's own
`"reload_style_on_change"` only watches style.css itself, not files it
imports, so an explicit reload is needed here (unlike kitty's plain
`include`, which kitty's own SIGUSR1 reload re-resolves fully).
"""

import subprocess
from pathlib import Path

COLORS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "waybar"
    / ".config"
    / "waybar"
    / "colors"
)
CURRENT_FILE = COLORS_DIR / "current.css"


def apply(profile: dict) -> bool:
    waybar_theme = profile.get("waybar_theme")
    if not waybar_theme:
        return False

    theme_file = COLORS_DIR / f"{waybar_theme}.css"
    if not theme_file.exists():
        print(f"[waybar] no color file at {theme_file}, skipping")
        return False

    print(f"[waybar] waybar_theme={waybar_theme}")
    CURRENT_FILE.write_text(theme_file.read_text())

    # Exit code 1 just means no waybar process was running -- fine.
    result = subprocess.run(["pkill", "-SIGUSR2", "-x", "waybar"])
    if result.returncode not in (0, 1):
        print(f"[waybar] pkill -SIGUSR2 waybar exited {result.returncode}")

    return True
