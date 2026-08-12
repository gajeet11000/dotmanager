local vars = require("configs.variables")
local utils = require("configs.utils")
local SUPER = "SUPER"
local SUPER_SHIFT = "SUPER+SHIFT"
local SUPER_CTRL = "SUPER+CTRL"
local SUPER_ALT = "SUPER+ALT"

-- ###################
-- ### KEYBINDINGS ###
-- ###################

-- Scripts
hl.bind(SUPER .. "+RETURN", hl.dsp.exec_cmd(vars.TERMINAL))
hl.bind(SUPER_ALT .. "+N", hl.dsp.exec_cmd(vars.TERMINAL))
hl.bind(SUPER_SHIFT .. "+E", hl.dsp.exec_cmd(vars.FILE_MANAGER))
hl.bind(SUPER .. "+A", hl.dsp.exec_cmd(vars.FILE_MANAGER .. " " .. vars.STORAGE_DIR))
hl.bind(SUPER .. "+B", hl.dsp.exec_cmd(vars.BROWSER))
hl.bind(SUPER .. "+SPACE", hl.dsp.exec_cmd(vars.LAUNCHER))
hl.bind(SUPER_SHIFT .. "+Q", hl.dsp.exec_cmd(vars.LOGOUT))
hl.bind(SUPER_CTRL .. "+W", hl.dsp.exec_cmd(vars.RELOAD_WAYBAR))
hl.bind("Print", hl.dsp.exec_cmd(vars.SCREENSHOT))
hl.bind(SUPER .. "+P", hl.dsp.exec_cmd(vars.SCREENSHOT))
hl.bind(SUPER .. "+D", hl.dsp.exec_cmd(vars.FILE_MANAGER .. " " .. vars.HOME .. "/Downloads"))
hl.bind(SUPER .. "+Q", hl.dsp.exec_cmd(vars.CALCULATOR))
hl.bind(SUPER .. "+W", hl.dsp.exec_cmd(vars.WINDOW_SWITCHER))
hl.bind(SUPER .. "+N", hl.dsp.exec_cmd(vars.TOGGLE_NOTIFICATION_CENTER))
hl.bind(SUPER_ALT .. "+B", hl.dsp.exec_cmd(vars.SET_RANDOM_WALLPAPER))

-- Window actions
hl.bind(SUPER .. "+F", hl.dsp.window.fullscreen({mode="maximized", action="toggle"}))
hl.bind(SUPER .. "+C", hl.dsp.window.close())
hl.bind(SUPER_SHIFT .. "+C", hl.dsp.window.kill())
hl.bind(SUPER .. "+G", hl.dsp.group.toggle())
hl.bind(SUPER_ALT .. "+F", hl.dsp.window.float())
hl.bind(SUPER_CTRL .. "+R", hl.dsp.exec_cmd("hyprctl reload"))
hl.bind(SUPER_ALT .. "+V", hl.dsp.layout("togglesplit"))

-- Move focus (Arrow keys)
hl.bind(SUPER .. "+LEFT",  hl.dsp.focus({direction="l"}))
hl.bind(SUPER .. "+RIGHT", hl.dsp.focus({direction="r"}))
hl.bind(SUPER .. "+UP",    hl.dsp.focus({direction="u"}))
hl.bind(SUPER .. "+DOWN",  hl.dsp.focus({direction="d"}))

-- Move focus (Vim keys)
hl.bind(SUPER .. "+H", hl.dsp.focus({direction="l"}))
hl.bind(SUPER .. "+L", hl.dsp.focus({direction="r"}))
hl.bind(SUPER .. "+K", hl.dsp.focus({direction="u"}))
hl.bind(SUPER .. "+J", hl.dsp.focus({direction="d"}))

-- Resize (repeating)
hl.bind(SUPER_CTRL .. "+H", hl.dsp.window.resize({ x = -50, y = 0, relative = true }), { repeating = true })
hl.bind(SUPER_CTRL .. "+L", hl.dsp.window.resize({ x = 50, y = 0, relative = true }), { repeating = true })
hl.bind(SUPER_CTRL .. "+K", hl.dsp.window.resize({ x = 0, y = -50, relative = true }), { repeating = true })
hl.bind(SUPER_CTRL .. "+J", hl.dsp.window.resize({ x = 0, y = 50, relative = true }), { repeating = true })

-- Move windows
hl.bind(SUPER_SHIFT .. "+H", hl.dsp.window.move({ direction = "l" }))
hl.bind(SUPER_SHIFT .. "+L", hl.dsp.window.move({ direction = "r" }))
hl.bind(SUPER_SHIFT .. "+K", hl.dsp.window.move({ direction = "u" }))
hl.bind(SUPER_SHIFT .. "+J", hl.dsp.window.move({ direction = "d" }))

-- Switch workspaces with SUPER + [0-9]
-- Move and follow active window to a workspace with SUPER + SHIFT + [0-9]
-- Move active window without follow to a workspace with SUPER + CTRL + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(SUPER .. "+" .. key, hl.dsp.focus({ workspace=i }))
    hl.bind(SUPER_SHIFT .. "+" .. key, hl.dsp.window.move({ workspace=i, follow=true }))
    hl.bind(SUPER_CTRL .. "+" .. key, hl.dsp.window.move({ workspace=i, follow=false }))
end

hl.bind(SUPER_SHIFT .. "+COMMA", hl.dsp.window.move({ workspace = "-1", follow = true }))
hl.bind(SUPER_SHIFT .. "+PERIOD", hl.dsp.window.move({ workspace = "+1", follow = true }))

