-- #####################
-- ### LOOK AND FEEL ###
-- #####################

hl.config({
    general = {
        gaps_in = 5,
        gaps_out = 7,

        border_size = 2,
        col = {
            active_border = {
                colors = {
                    "rgb(fab387)", -- Peach
                    "rgb(cba6f7)", -- Mauve
                },
                angle = 120,
            },
            inactive_border = "rgba(595959aa)",
        },
        resize_on_border = true,
        extend_border_grab_area = 20,
        hover_icon_on_border = true,

        allow_tearing = false,
        layout = "dwindle",

        snap = {
            enabled = true,
        }
    },

    decoration = {
        rounding = 10,
        rounding_power = 4.0,

        blur = {
            ignore_opacity = false,
            enabled = true,
            xray = true,
            special = false,
            new_optimizations = true,
            size = 10,
            passes = 5,
            brightness = 1,
            noise = 0.04,
            contrast = 0.9,
            popups = true,
            popups_ignorealpha = 0.6,
            input_methods = true,
            input_methods_ignorealpha = 0.8,
        },

        shadow = {
            enabled = true,
            range = 30,
            offset = "0 2",
            render_power = 4,
            color = "rgba(00000010)",
        },
    },

    dwindle = {
        preserve_split = true,
        smart_split = false,
        smart_resizing = false,
    },

    master = {
        new_status = "master",
        mfact = 0.5,
    },

    cursor = {
        no_hardware_cursors = true,
    },

    misc = {
        force_default_wallpaper = 1,
        disable_hyprland_logo = true,
        focus_on_activate = true,
        on_focus_under_fullscreen = 2,
        exit_window_retains_fullscreen = false,
        allow_session_lock_restore = true,
    },

    binds = {
        movefocus_cycles_fullscreen = true,
    },
})
