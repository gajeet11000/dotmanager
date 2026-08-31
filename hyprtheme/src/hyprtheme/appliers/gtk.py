"""Built-in plugin: applies a theme's GTK widget theme + light/dark
color-scheme via nwg-look (see _nwg_look.py).

Configure in apps.toml:
    [apps.gtk]
    kind = "plugin"
    plugin = "gtk"
    live_push = "nwg-look"
    gsettings_file = "~/.local/share/nwg-look/gsettings"
    theme_dirs = ["/usr/share/themes", "~/.local/share/themes"]  # optional,
        # used only to validate the theme is actually installed before
        # switching to it -- omit to skip the check
"""

from pathlib import Path

from hyprtheme.apps import AppConfig
from hyprtheme.appliers import _nwg_look
from hyprtheme.theme import Theme


def _validate_installed(gtk_theme: str, theme_dirs: list[str]) -> None:
    dirs = [Path(d).expanduser() for d in theme_dirs]
    if any((d / gtk_theme / "index.theme").exists() for d in dirs):
        return
    raise ValueError(
        f"GTK theme '{gtk_theme}' not found in {' or '.join(str(d) for d in dirs)}."
    )


def apply(theme: Theme, app: AppConfig) -> bool:
    fields = {}
    if "gtk_theme" in theme.apps:
        fields["gtk-theme"] = theme.apps["gtk_theme"]
    if "color_scheme" in theme.apps:
        fields["color-scheme"] = theme.apps["color_scheme"]

    if not fields:
        return False

    theme_dirs = app.options.get("theme_dirs")
    if theme_dirs and "gtk-theme" in fields:
        _validate_installed(fields["gtk-theme"], theme_dirs)

    print(f"[gtk] gtk-theme={fields.get('gtk-theme', '(unchanged)')} "
          f"color-scheme={fields.get('color-scheme', '(unchanged)')}")
    gsettings_file = Path(app.options["gsettings_file"]).expanduser()
    _nwg_look.patch_fields(gsettings_file, **fields)
    return True
