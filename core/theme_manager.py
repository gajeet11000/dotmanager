"""dotmanager's own thin wrapper around hyprtheme (./hyprtheme -- a
standalone, generically reusable theme-switcher library extracted from
what used to live entirely in this file + core/theme_appliers/). All the
actual app-by-app logic now lives there; this just points hyprtheme at
dotmanager's own config:
  - assets/hyprtheme-apps.toml -- where each of dotmanager's apps' files
    live and how to reload them (adding/removing a theme, or adding a new
    declaratively-themeable app, means editing assets/, not this file --
    see hyprtheme/README.md).
  - assets/themes/*.toml -- one file per theme (gruvbox-dark,
    catppuccin-macchiato-mauve, github-light).
  - core/theme_appliers/local_plugins/ -- herdr/claude support, kept out
    of the general-purpose library since they're personal/niche apps.
"""

from pathlib import Path

from hyprtheme import ThemeManager

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_FILE = REPO_ROOT / "assets" / "hyprtheme-apps.toml"
THEMES_DIR = REPO_ROOT / "assets" / "themes"
LOCAL_PLUGINS_DIR = REPO_ROOT / "core" / "theme_appliers" / "local_plugins"

_manager = ThemeManager(
    apps_path=APPS_FILE, themes_dir=THEMES_DIR, plugin_dirs=[LOCAL_PLUGINS_DIR],
)


def list_themes() -> list[str]:
    return _manager.list_themes()


def set_theme(name: str) -> None:
    _manager.set_theme(name)
