"""Applies a theme profile's waybar colors.

Rewrites dotfiles/waybar/.config/waybar/colors/current.css (what
style.css `@import`s) with the contents of the profile's
colors/<name>.css, then fully restarts waybar rather than just
signaling it. A SIGUSR2 reload only re-runs waybar's own CSS provider
(style.css's own "reload_style_on_change" only watches style.css
itself, not files it imports, so even that needs an explicit nudge) --
it does not re-resolve GTK's underlying theme engine for native widgets
waybar doesn't style itself, like the tray's DBusMenu popup (waybar is
what renders that, not the app that owns the tray icon -- confirmed by
restarting nm-applet alone doing nothing, while restarting waybar fixed
a stale-dark popup on a light theme). That only gets re-read at process
startup, so a real restart is required for the tray menu to actually
follow the active theme.
"""

import subprocess
import time
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
