"""Applies a theme profile's waybar colors.

Rewrites ~/.config/waybar/colors/current.css (what style.css `@import`s)
with the contents of the theme's own themes/<name>/waybar/theme.css, then
fully restarts waybar rather than just signaling it. A SIGUSR2 reload only
re-runs waybar's own CSS provider (style.css's own "reload_style_on_change"
only watches style.css itself, not files it imports, so even that needs an
explicit nudge) -- it does not re-resolve GTK's underlying theme engine for
native widgets waybar doesn't style itself, like the tray's DBusMenu popup
(waybar is what renders that, not the app that owns the tray icon --
confirmed by restarting nm-applet alone doing nothing, while restarting
waybar fixed a stale-dark popup on a light theme). That only gets re-read
at process startup, so a real restart is required for the tray menu to
actually follow the active theme.

current.css is written straight to the live ~/.config/waybar/colors/ --
it's not part of dotfiles/waybar/'s stow package, so switching a theme
never touches anything git-tracked (see _livefile.py).
"""

import subprocess
import time
from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_FILE = Path.home() / ".config" / "waybar" / "colors" / "current.css"


def apply(profile: dict) -> bool:
    waybar_theme = profile.get("waybar_theme")
    theme_dir = profile.get("theme_dir")
    if not waybar_theme or theme_dir is None:
        return False

    theme_file = theme_dir / "waybar" / "theme.css"
    if not theme_file.exists():
        print(f"[waybar] no color file at {theme_file}, skipping")
        return False

    print(f"[waybar] waybar_theme={waybar_theme}")
    _livefile.write(CURRENT_FILE, theme_file.read_text())

    # Exit code 1 just means no waybar process was running -- fine, the
    # respawn below still starts a correctly-themed one.
    result = subprocess.run(["pkill", "-x", "waybar"])
    if result.returncode not in (0, 1):
        print(f"[waybar] pkill waybar exited {result.returncode}")
    else:
        time.sleep(0.3)  # let the old process release its layer surface

    subprocess.Popen(
        ["waybar"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    return True
