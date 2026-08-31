-- #############################
-- ### ENVIRONMENT VARIABLES ###
-- #############################

-- See https://wiki.hyprland.org/Configuring/Environment-variables/
local vars = require("configs.variables")

hl.env("BROWSER", vars.BROWSER)
hl.env("SCRATCHPAD_BROWSER", vars.SCRATCHPAD_BROWSER)
hl.env("TERM", vars.TERMINAL)
hl.env("EDITOR", vars.EDITOR)
hl.env("XCURSOR_SIZE", vars.CURSOR_SIZE)
hl.env("XCURSOR_THEME", vars.CURSOR_THEME)
hl.env("HYPRCURSOR_SIZE", vars.CURSOR_SIZE)
hl.env("HYPRCURSOR_THEME", vars.CURSOR_THEME)
-- GTK_THEME is deliberately NOT exported: setting it hard-pins the theme for
-- every process's whole lifetime (Hyprland only exports env vars once, at
-- startup, and can't update them live), which permanently shadows the
-- org.gnome.desktop.interface gsettings key GTK actually live-reloads from.
-- Theme switching goes through `dotmanager theme set` instead.
hl.env("WAYLAND_DISPLAY", "wayland-1")

-- NVIDIA Variables
hl.env("LIBVA_DRIVER_NAME", "nvidia")
hl.env("GBM_BACKEND", "nvidia-drm")
hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")

-- Toolkit Backend Variables
hl.env("GDK_BACKEND", "wayland,x11,*")
hl.env("CLUTTER_BACKEND", "wayland")

-- XDG Specifications
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "sway")

-- QT Variables
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("QT_QPA_PLATFORM", "wayland")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
-- "qt5ct", not "qt6ct": Qt5 apps only look for a platform theme plugin
-- literally named "qt5ct" (that's qt5ct's own plugin's only registered
-- name), while qt6ct's plugin registers itself under *both* "qt6ct" and
-- "qt5ct" (verified via `strings` on libqt6ct.so) for exactly this
-- reason -- one shared value here satisfies both Qt5 and Qt6 apps, each
-- reading its own qt{5,6}ct.conf. See core/theme_appliers/qt_theme.py.
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
