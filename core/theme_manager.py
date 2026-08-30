from pathlib import Path

from core.theme_appliers import APPLIERS
from core.theme_appliers._nwg_look import apply_live

# Where GTK themes get installed (see setup gtk_theme); used only to sanity
# check a profile's gtk_theme actually exists before applying it.
THEME_SEARCH_DIRS = [Path("/usr/share/themes"), Path.home() / ".local" / "share" / "themes"]

# One entry per logical theme. Each maps to a profile of `app_key: value`
# pairs; core.theme_appliers.APPLIERS is the list of functions that know how
# to read those keys and apply them. A theme doesn't need every key defined
# for every app — an applier just skips itself if its key is missing.
#
# Current keys: gtk_theme, color_scheme (gtk_theme.py), icon_theme,
# icon_accent (icon_theme.py), kitty_theme (kitty_theme.py), lsd_theme
# (lsd_theme.py). Future: fish_theme, nvim_colorscheme, yazi_theme, ... —
# add the key here once its applier exists in core/theme_appliers/.
THEMES: dict[str, dict] = {
    "gruvbox-dark": {
        "gtk_theme": "Gruvbox-Dark",
        "color_scheme": "prefer-dark",
        "icon_theme": "Papirus-Dark",
        "icon_accent": "orange",
        "kitty_theme": "gruvbox-dark",
        "lsd_theme": "gruvbox-dark",
    },
    "gruvbox-light": {
        "gtk_theme": "Gruvbox-Light",
        "color_scheme": "default",
        "icon_theme": "Papirus-Light",
        "icon_accent": "orange",
        "kitty_theme": "gruvbox-light",
        "lsd_theme": "gruvbox-light",
    },
    "catppuccin-macchiato-mauve": {
        "gtk_theme": "catppuccin-macchiato-mauve-standard+default",
        "color_scheme": "prefer-dark",
        "icon_theme": "Papirus-Dark",
        "icon_accent": "cat-macchiato-mauve",
        "kitty_theme": "catppuccin-macchiato-mauve",
        "lsd_theme": "catppuccin-macchiato-mauve",
    },
}


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
    for applier in APPLIERS:
        did_anything |= applier(profile)

    if did_anything:
        print("Applying live via nwg-look -a -x...")
        apply_live()

    print(f"Done. '{name}' is now active.")
