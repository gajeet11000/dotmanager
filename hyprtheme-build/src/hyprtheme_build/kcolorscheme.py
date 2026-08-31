"""Generates a KDE Plasma-format .colors file from a raw hex palette.

This is what a platform theme engine linking KIconThemes (e.g.
hyprqt6engine) points its `color_scheme` config at, so it can build a
QPalette AND -- critically -- so KDE Frameworks apps can do KIconEngine's
ColorScheme-Text substitution (recoloring symbolic action icons like
zoom-in/zoom-out to match). Kvantum doesn't provide either on its own.

Section/key names and the overall shape follow the standard KDE Plasma
.colors format (verified against a real KDE-shipped scheme,
/usr/share/color-schemes/Kvantum.colors), just filled in from the palette.
"""

from pathlib import Path

from hyprtheme_build.palette import luminance, mix


def _rgb(hex_color: str) -> str:
    return ",".join(str(int(hex_color[i : i + 2], 16)) for i in (1, 3, 5))


def _section(bg_normal: str, fg_normal: str, p: dict) -> str:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    return (
        f"BackgroundAlternate={_rgb(mix(bg_normal, fg_normal, 0.06))}\n"
        f"BackgroundNormal={_rgb(bg_normal)}\n"
        f"DecorationFocus={_rgb(accent)}\n"
        f"DecorationHover={_rgb(mix(accent, fg, 0.2))}\n"
        f"ForegroundActive={_rgb(accent)}\n"
        f"ForegroundInactive={_rgb(muted)}\n"
        f"ForegroundLink={_rgb(p['blue'])}\n"
        f"ForegroundNegative={_rgb(p['red'])}\n"
        f"ForegroundNeutral={_rgb(p['yellow'])}\n"
        f"ForegroundNormal={_rgb(fg_normal)}\n"
        f"ForegroundPositive={_rgb(p['green'])}\n"
        f"ForegroundVisited={_rgb(p['purple'])}\n"
    )


def _selection_section(p: dict) -> str:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    on_accent = "#000000" if luminance(accent) > 0.5 else "#ffffff"
    return (
        f"BackgroundAlternate={_rgb(accent)}\nBackgroundNormal={_rgb(accent)}\n"
        f"DecorationFocus={_rgb(accent)}\nDecorationHover={_rgb(mix(accent, fg, 0.2))}\n"
        f"ForegroundActive={_rgb(on_accent)}\nForegroundInactive={_rgb(on_accent)}\n"
        f"ForegroundLink={_rgb(p['blue'])}\nForegroundNegative={_rgb(p['red'])}\n"
        f"ForegroundNeutral={_rgb(p['yellow'])}\nForegroundNormal={_rgb(on_accent)}\n"
        f"ForegroundPositive={_rgb(p['green'])}\nForegroundVisited={_rgb(p['purple'])}\n"
    )


def _render(name: str, p: dict) -> str:
    bg, fg, muted = p["bg"], p["fg"], p["muted"]
    button_bg = mix(bg, fg, 0.08)
    view_bg = mix(bg, "#000000", 0.08)
    tooltip_bg = mix(bg, "#000000", 0.20)
    inactive_bg = mix(bg, fg, 0.03)

    return (
        "[ColorEffects:Disabled]\n"
        f"Color={_rgb(muted)}\n"
        "ColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\n"
        "IntensityAmount=0.1\nIntensityEffect=0\n\n"
        "[ColorEffects:Inactive]\n"
        "ChangeSelectionColor=true\n"
        f"Color={_rgb(muted)}\n"
        "ColorAmount=0.025\nColorEffect=2\nContrastAmount=0.1\nContrastEffect=2\n"
        "Enable=true\nIntensityAmount=0\nIntensityEffect=0\n\n"
        f"[Colors:Button]\n{_section(button_bg, fg, p)}\n"
        f"[Colors:Selection]\n{_selection_section(p)}\n"
        f"[Colors:Tooltip]\n{_section(tooltip_bg, fg, p)}\n"
        f"[Colors:View]\n{_section(view_bg, fg, p)}\n"
        f"[Colors:Window]\n{_section(bg, fg, p)}\n"
        "[General]\n"
        f"ColorScheme={name}\nName={name}\nshadeSortColumn=true\n\n"
        "[KDE]\ncontrast=0\n\n"
        "[WM]\n"
        f"activeBackground={_rgb(bg)}\nactiveBlend={_rgb(bg)}\nactiveForeground={_rgb(fg)}\n"
        f"inactiveBackground={_rgb(inactive_bg)}\ninactiveBlend={_rgb(inactive_bg)}\ninactiveForeground={_rgb(muted)}\n"
    )


def write_scheme(output_dir: Path, theme_name: str, palette: dict) -> Path:
    """Generate `<output_dir>/<theme_name>.colors`, returning its path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{theme_name}.colors"
    path.write_text(_render(theme_name, palette))
    return path
