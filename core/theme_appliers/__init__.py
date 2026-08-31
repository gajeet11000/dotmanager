"""Registry of per-application theme appliers.

Each applier is a function `apply(profile: dict) -> bool` that reads
whichever keys it cares about out of a theme profile (see
core.theme_manager.THEMES) and applies them to its one application, no-op'ing
(returning False) if none of its keys are present in that profile — so a
theme can define only some apps and still be valid.

To add support for a new app (fish, yazi, ...):
  1. Add a module here with an `apply(profile) -> bool` function.
  2. Add its `apply` to APPLIERS below.
  3. Add whatever profile key(s) it reads to the theme(s) in THEMES.
"""

from core.theme_appliers import (
    gtk_theme,
    icon_theme,
    kitty_theme,
    lsd_theme,
    nvim_theme,
    rofi_theme,
    swaync_theme,
    waybar_theme,
)

APPLIERS = [
    gtk_theme.apply,
    icon_theme.apply,
    kitty_theme.apply,
    lsd_theme.apply,
    nvim_theme.apply,
    rofi_theme.apply,
    swaync_theme.apply,
    waybar_theme.apply,
]
