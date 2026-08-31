-- ##############################
-- ### WINDOWS AND WORKSPACES ###
-- ##############################

hl.window_rule({
    match = {
        class = "^()$",
        title = "^()$",
    },
    no_blur = true,
})

hl.window_rule({
    match = {
        class = ".*", -- You'll probably like this.
    },
    suppress_event = "maximize",
})

-- Floating
hl.window_rule({
    match = {
        title = "^(Open File)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(Select a File)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(Choose wallpaper)(.*)$",
    },
    center = true,
    float = true,
    size = "(monitor_w*0.6) (monitor_h*0.65)",
})

hl.window_rule({
    match = {
        title = "^(Open Folder)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(Save As)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(Library)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(File Upload)(.*)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(.*)(wants to save)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        title = "^(.*)(wants to open)$",
    },
    center = true,
    float = true,
})

hl.window_rule({
    match = {
        class = "^(blueberry\\.py)$",
    },
    float = true,
})

hl.window_rule({
    match = {
        class = "^(guifetch)$", -- FlafyDev/guifetch
    },
    float = true,
})

hl.window_rule({
    match = {
        class = "^(pavucontrol)$",
    },
    float = true,
    center = true,
    size = {"(monitor_w*0.45)", "(monitor_h*0.45)"}
})

hl.window_rule({
    match = {
        class = "^(org.pulseaudio.pavucontrol)$",
    },
    float = true,
    center = true,
    size = {"(monitor_w*0.45)", "(monitor_h*0.45)"}
})

hl.window_rule({
    match = {
        class = "^(nm-connection-editor)$",
    },
    float = true,
    center = true,
    size = {"(monitor_w*0.45)", "(monitor_h*0.45)"}
})

hl.window_rule({
    match = {
        class = "^(com.nextcloud.desktopclient.nextcloud)$",
    },
    float = true,
    center = true,
    size = {"(monitor_w*0.45)", "(monitor_h*0.45)"}
})

hl.window_rule({
    match = {
        class = "^(org.gnome.baobab)$",
    },
    float = true,
    center = true,
    size = {"(monitor_w*0.75)", "(monitor_h*0.75)"}
})

hl.window_rule({
    match = {
        class = ".*plasmawindowed.*",
    },
    float = true,
})

hl.window_rule({
    match = {
        class = "kcm_.*",
    },
    float = true,
})

hl.window_rule({
    match = {
        class = ".*bluedevilwizard",
    },
    float = true,
})

hl.window_rule({
    match = {
        title = ".*Welcome.*",
    },
    float = true,
})

hl.window_rule({
    match = {
        title = "^(illogical-impulse Settings)$",
    },
    float = true,
})

hl.window_rule({
    match = {
        title = ".*Shell conflicts.*",
    },
    float = true,
})

hl.window_rule({
    match = {
        class = "org.freedesktop.impl.portal.desktop.kde",
    },
    float = true,
    size = "(monitor_w*0.6) (monitor_h*0.65)",
})

hl.window_rule({
    match = {
        class = "(org.gnome.Calculator)",
    },
    float = true,
})

-- Picture-in-Picture
hl.window_rule({
    match = {
        title = "^([Pp]icture[-\\s]?[Ii]n[-\\s]?[Pp]icture)(.*)$",
    },
    float = true,
    keep_aspect_ratio = true,
    move = {"((monitor_w*0.73))", "((monitor_h*0.72))"},
    size = {"(monitor_w*0.25)", "(monitor_h*0.25)"},
    pin = true,
})

-- --- Tearing ---
hl.window_rule({
    match = {
        class = "^(steam_app).*",
    },
    immediate = true,
})

-- No shadow for tiled windows (matches windows that are not floating).
hl.window_rule({
    match = {
        float = false,
    },
    no_shadow = true,
})

hl.window_rule({
    match = {
        class = "^PacketTracer$",
        -- match windows whose title is not the main Cisco Packet Tracer window
        title = "negative:^Cisco Packet Tracer",
    },
    float = true,
})

-- ######## Layer rules ########

hl.layer_rule({
    match = {
        namespace = ".*",
    },
    xray = true,
    no_anim = true,
})

hl.layer_rule({
    -- config.jsonc sets "name"/"id" to "mainbar", so that's the actual
    -- Wayland layer-shell namespace waybar registers under (verified via
    -- `hyprctl layers -j`) -- "waybar" here never matched anything, so
    -- blur was never actually being applied to the bar.
    match = {
        namespace = "mainbar",
    },
    blur = true,
    ignore_alpha = 0.5,
})

hl.layer_rule({
    match = {
        namespace = "rofi",
    },
    blur = true,
    ignore_alpha = 0.5,
})

hl.layer_rule({
    match = {
        namespace = "walker",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "selection",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "overview",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "anyrun",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "indicator.*",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "osk",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "hyprpicker",
    },
    no_anim = true,
})

hl.layer_rule({
    match = {
        namespace = "gtk-layer-shell",
    },
    blur = true,
    ignore_alpha = 0,
})

hl.layer_rule({
    match = {
        namespace = "launcher",
    },
    blur = true,
    ignore_alpha = 0.5,
})

hl.layer_rule({
    match = {
        namespace = "logout_dialog", -- wlogout
    },
    blur = true,
})

hl.layer_rule({
    match = {
        namespace = "swaync-control-center",
    },
    blur = true,
    ignore_alpha = 0.5,
})

hl.layer_rule({
    match = {
        namespace = "swaync-notification-window",
    },
    blur = true,
    ignore_alpha = 0.5,
})