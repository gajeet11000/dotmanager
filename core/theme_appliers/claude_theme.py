"""Applies a theme profile's Claude Code CLI colors -- yes, this tool.

Claude Code supports custom themes: a JSON file in ~/.claude/themes/
with `{"name", "base": "dark"|"light", "overrides": {token: color}}`,
selected by setting `"theme": "custom:<slug>"` in ~/.claude/settings.json.
Claude Code watches ~/.claude/themes and hot-reloads on change, per its
own docs (https://code.claude.com/docs/en/terminal-config).

~/.claude/settings.json isn't otherwise repo-managed (it may hold other
user settings beyond theme), so this edits it in place like herdr's
config.toml -- load the JSON, set just the "theme" key, write it back,
rather than a blanket file replace.

Token list and "mix" semantics follow the reference at
https://gist.github.com/cameronsjo/34a6fb8ade2b44c8380e1a2adebbac2b
(reconciled against Claude Code 2.1.251; installed here is 2.1.241),
covering the documented tokens plus the most visually load-bearing
internal ones (shimmer pairs, diffs, subagent palette). Skips the purely
decorative internal-only tokens (rainbow_*, clawd_*).
"""

import json
from pathlib import Path

THEMES_DIR = Path.home() / ".claude" / "themes"
THEME_FILE = THEMES_DIR / "dotmanager.json"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# Base palette per profile, reusing the exact hex already established for
# kitty/lsd/rofi/waybar/herdr. `base` picks Claude's own dark/light preset
# to fall through to for any of the 72 tokens this file doesn't override.
PALETTES = {
    "gruvbox-dark": {
        "base": "dark",
        "bg": "#282828", "fg": "#ebdbb2", "accent": "#d79921", "muted": "#7c6f64",
        "red": "#fb4934", "green": "#b8bb26", "yellow": "#fabd2f", "blue": "#83a598",
        "purple": "#d3869b", "cyan": "#8ec07c", "orange": "#fe8019",
        "selection_bg": "#504945",
    },
    "gruvbox-light": {
        "base": "light",
        "bg": "#fbf1c7", "fg": "#3c3836", "accent": "#b57614", "muted": "#a89984",
        "red": "#9d0006", "green": "#79740e", "yellow": "#b57614", "blue": "#076678",
        "purple": "#8f3f71", "cyan": "#427b58", "orange": "#d65d0e",
        "selection_bg": "#d5c4a1",
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


def _mix(hex_a: str, hex_b: str, fraction: float) -> str:
    """hex_a blended `fraction` of the way toward hex_b."""
    a = [int(hex_a[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x + (y - x) * fraction) for x, y in zip(a, b)]
    return "#" + "".join(f"{v:02x}" for v in mixed)


def _build_overrides(p: dict) -> dict:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    red, green, yellow, blue = p["red"], p["green"], p["yellow"], p["blue"]
    purple, cyan, orange = p["purple"], p["cyan"], p["orange"]

    return {
        "claude": accent,
        "claudeShimmer": _mix(accent, fg, 0.35),
        "text": fg,
        "inverseText": bg,
        "inactive": _mix(fg, bg, 0.40),
        "inactiveShimmer": _mix(fg, bg, 0.25),
        "subtle": muted,
        "suggestion": cyan,
        "remember": yellow,
        "success": green,
        "error": red,
        "warning": yellow,
        "warningShimmer": _mix(yellow, fg, 0.35),
        "merged": purple,
        "promptBorder": accent,
        "promptBorderShimmer": _mix(accent, fg, 0.35),
        "permission": blue,
        "permissionShimmer": _mix(blue, fg, 0.35),
        "planMode": cyan,
        "autoAccept": yellow,
        "autoAcceptShimmer": _mix(yellow, fg, 0.35),
        "skill": yellow,
        "bashBorder": yellow,
        "ide": cyan,
        "fastMode": accent,
        "fastModeShimmer": _mix(accent, fg, 0.35),
        "diffAdded": _mix(bg, green, 0.15),
        "diffRemoved": _mix(bg, red, 0.15),
        "diffAddedDimmed": _mix(bg, green, 0.08),
        "diffRemovedDimmed": _mix(bg, red, 0.08),
        "diffAddedWord": _mix(bg, green, 0.32),
        "diffRemovedWord": _mix(bg, red, 0.32),
        "userMessageBackground": _mix(bg, fg, 0.06),
        "userMessageBackgroundHover": _mix(bg, fg, 0.10),
        "bashMessageBackgroundColor": _mix(bg, fg, 0.06),
        "memoryBackgroundColor": _mix(bg, fg, 0.06),
        "selectionBg": p["selection_bg"],
        "rate_limit_fill": accent,
        "rate_limit_empty": _mix(bg, fg, 0.20),
        "briefLabelYou": yellow,
        "briefLabelClaude": accent,
        "red_FOR_SUBAGENTS_ONLY": red,
        "blue_FOR_SUBAGENTS_ONLY": blue,
        "green_FOR_SUBAGENTS_ONLY": green,
        "yellow_FOR_SUBAGENTS_ONLY": yellow,
        "purple_FOR_SUBAGENTS_ONLY": purple,
        "orange_FOR_SUBAGENTS_ONLY": orange,
        "pink_FOR_SUBAGENTS_ONLY": purple,
        "cyan_FOR_SUBAGENTS_ONLY": cyan,
    }


def apply(profile: dict) -> bool:
    claude_theme = profile.get("claude_theme")
    if not claude_theme:
        return False

    palette = PALETTES.get(claude_theme)
    if palette is None:
        print(f"[claude] no palette for '{claude_theme}', skipping")
        return False

    print(f"[claude] claude_theme={claude_theme}")
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(
        json.dumps(
            {
                "name": "dotmanager",
                "base": palette["base"],
                "overrides": _build_overrides(palette),
            },
            indent=2,
        )
        + "\n"
    )

    settings = {}
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
        except json.JSONDecodeError:
            print(f"[claude] {SETTINGS_FILE} has invalid JSON, leaving theme selection alone")
            return True

    if settings.get("theme") != "custom:dotmanager":
        settings["theme"] = "custom:dotmanager"
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2) + "\n")

    return True
