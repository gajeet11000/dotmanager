"""Applies a theme profile's lsd (ls deluxe) colors.

lsd's colors.yaml has no include/import mechanism (unlike kitty's `include`),
and it hardcodes its directory/file/symlink/device colors regardless of
theme (the `file-type` section is not user-configurable in lsd itself) --
only user/group/permission/attributes/date/size/inode/links/git-status are
themeable. This overwrites the file lsd actually reads
(~/.config/lsd/colors.yaml) with the contents of the theme's own
themes/<name>/lsd/theme.yaml. lsd re-reads its config on every invocation,
so there's no reload step -- the next `lsd` just picks it up.

colors.yaml is written straight to the live ~/.config/lsd/ -- it's not
part of dotfiles/lsd/'s stow package, so switching a theme never touches
anything git-tracked (see _livefile.py).
"""

from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_COLORS_FILE = Path.home() / ".config" / "lsd" / "colors.yaml"


def apply(profile: dict) -> bool:
    lsd_theme = profile.get("lsd_theme")
    theme_dir = profile.get("theme_dir")
    if not lsd_theme or theme_dir is None:
        return False

    theme_file = theme_dir / "lsd" / "theme.yaml"
    if not theme_file.exists():
        print(f"[lsd] no theme file at {theme_file}, skipping")
        return False

    print(f"[lsd] lsd_theme={lsd_theme}")
    _livefile.write(CURRENT_COLORS_FILE, theme_file.read_text())
    return True