-- Example special workspace (scratchpad)
hl.bind(SUPER .. "+S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(SUPER .. "+SHIFT+S", hl.dsp.window.move({ workspace = "special:magic", follow = true }))

-- Cursor zoom
hl.bind(SUPER .. "+mouse_down", function() utils.zoom(-0.1) end)
hl.bind(SUPER .. "+mouse_up", function() utils.zoom(0.1) end)

hl.bind(SUPER .. "+EQUAL", function() utils.zoom(0.1) end, {repeating=true})
hl.bind(SUPER .. "+MINUS", function() utils.zoom(-0.1) end, {repeating=true})
hl.bind(SUPER .. "+KP_ADD", function() utils.zoom(0.1) end, {repeating=true})
hl.bind(SUPER .. "+KP_SUBTRACT", function() utils.zoom(-0.1) end, {repeating=true})

-- Scratchpads/Special workspaces
hl.bind(SUPER_ALT .. "+P", hl.dsp.exec_cmd(utils.scratchpad_cmd({
    identifier="Whatsapp",
    scratch="Whatsapp",
    exec= vars.SCRATCHPAD_BROWSER .. " --app=https://web.whatsapp.com"
})))

hl.bind(SUPER_ALT .. "+SPACE", hl.dsp.exec_cmd(utils.scratchpad_cmd({
    identifier="Youtube Music",
    scratch="Music",
    exec= vars.SCRATCHPAD_BROWSER .. " --app=https://music.youtube.com"
})))

hl.bind(SUPER .. "+E", hl.dsp.exec_cmd(utils.scratchpad_cmd({
    identifier="yazi",
    scratch="Yazi",
    exec="kitty --class yazi -e yazi"
})))


hl.bind(SUPER .. "+V", hl.dsp.exec_cmd(
    "kitty --class clipse -o font_size=14 -e clipse",
    {float=true, size={"(monitor_w*0.5)", "(monitor_h*0.5)"}}
))

hl.bind(SUPER .. "+PERIOD", hl.dsp.focus({workspace="e+1"}))
hl.bind(SUPER .. "+COMMA", hl.dsp.focus({workspace="e-1"}))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(SUPER .. "+mouse:272", hl.dsp.window.drag())
hl.bind(SUPER .. "+mouse:273", hl.dsp.window.resize())

-- Laptop multimedia keys for volume and LCD brightness
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(vars.VOLUME .. " --inc"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(vars.VOLUME .. " --dec"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd(vars.VOLUME .. " --toggle"), { locked = true, repeating = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd(vars.VOLUME .. " --toggle-mic"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd(vars.BRIGHTNESS .. " --inc"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(vars.BRIGHTNESS .. " --dec"), { locked = true, repeating = true })

-- Hyprsunset controls
hl.bind(SUPER_ALT .. " +I", hl.dsp.exec_cmd("hyprctl hyprsunset gamma +5"), {locked = true, repeating=true})
hl.bind(SUPER_ALT .. " +U", hl.dsp.exec_cmd("hyprctl hyprsunset gamma -5"),{locked = true, repeating=true} )
hl.bind(SUPER_ALT .. " +0", hl.dsp.exec_cmd("hyprctl hyprsunset temperature +200"),{locked = true, repeating=true})
hl.bind(SUPER_ALT .. " +9", hl.dsp.exec_cmd("hyprctl hyprsunset temperature -200"),{locked = true, repeating=true})
hl.bind(SUPER .. " +O", hl.dsp.exec_cmd("hyprctl hyprsunset reset"),{locked = true})
hl.bind(SUPER_ALT .. " +O", hl.dsp.exec_cmd("hyprctl hyprsunset identity"),{locked = true})

hl.bind(SUPER_ALT .. "+PERIOD", hl.dsp.exec_cmd(vars.VOLUME .. " --inc"), { locked = true, repeating = true })
hl.bind(SUPER_ALT .. "+COMMA", hl.dsp.exec_cmd(vars.VOLUME .. " --dec"), { locked = true, repeating = true })
hl.bind(SUPER .. "+M", hl.dsp.exec_cmd(vars.VOLUME .. " --toggle"), { locked = true, repeating = true })
hl.bind(SUPER_ALT .. "+M", hl.dsp.exec_cmd(vars.VOLUME .. " --toggle-mic"), { locked = true, repeating = true })
hl.bind(SUPER .. "+X", hl.dsp.exec_cmd(vars.BRIGHTNESS .. " --inc"), { locked = true, repeating = true })
hl.bind(SUPER .. "+Z", hl.dsp.exec_cmd(vars.BRIGHTNESS .. " --dec"), { locked = true, repeating = true })

-- Media controls
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"))
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"))
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"))
hl.bind("XF86AudioStop", hl.dsp.exec_cmd("playerctl stop"))

hl.bind(SUPER_ALT .. "+RIGHT", hl.dsp.exec_cmd("playerctl next"))
hl.bind(SUPER_ALT .. "+LEFT", hl.dsp.exec_cmd("playerctl previous"))
hl.bind(SUPER_ALT .. "+UP", hl.dsp.exec_cmd("playerctl stop"))
hl.bind(SUPER_ALT .. "+DOWN", hl.dsp.exec_cmd("playerctl play-pause"))

hl.bind(SUPER_ALT .. "+L", hl.dsp.exec_cmd("playerctl next"))
hl.bind(SUPER_ALT .. "+J", hl.dsp.exec_cmd("playerctl previous"))
hl.bind(SUPER_ALT .. "+K", hl.dsp.exec_cmd("playerctl play-pause"))

-- Plugins
-- hl.bind("SUPER+D", hl.dsp.hyprexpo_expo("toggle"))
