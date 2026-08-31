"""Applies a theme profile's colors to Qt5/Qt6 applications.

This took three real, verified mechanisms to get right -- each layer
below covers a gap the previous one left, discovered by screenshotting
a live KDE app (okular) and checking pixel colors, not by assumption:

1. Kvantum (core.theme_appliers._kvantum) for widget/window painting.
   Plain qt6ct's own QPalette gets ignored by KDE-Frameworks apps
   (okular, dolphin, ...) -- they layer their own KColorScheme system on
   top. Confirmed live: style=Fusion + a correct custom QPalette still
   rendered okular fully light; style=kvantum with a real Kvantum theme
   rendered it correctly dark.

2. ~/.config/kdeglobals's [Icons] Theme= for icon *theme selection*.
   KDE Frameworks apps resolve this independently of qt6ct's own
   icon_theme= setting, which only plain Qt apps honor. Confirmed live:
   qt6ct.conf correctly said icon_theme=Papirus-Dark, but okular's
   toolbar icons stayed barely-visible until kdeglobals had it too.

3. hyprqt6engine (github.com/hyprwm/hyprqt6engine) as QT_QPA_PLATFORMTHEME
   instead of qt6ct, for icon *recoloring*. qt6ct can't apply KIconEngine's
   ColorScheme-Text substitution -- the mechanism that recolors a KDE-aware
   icon theme's symbolic action icons (zoom-in, zoom-out, ...) to match the
   active palette -- because it doesn't link KIconThemes at all. That left
   those specific icons unthemed even with (1) and (2) both correctly
   configured; confirmed by pixel-diffing repeated okular screenshots and a
   full Hyprland session restart, all still wrong, ruling out a caching
   explanation before landing on this one. hyprqt6engine links KIconThemes
   directly, and needs theme:color_scheme pointed at a real KDE .colors
   file to do the substitution (core.theme_appliers._kcolorscheme) --
   confirmed by reading hyprqt6engine's own source: isKColorScheme() just
   checks the value ends in ".colors", then sets it as the
   KDE_COLOR_SCHEME_PATH qApp property.

hyprqt6engine has no Qt5 build, so Qt5 apps get no platform-theme
integration at all under this setup (see dotfiles/hypr/.config/hypr/
configs/environment.lua) -- an accepted tradeoff, since nothing Qt5 is
in daily use here.
"""

from pathlib import Path

from core.theme_appliers import _kcolorscheme, _kvantum
from core.theme_appliers._ini import set_key
from core.theme_appliers._palette import PALETTES

KDEGLOBALS = Path.home() / ".config" / "kdeglobals"
HYPRQT6ENGINE_CONF = Path.home() / ".config" / "hypr" / "hyprqt6engine.conf"


def _write_hyprqt6engine_conf(color_scheme_path: Path, icon_theme: str) -> None:
    HYPRQT6ENGINE_CONF.parent.mkdir(parents=True, exist_ok=True)
    HYPRQT6ENGINE_CONF.write_text(
        "theme {\n"
        f"    color_scheme = {color_scheme_path}\n"
        f"    icon_theme = {icon_theme}\n"
        "    style = kvantum\n"
        "}\n"
    )


def apply(profile: dict) -> bool:
    qt_theme = profile.get("qt_theme")
    if not qt_theme:
        return False

    palette = PALETTES.get(qt_theme)
    if palette is None:
        print(f"[qt] no palette for '{qt_theme}', skipping")
        return False

    icon_theme = profile.get("icon_theme", "Papirus-Dark")
    print(f"[qt] qt_theme={qt_theme} icon_theme={icon_theme}")

    _kvantum.write_theme(qt_theme, palette)
    _kvantum.select_theme(qt_theme)
    set_key(KDEGLOBALS, "Icons", "Theme", icon_theme)

    color_scheme_path = _kcolorscheme.write_scheme(qt_theme, palette)
    _write_hyprqt6engine_conf(color_scheme_path, icon_theme)

    return True
