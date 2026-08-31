"""Built-in plugin: applies a theme's raw `[palette]` to Qt5/Qt6/KDE apps.

Three real, verified mechanisms, layered because each covers a gap the
previous one left (see the original investigation this was ported from --
dotmanager's git history has the full story):

1. Kvantum (_kvantum.py) for widget/window painting -- plain QPalette gets
   ignored by KDE-Frameworks apps.
2. kdeglobals's [Icons] Theme= for icon *theme selection* -- KDE Frameworks
   apps resolve this independently of qt5ct/qt6ct's own icon_theme=.
3. A generated KDE .colors file (_kcolorscheme.py), pointed at by a
   platform theme engine that links KIconThemes (e.g. hyprwm/hyprqt6engine)
   for icon *recoloring* -- qt5ct/qt6ct can't apply KIconEngine's
   ColorScheme-Text substitution at all, since neither links KIconThemes.

Configure in apps.toml:
    [apps.qt]
    kind = "plugin"
    plugin = "qt"
    kvantum_dir = "~/.config/Kvantum"                    # optional, this default
    base_svg_dark = "~/dotfiles-assets/kvantum/base-dark.svg"
    base_svg_light = "~/dotfiles-assets/kvantum/base-light.svg"
    kvconfig_template = "~/dotfiles-assets/kvantum/base.kvconfig.template"
    kdeglobals = "~/.config/kdeglobals"                  # optional, this default
    color_schemes_dir = "~/.local/share/color-schemes"   # optional, this default
    # Only needed if you're using a platform engine that reads a
    # color_scheme path from its own config file (e.g. hyprqt6engine):
    platform_engine_conf = "~/.config/hypr/hyprqt6engine.conf"
    platform_engine_format = "theme {{\\n    color_scheme = {color_scheme}\\n    icon_theme = {icon_theme}\\n    style = {style}\\n}}\\n"
    style = "kvantum"                                    # optional, this default
"""

from pathlib import Path

from hyprtheme.apps import AppConfig
from hyprtheme.appliers import _kcolorscheme, _kvantum
from hyprtheme.appliers._ini import set_key
from hyprtheme.theme import Theme

DEFAULT_ENGINE_FORMAT = (
    "theme {{\n"
    "    color_scheme = {color_scheme}\n"
    "    icon_theme = {icon_theme}\n"
    "    style = {style}\n"
    "}}\n"
)


def apply(theme: Theme, app: AppConfig) -> bool:
    if theme.palette is None:
        print(f"[qt] theme '{theme.name}' has no [palette], skipping")
        return False

    opts = app.options
    theme_name = f"hyprtheme-{theme.name}"
    icon_theme = theme.apps.get("icon_theme", "")
    print(f"[qt] theme={theme.name} icon_theme={icon_theme or '(unset)'}")

    kvantum_dir = Path(opts.get("kvantum_dir", "~/.config/Kvantum")).expanduser()
    base_svg = {
        "dark": Path(opts["base_svg_dark"]).expanduser(),
        "light": Path(opts["base_svg_light"]).expanduser(),
    }
    template_file = Path(opts["kvconfig_template"]).expanduser()
    _kvantum.write_theme(kvantum_dir, base_svg, template_file, theme_name, theme.palette)
    _kvantum.select_theme(kvantum_dir, theme_name)

    if icon_theme:
        kdeglobals = Path(opts.get("kdeglobals", "~/.config/kdeglobals")).expanduser()
        set_key(kdeglobals, "Icons", "Theme", icon_theme)

    schemes_dir = Path(opts.get("color_schemes_dir", "~/.local/share/color-schemes")).expanduser()
    color_scheme_path = _kcolorscheme.write_scheme(schemes_dir, theme_name, theme.palette)

    if "platform_engine_conf" in opts:
        engine_conf = Path(opts["platform_engine_conf"]).expanduser()
        engine_conf.parent.mkdir(parents=True, exist_ok=True)
        fmt = opts.get("platform_engine_format", DEFAULT_ENGINE_FORMAT)
        engine_conf.write_text(fmt.format(
            color_scheme=color_scheme_path,
            icon_theme=icon_theme,
            style=opts.get("style", "kvantum"),
        ))

    return True
