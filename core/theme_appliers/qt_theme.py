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

    return True
