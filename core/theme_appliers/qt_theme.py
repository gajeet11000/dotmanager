"""Applies a theme profile's colors to Qt5/Qt6 applications, via Kvantum.

Plain qt5ct/qt6ct (a QPalette handed to the built-in Fusion style) only
themes vanilla Qt widgets -- KDE Frameworks apps (okular, dolphin, kate,
...) layer their own KColorScheme system on top and mostly ignore that
QPalette, so they stay stuck on Breeze Light regardless. Verified live:
screenshotting okular with style=Fusion + a custom QPalette still
rendered fully light; switching to style=kvantum with a real Kvantum
theme rendered it correctly dark. Kvantum's QStyle plugin builds its own
palette from the theme's [GeneralColors] and reaches KDE apps too, so
that's what this drives instead.

assets/kvantum/base.svg is copied verbatim from the system-installed
`catppuccin-macchiato-mauve` Kvantum theme (kvantum-theme-catppuccin-git)
-- confirmed to have zero hardcoded colors (`grep fill=\"#` on it matches
nothing), so it's a pure shape template safe to reuse for any palette.
assets/kvantum/base.kvconfig.template is that same theme's .kvconfig
with every one of its hex colors replaced by an @ROLE@ token (see the
_TOKEN_ROLES mapping below) -- structure/geometry/widget-state settings
untouched, only recolored per dotmanager theme.

Each dotmanager theme gets its own generated Kvantum theme directory,
~/.config/Kvantum/dotmanager-<name>/, and ~/.config/Kvantum/kvantum.
kvconfig's `theme=` is repointed at it. qt{5,6}ct.conf get style=kvantum
(not "kvantum-dark", which -- confusingly -- is Kvantum's OWN separate
built-in fixed dark theme, not "follow whatever's selected").

Kvantum covers the *widget* painting (backgrounds, buttons, menus) for
both plain Qt and KDE-Frameworks apps -- confirmed live. It doesn't
cover symbolic *icon* recoloring in KDE apps, though -- that needs
hyprqt6engine as QT_QPA_PLATFORMTHEME instead of qt6ct for Qt6 apps (see
dotfiles/hypr/.config/hypr/configs/environment.lua), pointed at a
generated KColorScheme .colors file. qt5ct stays the platform theme for
Qt5 apps (hyprqt6engine has no Qt5 build) -- see _patch_conf below.
"""

import shutil
from pathlib import Path

from core.theme_appliers._palette import PALETTES, luminance, mix

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_SVG = REPO_ROOT / "assets" / "kvantum" / "base.svg"
TEMPLATE_FILE = REPO_ROOT / "assets" / "kvantum" / "base.kvconfig.template"

KVANTUM_DIR = Path.home() / ".config" / "Kvantum"
KVANTUM_MAIN_CONF = KVANTUM_DIR / "kvantum.kvconfig"

QT5CT_CONF = Path.home() / ".config" / "qt5ct" / "qt5ct.conf"
QT6CT_CONF = Path.home() / ".config" / "qt6ct" / "qt6ct.conf"

# KDE Frameworks apps (okular, dolphin, ...) resolve their icon theme from
# here -- separately from qt{5,6}ct's icon_theme=, which only plain Qt
# apps honor. Verified live: qt6ct.conf correctly said icon_theme=Papirus
# -Dark, but okular's toolbar icons still rendered as barely-visible
# light-on-light until this file's [Icons] Theme= was set too.
KDEGLOBALS = Path.home() / ".config" / "kdeglobals"

# qt6ct (and its dual-registered "qt5ct" key) can't apply KIconEngine's
# ColorScheme-Text substitution -- the mechanism that recolors Papirus's
# (or any KDE-aware icon theme's) symbolic action icons (zoom-in, zoom-
# out, ...) to match the active palette. That's a documented qt6ct gap
# (see hyprqt6engine's README/wiki), not a caching issue -- confirmed by
# comparing okular screenshots pixel-by-pixel across repeated launches
# and a full Hyprland session restart, all still wrong. hyprqt6engine
# replaces qt6ct as QT_QPA_PLATFORMTHEME and links KIconThemes directly,
# so it can do this substitution -- but only once theme:color_scheme
# points at a real KColorScheme .colors file (confirmed by reading
# hyprqt6engine's own source: isKColorScheme() just checks the value
# ends in ".colors", then sets it as the KDE_COLOR_SCHEME_PATH qApp
# property). No dotmanager-specific .colors scheme is installed
# system-wide, so this generates one per theme too.
COLOR_SCHEMES_DIR = Path.home() / ".local" / "share" / "color-schemes"
HYPRQT6ENGINE_CONF = Path.home() / ".config" / "hypr" / "hyprqt6engine.conf"


