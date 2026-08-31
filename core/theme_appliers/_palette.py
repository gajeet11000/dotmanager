"""Shared base palette for appliers that need raw hex values rather than
a pre-built theme file to hand off to (claude_theme, qt_theme -- herdr_theme
keeps its own richer, hand-tuned surface/overlay scale since herdr's
CustomThemeColors struct wants more shades than this 12-key set covers).

Each profile's `base` is "dark" or "light"; the rest are the exact hex
values already established for kitty/rofi/waybar/herdr's palettes.
"""

PALETTES = {
    "gruvbox-dark": {
        "base": "dark",
        "bg": "#282828", "fg": "#ebdbb2", "accent": "#d79921", "muted": "#7c6f64",
        "red": "#fb4934", "green": "#b8bb26", "yellow": "#fabd2f", "blue": "#83a598",
        "purple": "#d3869b", "cyan": "#8ec07c", "orange": "#fe8019",
        "selection_bg": "#504945",
    },
    "catppuccin-macchiato-mauve": {
        "base": "dark",
        "bg": "#24273a", "fg": "#cad3f5", "accent": "#c6a0f6", "muted": "#6e738d",
        "red": "#ed8796", "green": "#a6da95", "yellow": "#eed49f", "blue": "#8aadf4",
        "purple": "#c6a0f6", "cyan": "#8bd5ca", "orange": "#f5a97f",
        "selection_bg": "#494d64",
    },
    "github-light": {
        "base": "light",
        "bg": "#ffffff", "fg": "#24292f", "accent": "#0969da", "muted": "#8c959f",
        "red": "#cf222e", "green": "#116329", "yellow": "#4d2d00", "blue": "#0969da",
        "purple": "#8250df", "cyan": "#1b7c83", "orange": "#9a6700",
        "selection_bg": "#eaeef2",
    },
}


def mix(hex_a: str, hex_b: str, fraction: float) -> str:
    """hex_a blended `fraction` of the way toward hex_b."""
    a = [int(hex_a[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x + (y - x) * fraction) for x, y in zip(a, b)]
    return "#" + "".join(f"{v:02x}" for v in mixed)


def luminance(hex_color: str) -> float:
    """Perceived (ITU-R BT.601) luminance of hex_color, 0.0-1.0."""
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255
