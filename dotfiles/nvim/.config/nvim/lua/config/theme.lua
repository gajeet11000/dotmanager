-- Applies a named dotmanager theme to this nvim session. The name-to-
-- colorscheme mapping lives here (nvim-specific detail); the Python side
-- (core/theme_appliers/nvim_theme.py) only ever deals with the theme name
-- itself, same as it does for kitty/lsd.
local M = {}

-- `flavour` only matters for colorscheme="catppuccin" entries -- see
-- plugins/catppuccin.lua, which reads M.PROFILES directly to pick its
-- flavour at plugin-setup time (before M.apply below ever runs; lazy.nvim
-- evaluates plugin opts before config/lazy.lua's M.apply(...) call at the
-- bottom). Without this, catppuccin.nvim's flavour stays whatever's
-- hardcoded in that setup() call regardless of which dotmanager theme is
-- active -- vim.o.background alone does not change catppuccin.nvim's
-- flavour.
M.PROFILES = {
  ["gruvbox-dark"] = { colorscheme = "gruvbox", background = "dark" },
  ["catppuccin-macchiato-mauve"] = { colorscheme = "catppuccin", background = "dark", flavour = "macchiato" },
  ["catppuccin-latte"] = { colorscheme = "catppuccin", background = "light", flavour = "latte" },
}

function M.apply(name)
  local profile = M.PROFILES[name]
  if not profile then
    vim.notify("dotmanager: unknown nvim theme '" .. tostring(name) .. "'", vim.log.levels.WARN)
    return
  end
  vim.o.background = profile.background
  vim.cmd.colorscheme(profile.colorscheme)
end

return M
