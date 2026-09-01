"""Applies a theme profile's icon theme: light/dark variant + accent color.

Two independent mechanisms live here:
  - icon_theme (Papirus-Dark / Papirus-Light): an nwg-look-managed gsettings
    field, same delivery path as the GTK theme.
  - icon_accent: restored from a pre-baked symlink snapshot under
    themes/<name>/icons/ (see scripts/bake_icon_accents.py), rather than
    calling papirus-folders live. papirus-folders is slow (rebuilds
    gtk-update-icon-cache for Papirus *and* every sibling variant, no flag
    to opt out) and has its own bug where folder-videos.svg -- a symlink
    alias to folder-video.svg for most colors -- never gets repointed,
    since its color-swap logic skips anything that's already a symlink.
    Baking once (fixing the bug in the process) and restoring a snapshot
    sidesteps both: it's just a fast tar extract + one targeted cache
    rebuild, fast enough to run synchronously.

Both the tar extract and the cache rebuild need root. When `theme set`
runs from an interactive terminal, sudo can just prompt. When it runs
from somewhere with no terminal attached -- the rofi theme switcher's
keybind, for instance -- there's nothing to prompt, so it needs a
NOPASSWD sudoers rule for these exact commands (see
assets/sudoers/dotmanager-theme). That rule is scoped to extracting
.tar files already inside this repo's themes/*/icons/ and rebuilding
the cache for exactly Papirus-Dark/Papirus-Light -- it doesn't grant
anything a user who already owns this repo's files couldn't already do.
"""

from core import shell
from core.theme_appliers import _nwg_look


def apply(profile: dict) -> bool:
    changed = False

    if "icon_theme" in profile:
        print(f"[icons] icon-theme={profile['icon_theme']}")
        _nwg_look.patch_fields(**{"icon-theme": profile["icon_theme"]})
        changed = True

    if "icon_accent" in profile:
        icon_theme = profile.get("icon_theme", "Papirus-Dark")
        accent = profile["icon_accent"]
        theme_dir = profile.get("theme_dir")
        archive = theme_dir / "icons" / f"{accent}__{icon_theme}.tar"
        if not archive.exists():
            print(
                f"[icons] no baked snapshot for accent='{accent}' theme='{icon_theme}' "
                f"(expected {archive}). Run scripts/bake_icon_accents.py once to create it."
            )
            return changed

        print(f"[icons] accent={accent} (theme={icon_theme}, from baked snapshot)")
        shell.run(["sudo", "tar", "-xf", str(archive), "-C", "/"])
        # Targeted at just the theme actually in use -- unlike
        # papirus-folders' own cache step, which rebuilds all three
        # siblings regardless of which one anything reads from.
        shell.run(["sudo", "gtk-update-icon-cache", "-qf", f"/usr/share/icons/{icon_theme}"])
        changed = True

    return changed
