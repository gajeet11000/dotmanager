"""Applies a theme profile's colors to Qt5/Qt6 applications, via qt5ct/qt6ct.

Qt has no native "just give me these hex codes" theming path -- qt5ct and
qt6ct (already installed) are the standard way to drive it: each writes a
QSettings ini (qt{5,6}ct.conf) that Qt's "qt5ct"/"qt6ct" platform theme
plugins read at startup (selected via QT_QPA_PLATFORMTHEME -- see
dotfiles/hypr/.config/hypr/configs/environment.lua). This applier:

  - sets style=Fusion (Qt's built-in style that actually honors a custom
    QPalette -- most other styles, including Kvantum, need a matching
    pre-built theme asset per color scheme; only catppuccin-macchiato-mauve
    has one installed system-wide, so Fusion + a generated palette is the
    only approach that covers every dotmanager theme uniformly)
  - sets icon_theme= to the same Papirus variant icon_theme.py already
    picked for this profile, so file/folder icons in Qt file dialogs match
  - writes qt{5,6}ct's color_scheme_path target (style-colors.conf) with a
    QPalette generated from the same base hex values core.theme_appliers
    ._palette already defines for claude_theme/herdr_theme

qt{5,6}ct.conf hold other user state (fonts, window geometry) qt5ct/qt6ct
themselves manage, so this patches just the style/icon_theme/custom_palette
lines in place rather than replacing the file, same technique herdr_theme
uses on config.toml.

QPalette::ColorRole order/count (21 roles, Qt5 and Qt6 agree) verified
against the sample palettes qt5ct itself ships in /usr/share/qt5ct/colors/.
inactive_colors is always identical to active_colors in every one of those
samples, so this only computes an active row and a dimmed disabled row.
"""

from pathlib import Path

from core.theme_appliers._palette import PALETTES, luminance, mix

QT5CT_CONF = Path.home() / ".config" / "qt5ct" / "qt5ct.conf"
QT6CT_CONF = Path.home() / ".config" / "qt6ct" / "qt6ct.conf"
QT5CT_COLORS = Path.home() / ".config" / "qt5ct" / "style-colors.conf"
QT6CT_COLORS = Path.home() / ".config" / "qt6ct" / "style-colors.conf"

# QPalette::ColorRole, in enum order: WindowText, Button, Light, Midlight,
# Dark, Mid, Text, BrightText, ButtonText, Base, Window, Shadow, Highlight,
# HighlightedText, Link, LinkVisited, AlternateBase, NoRole, ToolTipBase,
# ToolTipText, PlaceholderText.
_ROLE_NAMES = [
    "WindowText", "Button", "Light", "Midlight", "Dark", "Mid", "Text",
    "BrightText", "ButtonText", "Base", "Window", "Shadow", "Highlight",
    "HighlightedText", "Link", "LinkVisited", "AlternateBase", "NoRole",
    "ToolTipBase", "ToolTipText", "PlaceholderText",
]


def _argb(hex_color: str) -> str:
    return "#ff" + hex_color.lstrip("#")


def _build_active_row(p: dict) -> dict:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    blue, purple = p["blue"], p["purple"]
    light = p["base"] == "light"

    button = mix(bg, fg, 0.08)
    dark_role = mix(button, "#000000", 0.30)
    highlighted_text = "#000000" if luminance(accent) > 0.5 else "#ffffff"

    return {
        "WindowText": fg,
        "Button": button,
        "Light": mix(bg, fg, 0.20),
        "Midlight": mix(bg, fg, 0.14),
        "Dark": dark_role,
        "Mid": mix(button, dark_role, 0.5),
        "Text": fg,
        "BrightText": "#ffffff",
        "ButtonText": fg,
        "Base": "#ffffff" if light else mix(bg, fg, 0.08),
        "Window": bg,
        "Shadow": mix(bg, "#000000", 0.40),
        "Highlight": accent,
        "HighlightedText": highlighted_text,
        "Link": blue,
        "LinkVisited": purple,
        "AlternateBase": mix(bg, fg, 0.05),
        "NoRole": bg,
        "ToolTipBase": mix(bg, fg, 0.08),
        "ToolTipText": fg,
        "PlaceholderText": muted,
    }


# Roles that get replaced by `muted` in the disabled row; everything else
# is carried over unchanged (matches qt5ct's own bundled sample palettes).
_DISABLED_MUTED_ROLES = {"WindowText", "Text", "ButtonText", "HighlightedText", "ToolTipText"}


def _render_colors_conf(p: dict) -> str:
    active = _build_active_row(p)
    disabled = {
        role: (p["muted"] if role in _DISABLED_MUTED_ROLES else active[role])
        for role in _ROLE_NAMES
    }

    active_str = ", ".join(_argb(active[role]) for role in _ROLE_NAMES)
    disabled_str = ", ".join(_argb(disabled[role]) for role in _ROLE_NAMES)

    return (
        "[ColorScheme]\n"
        f"active_colors={active_str}\n"
        f"disabled_colors={disabled_str}\n"
        f"inactive_colors={active_str}\n"
    )


def _patch_conf(conf_file: Path, icon_theme: str) -> None:
    if not conf_file.exists():
        print(f"[qt] no config at {conf_file}, skipping")
        return

    replacements = {"style": "Fusion", "custom_palette": "true", "icon_theme": icon_theme}
    lines = conf_file.read_text().splitlines(keepends=True)
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip()
        if key in replacements:
            lines[i] = f"{key}={replacements[key]}\n"
    conf_file.write_text("".join(lines))


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

    colors_conf = _render_colors_conf(palette)
    for path in (QT5CT_COLORS, QT6CT_COLORS):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            path.unlink()
        path.write_text(colors_conf)

    _patch_conf(QT5CT_CONF, icon_theme)
    _patch_conf(QT6CT_CONF, icon_theme)

    return True
