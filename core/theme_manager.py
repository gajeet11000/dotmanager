"""dotmanager's theme switcher.

Deliberately plain: `themes/<name>/theme.toml` is the whole picture for a
theme -- one `[apps]` table of per-app string values (an applier only ever
reads the keys it cares about, see core/theme_appliers/__init__.py), and an
optional `[palette]` table of raw hex colors for the couple of appliers that
compute colors instead of copying a pre-made file (claude_theme.py; and
scripts/build_qt_theme.py, run manually, not here). Every other per-theme
file (GTK zip, icon accent tar, kitty/waybar/rofi/swaync/lsd color files,
the generated Kvantum theme + .colors file) lives alongside it, one
subfolder per app, under that same `themes/<name>/` directory.

Fixed to three themes (gruvbox-dark, catppuccin-macchiato-mauve,
catppuccin-latte) -- see `themes/*/theme.toml` and `themes/*/` for what
each actually contains.
"""

import tomllib
from pathlib import Path

from core.theme_appliers import POST_LIVE_APPLIERS, PRE_LIVE_APPLIERS
from core.theme_appliers._nwg_look import apply_live

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"

# Where GTK themes get installed (see setup gtk_theme); used only to sanity
# check a profile's gtk_theme actually exists before applying it.
THEME_SEARCH_DIRS = [Path("/usr/share/themes"), Path.home() / ".local" / "share" / "themes"]


def _load_themes() -> dict[str, dict]:
    """Every `themes/<name>/theme.toml` file is one theme. A theme's
    `[apps]` table is flattened directly into its profile dict (so
    `profile["kitty_theme"]` works, same as every other key); its
    `[palette]` table (if present) is kept under the reserved key
    "palette" for the couple of appliers that need raw hex colors."""
    themes = {}
    for path in sorted(THEMES_DIR.glob("*/theme.toml")):
        data = tomllib.loads(path.read_text())
        name = data.get("name", path.parent.name)
        profile = dict(data.get("apps", {}))
        profile["palette"] = data.get("palette")
        # qt_theme always equals the theme's own name -- it's not a
        # per-app choice like kitty_theme/waybar_theme/etc, since a theme's
        # Qt assets are named after the theme itself (see qt_theme.py).
        profile["qt_theme"] = name
        # Every per-app subfolder (kitty/, waybar/, gtk/, qt/, icons/, ...)
        # for this theme lives under here.
        profile["theme_dir"] = path.parent
        themes[name] = profile
    return themes


THEMES: dict[str, dict] = _load_themes()


def list_themes() -> list[str]:
    return sorted(THEMES)


def _validate_gtk_theme_installed(profile: dict) -> None:
    gtk_theme = profile.get("gtk_theme")
    if not gtk_theme:
        return
    if any((d / gtk_theme / "index.theme").exists() for d in THEME_SEARCH_DIRS):
        return
    raise ValueError(
        f"GTK theme '{gtk_theme}' not found in {' or '.join(str(d) for d in THEME_SEARCH_DIRS)}. "
        "Run 'python3 main.py setup gtk_theme' first."
    )


def set_theme(name: str) -> None:
    profile = THEMES.get(name)
    if profile is None:
        raise ValueError(
            f"unknown theme '{name}'. Run 'python3 main.py theme list' to see options."
        )
    _validate_gtk_theme_installed(profile)

    print(f"Setting theme '{name}'...")
    did_anything = False
    for applier in PRE_LIVE_APPLIERS:
        did_anything |= applier(profile)

    if did_anything:
        print("Applying live via nwg-look -a -x...")
        apply_live()

    for applier in POST_LIVE_APPLIERS:
        did_anything |= applier(profile)

    print(f"Done. '{name}' is now active.")
