"""Applies a theme profile's rofi (window switcher + app launcher) colors.

Rewrites dotfiles/rofi/.config/rofi/colors/current.rasi -- which
application_launcher.rasi and window_switcher.rasi both `@import` -- with
the contents of the profile's colors/<name>.rasi. rofi has no daemon to
reload; it reads its config fresh on every invocation, so there's nothing
to signal.
"""

from pathlib import Path

COLORS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "rofi"
    / ".config"
    / "rofi"
    / "colors"
)
CURRENT_FILE = COLORS_DIR / "current.rasi"


def apply(profile: dict) -> bool:
    rofi_theme = profile.get("rofi_theme")
    if not rofi_theme:
        return False

    theme_file = COLORS_DIR / f"{rofi_theme}.rasi"
    if not theme_file.exists():
        print(f"[rofi] no color file at {theme_file}, skipping")
        return False

    print(f"[rofi] rofi_theme={rofi_theme}")
    CURRENT_FILE.write_text(theme_file.read_text())

    return True
