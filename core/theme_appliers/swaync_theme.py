"""Applies a theme profile's swaync (notification center) colors.

Rewrites ~/.config/swaync/style.css (the file swaync loads by convention)
to `@import` the theme's own themes/<name>/swaync/theme.css by absolute
file:// URL (the source file lives outside swaync's own dotfiles/ package,
so a bare relative path won't reach it), then live-reloads via
`swaync-client --reload-css` -- no restart needed. Each theme file itself
imports the packaged /etc/xdg/swaync/style.css first for the full
component layout, then overrides just the color variables.

style.css is written straight to the live ~/.config/swaync/ -- it's not
part of dotfiles/swaync/'s stow package (it has no permanent content of
its own; every switch fully rewrites it), so switching a theme never
touches anything git-tracked (see _livefile.py).
"""

import subprocess
from pathlib import Path

from core.theme_appliers import _livefile

STYLE_FILE = Path.home() / ".config" / "swaync" / "style.css"


def apply(profile: dict) -> bool:
    swaync_theme = profile.get("swaync_theme")
    theme_dir = profile.get("theme_dir")
    if not swaync_theme or theme_dir is None:
        return False

    theme_file = theme_dir / "swaync" / "theme.css"
    if not theme_file.exists():
        print(f"[swaync] no theme file at {theme_file}, skipping")
        return False

    print(f"[swaync] swaync_theme={swaync_theme}")
    _livefile.write(
        STYLE_FILE,
        "/* Rewritten by core/theme_appliers/swaync_theme.py on `dotmanager theme set`. */\n"
        f"@import url(\"file://{theme_file}\");\n",
    )

    # 1 = not running, 2 = running but reload failed some other way -- both
    # fine, swaync picks up the new style.css on its own next start/reload.
    result = subprocess.run(["swaync-client", "--reload-css"], capture_output=True)
    if result.returncode not in (0, 1, 2):
        print(f"[swaync] swaync-client --reload-css exited {result.returncode}")

    return True
