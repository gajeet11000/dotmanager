#!/usr/bin/env bash

## Rofi   : Theme Switcher (dotmanager)
## Lists the themes core/theme_manager.py knows about and applies the
## one picked via `python3 main.py theme set <name>`.

DOTMANAGER_DIR="$HOME/Projects/dotmanager"

# Rofi theme (same visual style as rofi-power-menu.sh -- a horizontal
# pill row at the top of the screen)
dir="$HOME/.config/rofi/themes/"
theme='application_launcher'

rofi_cmd() {
	rofi -dmenu \
		-p "Theme: " -i \
		-theme "${dir}/${theme}.rasi"
}

chosen="$(python3 "$DOTMANAGER_DIR/main.py" theme list | sed 's/^[[:space:]]*//' | rofi_cmd)"

# Empty selection means the user cancelled (Esc).
[[ -z "$chosen" ]] && exit 0

if python3 "$DOTMANAGER_DIR/main.py" theme set "$chosen"; then
	notify-send -e -u low -i "preferences-desktop-theme" "Theme set" "${chosen}"
else
	notify-send -e -u critical -i "dialog-error" "Theme set failed" "${chosen}"
fi