def _theme_name(dotmanager_theme: str) -> str:
    return f"dotmanager-{dotmanager_theme}"


def _build_tokens(p: dict) -> dict:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]

    return {
        "@WINDOW@": bg,
        "@BASE@": mix(bg, "#000000", 0.12),
        "@BUTTON@": mix(bg, fg, 0.08),
        "@LIGHT@": mix(bg, fg, 0.15),
        "@HIGHLIGHT_ALPHA@": accent + "4d",  # ~30% alpha, matches the source theme
        "@TEXT@": fg,
        "@MUTED@": muted,
        "@DIM_TEXT@": mix(fg, bg, 0.35),
        "@ACCENT@": accent,
        "@LINK_VISITED@": p["purple"],
        "@ON_ACCENT@": "#000000" if luminance(accent) > 0.5 else "#ffffff",
    }


def _render_kvconfig(p: dict) -> str:
    text = TEMPLATE_FILE.read_text()
    for token, value in _build_tokens(p).items():
        text = text.replace(token, value)
    return text


def _write_theme_dir(dotmanager_theme: str, palette: dict) -> None:
    name = _theme_name(dotmanager_theme)
    theme_dir = KVANTUM_DIR / name
    theme_dir.mkdir(parents=True, exist_ok=True)

    (theme_dir / f"{name}.kvconfig").write_text(_render_kvconfig(palette))
    shutil.copyfile(BASE_SVG, theme_dir / f"{name}.svg")


def _select_theme(dotmanager_theme: str) -> None:
    KVANTUM_DIR.mkdir(parents=True, exist_ok=True)
    KVANTUM_MAIN_CONF.write_text(f"[General]\ntheme={_theme_name(dotmanager_theme)}\n")


def _patch_conf(conf_file: Path, icon_theme: str) -> None:
    if not conf_file.exists():
        print(f"[qt] no config at {conf_file}, skipping")
        return

    replacements = {"style": "kvantum", "custom_palette": "false", "icon_theme": icon_theme}
    lines = conf_file.read_text().splitlines(keepends=True)
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip()
        if key in replacements:
            lines[i] = f"{key}={replacements[key]}\n"
    conf_file.write_text("".join(lines))


