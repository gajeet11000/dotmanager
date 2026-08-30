local M = {}

M.HOME = os.getenv("HOME")
M.SCRIPTS_DIR = M.HOME .. "/.scripts"
M.STORAGE_DIR = "/mnt/Storage/"

M.EDITOR = "nvim"
M.TERMINAL = "kitty"
M.TERMINAL_MULPLEX = "kitty -e herdr"
M.FILE_MANAGER = "thunar"
M.LAUNCHER = string.format(
    'rofi -show drun -config "%s/.config/rofi/configs/application_launcher.rasi"',
    M.HOME
)
M.BROWSER = "zen-browser"
M.SCRATCHPAD_BROWSER = "chromium"
M.CALCULATOR = "gnome-calculator"

M.REFRESH_MIRRORS = M.SCRIPTS_DIR .. "/refresh_mirrors.sh"
M.RELOAD_WAYBAR = M.SCRIPTS_DIR .. "/reload_waybar.sh"
M.VOLUME = M.SCRIPTS_DIR .. "/Volume.sh"
M.BRIGHTNESS = M.SCRIPTS_DIR .. "/Brightness.sh"
M.SCRATCHPAD = M.SCRIPTS_DIR .. "/scratchpads.sh"
M.WINDOW_SWITCHER = M.SCRIPTS_DIR .. "/window_switcher.sh"
M.LOGOUT = M.SCRIPTS_DIR .. "/rofi-power-menu.sh"

M.TOGGLE_NOTIFICATION_CENTER = "swaync-client -t"
M.SCREENSHOT = "env XDG_CURRENT_DESKTOP=Sway flameshot gui"
M.SET_RANDOM_WALLPAPER = "waypaper --random"

M.CURSOR_SIZE = "24"
M.CURSOR_THEME = "Bibata-Rainbow-Modern"

return M
