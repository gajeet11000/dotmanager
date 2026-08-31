"""Applies a theme profile's swaync (notification center) colors.

Rewrites dotfiles/swaync/.config/swaync/style.css (the file swaync loads by
convention from ~/.config/swaync/) to `@import` the profile's
themes/<name>.css, then live-reloads via `swaync-client --reload-css` --
no restart needed. Each theme file itself imports the packaged
/etc/xdg/swaync/style.css first for the full component layout, then
overrides just the color variables.
"""

import subprocess
from pathlib import Path

SWAYNC_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "swaync"
    / ".config"
    / "swaync"
)
STYLE_FILE = SWAYNC_DIR / "style.css"
THEMES_DIR = SWAYNC_DIR / "themes"


def apply(profile: dict) -> bool:
    swaync_theme = profile.get("swaync_theme")
    if not swaync_theme:
        return False

    theme_file = THEMES_DIR / f"{swaync_theme}.css"
    if not theme_file.exists():
        print(f"[swaync] no theme file at {theme_file}, skipping")
        return False

    print(f"[swaync] swaync_theme={swaync_theme}")
    STYLE_FILE.write_text(
        "/* Rewritten by core/theme_appliers/swaync_theme.py on `dotmanager theme set`. */\n"
        f"@import 'themes/{swaync_theme}.css';\n"
    )

    # Non-zero just means swaync isn't running -- fine, it'll pick up the
    # new style.css whenever it does start.
    subprocess.run(["swaync-client", "--reload-css"], capture_output=True)

    return True