def _render_colors_scheme(name: str, p: dict) -> str:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    button_bg = mix(bg, fg, 0.08)
    view_bg = mix(bg, "#000000", 0.08)
    tooltip_bg = mix(bg, "#000000", 0.20)
    inactive_bg = mix(bg, fg, 0.03)
    on_accent = "#000000" if luminance(accent) > 0.5 else "#ffffff"

    def rgb(hex_color: str) -> str:
        return ",".join(str(int(hex_color[i : i + 2], 16)) for i in (1, 3, 5))

    def section(bg_normal: str, fg_normal: str) -> str:
        return (
            f"BackgroundAlternate={rgb(mix(bg_normal, fg_normal, 0.06))}\n"
            f"BackgroundNormal={rgb(bg_normal)}\n"
            f"DecorationFocus={rgb(accent)}\n"
            f"DecorationHover={rgb(mix(accent, fg, 0.2))}\n"
            f"ForegroundActive={rgb(accent)}\n"
            f"ForegroundInactive={rgb(muted)}\n"
            f"ForegroundLink={rgb(p['blue'])}\n"
            f"ForegroundNegative={rgb(p['red'])}\n"
            f"ForegroundNeutral={rgb(p['yellow'])}\n"
            f"ForegroundNormal={rgb(fg_normal)}\n"
            f"ForegroundPositive={rgb(p['green'])}\n"
            f"ForegroundVisited={rgb(p['purple'])}\n"
        )

    return (
        "[ColorEffects:Disabled]\n"
        f"Color={rgb(muted)}\n"
        "ColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\n"
        "IntensityAmount=0.1\nIntensityEffect=0\n\n"
        "[ColorEffects:Inactive]\n"
        "ChangeSelectionColor=true\n"
        f"Color={rgb(muted)}\n"
        "ColorAmount=0.025\nColorEffect=2\nContrastAmount=0.1\nContrastEffect=2\n"
        "Enable=true\nIntensityAmount=0\nIntensityEffect=0\n\n"
        f"[Colors:Button]\n{section(button_bg, fg)}\n"
        f"[Colors:Selection]\nBackgroundAlternate={rgb(accent)}\nBackgroundNormal={rgb(accent)}\n"
        f"DecorationFocus={rgb(accent)}\nDecorationHover={rgb(mix(accent, fg, 0.2))}\n"
        f"ForegroundActive={rgb(on_accent)}\nForegroundInactive={rgb(on_accent)}\n"
        f"ForegroundLink={rgb(p['blue'])}\nForegroundNegative={rgb(p['red'])}\n"
        f"ForegroundNeutral={rgb(p['yellow'])}\nForegroundNormal={rgb(on_accent)}\n"
        f"ForegroundPositive={rgb(p['green'])}\nForegroundVisited={rgb(p['purple'])}\n\n"
        f"[Colors:Tooltip]\n{section(tooltip_bg, fg)}\n"
        f"[Colors:View]\n{section(view_bg, fg)}\n"
        f"[Colors:Window]\n{section(bg, fg)}\n"
        "[General]\n"
        f"ColorScheme={name}\nName={name}\nshadeSortColumn=true\n\n"
        "[KDE]\ncontrast=0\n\n"
        "[WM]\n"
        f"activeBackground={rgb(bg)}\nactiveBlend={rgb(bg)}\nactiveForeground={rgb(fg)}\n"
        f"inactiveBackground={rgb(inactive_bg)}\ninactiveBlend={rgb(inactive_bg)}\ninactiveForeground={rgb(muted)}\n"
    )


def _write_color_scheme(dotmanager_theme: str, palette: dict) -> Path:
    name = _theme_name(dotmanager_theme)
    COLOR_SCHEMES_DIR.mkdir(parents=True, exist_ok=True)
    path = COLOR_SCHEMES_DIR / f"{name}.colors"
    path.write_text(_render_colors_scheme(name, palette))
    return path


def _write_hyprqt6engine_conf(color_scheme_path: Path, icon_theme: str) -> None:
    HYPRQT6ENGINE_CONF.parent.mkdir(parents=True, exist_ok=True)
    HYPRQT6ENGINE_CONF.write_text(
        "theme {\n"
        f"    color_scheme = {color_scheme_path}\n"
        f"    icon_theme = {icon_theme}\n"
        "    style = kvantum\n"
        "}\n"
    )


def _set_ini_key(path: Path, section: str, key: str, value: str) -> None:
    """Ensure `key=value` under `[section]` in an INI file, preserving
    everything else -- creates the file/section if either is missing."""
    header = f"[{section}]"
    lines = path.read_text().splitlines(keepends=True) if path.exists() else []

    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += [f"\n{header}\n" if lines else f"{header}\n", f"{key}={value}\n"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(lines))
        return

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("["):
            end = i
            break

    for i in range(start + 1, end):
        if lines[i].split("=", 1)[0].strip() == key:
            lines[i] = f"{key}={value}\n"
            path.write_text("".join(lines))
            return

    lines.insert(end, f"{key}={value}\n")
    path.write_text("".join(lines))


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

    _write_theme_dir(qt_theme, palette)
    _select_theme(qt_theme)
    _patch_conf(QT5CT_CONF, icon_theme)
    _patch_conf(QT6CT_CONF, icon_theme)
    _set_ini_key(KDEGLOBALS, "Icons", "Theme", icon_theme)

    color_scheme_path = _write_color_scheme(qt_theme, palette)
    _write_hyprqt6engine_conf(color_scheme_path, icon_theme)

    return True
