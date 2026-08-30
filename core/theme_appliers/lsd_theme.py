"""Applies a theme profile's lsd (ls deluxe) colors.

lsd's colors.yaml has no include/import mechanism (unlike kitty's `include`),
and it hardcodes its directory/file/symlink/device colors regardless of
theme (the `file-type` section is not user-configurable in lsd itself) --
only user/group/permission/attributes/date/size/inode/links/git-status are
themeable. This overwrites the file lsd actually reads
(dotfiles/lsd/.config/lsd/colors.yaml) with the contents of the profile's
colors/<lsd_theme>.yaml. lsd re-reads its config on every invocation, so
there's no reload step -- the next `lsd` just picks it up.
"""

from pathlib import Path

LSD_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "lsd"
    / ".config"
    / "lsd"
)
CURRENT_COLORS_FILE = LSD_DIR / "colors.yaml"
COLORS_DIR = LSD_DIR / "colors"


def apply(profile: dict) -> bool:
    lsd_theme = profile.get("lsd_theme")
    if not lsd_theme:
        return False

    theme_file = COLORS_DIR / f"{lsd_theme}.yaml"
    if not theme_file.exists():
        print(f"[lsd] no theme file at {theme_file}, skipping")
        return False

    print(f"[lsd] lsd_theme={lsd_theme}")
    CURRENT_COLORS_FILE.write_text(theme_file.read_text())
    return True
