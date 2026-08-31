-- Applies a named dotmanager theme to this nvim session. The name-to-
-- colorscheme mapping lives here (nvim-specific detail); the Python side
-- (core/theme_appliers/nvim_theme.py) only ever deals with the theme name
-- itself, same as it does for kitty/lsd.
local M = {}

local PROFILES = {
  ["gruvbox-dark"] = { colorscheme = "gruvbox", background = "dark" },
  ["catppuccin-macchiato-mauve"] = { colorscheme = "catppuccin", background = "dark" },
  ["github-light"] = { colorscheme = "vscode", background = "light" },
}

function M.apply(name)
  local profile = PROFILES[name]
  if not profile then
    vim.notify("dotmanager: unknown nvim theme '" .. tostring(name) .. "'", vim.log.levels.WARN)
    return
  end
  vim.o.background = profile.background
  vim.cmd.colorscheme(profile.colorscheme)
end

return M
