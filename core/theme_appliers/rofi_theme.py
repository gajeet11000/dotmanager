"""Applies a theme profile's rofi (window switcher + app launcher) colors.

Rewrites ~/.config/rofi/colors/current.rasi -- which
application_launcher.rasi and window_switcher.rasi both `@import` -- with
the contents of the theme's own themes/<name>/rofi/theme.rasi. rofi has no
daemon to reload; it reads its config fresh on every invocation, so
there's nothing to signal.

current.rasi is written straight to the live ~/.config/rofi/colors/ --
it's not part of dotfiles/rofi/'s stow package, so switching a theme
never touches anything git-tracked (see _livefile.py).
"""

from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_FILE = Path.home() / ".config" / "rofi" / "colors" / "current.rasi"


def apply(profile: dict) -> bool:
    rofi_theme = profile.get("rofi_theme")
    theme_dir = profile.get("theme_dir")
    if not rofi_theme or theme_dir is None:
        return False

    theme_file = theme_dir / "rofi" / "theme.rasi"
    if not theme_file.exists():
        print(f"[rofi] no color file at {theme_file}, skipping")
        return False

    print(f"[rofi] rofi_theme={rofi_theme}")
    _livefile.write(CURRENT_FILE, theme_file.read_text())

    return True
