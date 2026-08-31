from pathlib import Path

from core.theme_appliers import POST_LIVE_APPLIERS, PRE_LIVE_APPLIERS
from core.theme_appliers._nwg_look import apply_live

# Where GTK themes get installed (see setup gtk_theme); used only to sanity
# check a profile's gtk_theme actually exists before applying it.
THEME_SEARCH_DIRS = [Path("/usr/share/themes"), Path.home() / ".local" / "share" / "themes"]

# One entry per logical theme. Each maps to a profile of `app_key: value`
# pairs; core.theme_appliers.PRE_LIVE_APPLIERS/POST_LIVE_APPLIERS are the
# functions that know how to read those keys and apply them. A theme
# doesn't need every key defined for every app — an applier just skips
# itself if its key is missing.
#
# Current keys: gtk_theme, color_scheme, icon_theme, icon_accent (all set
# explicitly per theme below -- these are the ones that genuinely differ
# per app) plus kitty_theme, lsd_theme, nvim_theme, swaync_theme,
# rofi_theme, waybar_theme, herdr_theme, claude_theme, qt_theme (every one
# of these always equals the theme's own name -- see _SLUG_KEYS/_profile
# below).
# Future app: if its applier can just reuse the theme name as-is, add it
# to _SLUG_KEYS; if it needs its own per-theme value instead, add it as
# an explicit argument to _profile() like gtk_theme/icon_accent are.
_SLUG_KEYS = [
    "kitty_theme",
    "lsd_theme",
    "nvim_theme",
    "swaync_theme",
    "rofi_theme",
    "waybar_theme",
    "herdr_theme",
    "claude_theme",
    "qt_theme",
]


def _profile(name: str, *, gtk_theme: str, color_scheme: str, icon_theme: str, icon_accent: str) -> dict:
    profile = {
        "gtk_theme": gtk_theme,
        "color_scheme": color_scheme,
        "icon_theme": icon_theme,
        "icon_accent": icon_accent,
    }
    profile.update(dict.fromkeys(_SLUG_KEYS, name))
    return profile


THEMES: dict[str, dict] = {
    "gruvbox-dark": _profile(
        "gruvbox-dark",
        gtk_theme="Gruvbox-Dark",
        color_scheme="prefer-dark",
        icon_theme="Papirus-Dark",
        icon_accent="orange",
    ),
    "catppuccin-macchiato-mauve": _profile(
        "catppuccin-macchiato-mauve",
        gtk_theme="catppuccin-macchiato-mauve-standard+default",
        color_scheme="prefer-dark",
        icon_theme="Papirus-Dark",
        icon_accent="cat-macchiato-mauve",
    ),
    "github-light": _profile(
        "github-light",
        gtk_theme="Materia-light",
        color_scheme="default",
        icon_theme="Papirus-Light",
        icon_accent="blue",
    ),
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
    for applier in PRE_LIVE_APPLIERS:
        did_anything |= applier(profile)

    if did_anything:
        print("Applying live via nwg-look -a -x...")
        apply_live()

    for applier in POST_LIVE_APPLIERS:
        did_anything |= applier(profile)

    print(f"Done. '{name}' is now active.")
