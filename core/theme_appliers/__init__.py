"""Registry of per-application theme appliers.

Each applier is a function `apply(profile: dict) -> bool` that reads
whichever keys it cares about out of a theme profile (see
core.theme_manager.THEMES) and applies them to its one application, no-op'ing
(returning False) if none of its keys are present in that profile -- so a
theme can define only some apps and still be valid.

To add support for a new app (fish, yazi, ...):
  1. Add a module here with an `apply(profile) -> bool` function.
  2. Add its `apply` to POST_LIVE_APPLIERS below (see PRE_LIVE_APPLIERS'
     docstring for the one case where it belongs there instead).
  3. Add whatever profile key(s) it reads to the theme(s) in
     themes/*/theme.toml.
"""

from core.theme_appliers import (
    claude_theme,
    gtk_theme,
    herdr_theme,
    icon_theme,
    kitty_theme,
    lsd_theme,
    nvim_theme,
    qt_theme,
    rofi_theme,
    swaync_theme,
    waybar_theme,
)

# gtk_theme and icon_theme don't touch GTK live -- they only write fields
# into the nwg-look-managed gsettings file core.theme_appliers._nwg_look
# reads. core.theme_manager.set_theme() pushes that file live (nwg-look
# -a -x) once, after these two run and before POST_LIVE_APPLIERS.
PRE_LIVE_APPLIERS = [
    gtk_theme.apply,
    icon_theme.apply,
]

# Everything else. waybar_theme specifically depends on this ordering:
# it restarts waybar to force GTK to re-resolve the theme for native
# widgets it doesn't style itself (the tray's popup menu) -- restarting
# before the live push would just re-read the *previous* theme.
POST_LIVE_APPLIERS = [
    kitty_theme.apply,
    lsd_theme.apply,
    nvim_theme.apply,
    rofi_theme.apply,
    swaync_theme.apply,
    waybar_theme.apply,
    herdr_theme.apply,
    claude_theme.apply,
    qt_theme.apply,
]

APPLIERS = PRE_LIVE_APPLIERS + POST_LIVE_APPLIERS
