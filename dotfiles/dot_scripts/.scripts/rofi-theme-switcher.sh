#!/usr/bin/env bash

## Rofi   : Theme Switcher (dotmanager)
## Lists the themes core/theme_manager.py knows about and applies the
## one picked via `main.py theme set <name>`.

DOTMANAGER_DIR="$HOME/Projects/dotmanager"

# Run everything through `uv run --project` so the right .venv resolves
# regardless of rofi's own cwd/environment.
run_dotmanager() {
	uv run --project "$DOTMANAGER_DIR" python3 "$DOTMANAGER_DIR/main.py" "$@"
}

# Rofi theme (same visual style as rofi-power-menu.sh -- a horizontal
# pill row at the top of the screen)
dir="$HOME/.config/rofi/themes/"
theme='application_launcher'

rofi_cmd() {
	rofi -dmenu \
		-p "Theme: " -i \
		-theme "${dir}/${theme}.rasi"
}

chosen="$(run_dotmanager theme list | sed 's/^[[:space:]]*//' | rofi_cmd)"

# Empty selection means the user cancelled (Esc).
[[ -z "$chosen" ]] && exit 0

# Logged to a file (not just captured for the notification) so a failure
# triggered from a keybind -- no terminal to see stdout/stderr in -- still
# leaves something to look at afterwards.
log="/tmp/dotmanager-theme-switch.log"
if run_dotmanager theme set "$chosen" >"$log" 2>&1; then
	notify-send -e -u low -i "preferences-desktop-theme" "Theme set" "${chosen}"
else
	notify-send -e -u critical -i "dialog-error" "Theme set failed: ${chosen}" \
		"$(tail -n 6 "$log")\n\nFull log: $log"
fi
