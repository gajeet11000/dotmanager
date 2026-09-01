"""Small color-math helpers shared by the appliers/scripts that compute
colors instead of just copying a pre-made file (claude_theme.py, and
scripts/build_qt_theme.py)."""


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
