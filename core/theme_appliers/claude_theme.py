"""Applies a theme profile's colors to the Claude Code CLI -- yes, this tool.

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
(reconciled against Claude Code 2.1.251), covering the documented tokens
plus the most visually load-bearing internal ones (shimmer pairs, diffs,
subagent palette). Skips the purely decorative internal-only tokens
(rainbow_*, clawd_*).

Unlike qt_theme.py, this computes its output live on every switch rather
than from a pre-built file -- it's cheap string/hex math, no external
tool invocation, so there's no build-step to save.
"""

import json
from pathlib import Path

from core.theme_appliers._palette import mix as _mix

THEMES_DIR = Path.home() / ".claude" / "themes"
THEME_FILE = THEMES_DIR / "dotmanager.json"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"


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
    palette = profile.get("palette")
    if not claude_theme or palette is None:
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
