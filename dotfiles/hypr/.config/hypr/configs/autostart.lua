-- #################
-- ### AUTOSTART ###
-- #################

local var = require("configs.variables")

hl.on("hyprland.start", function()
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("waybar")
    hl.exec_cmd("/usr/bin/gnome-keyring-daemon --start --components=secrets,pkcs11,ssh,gpg")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("hyprctl setcursor Bibata-Rainbow-Modern 24")
    hl.exec_cmd("kdeconnect-indicator")
    hl.exec_cmd("clipse -listen")
    hl.exec_cmd("swaync")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("hyprsunset")
    hl.exec_cmd("awww-daemon")
    hl.exec_cmd("/usr/lib/xdg-desktop-portal-wlr")
    hl.exec_cmd("/usr/lib/xdg-desktop-portal")
    hl.exec_cmd("qbittorrent")
    hl.exec_cmd(var.SET_RANDOM_WALLPAPER)
    hl.exec_cmd(var.REFRESH_MIRRORS)
    -- hl.exec_cmd("slack")
    -- hl.exec_cmd("dropbox")
end)
