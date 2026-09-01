-- flavour is read from the active dotmanager theme (config/theme.lua's
-- M.PROFILES), not hardcoded -- lazy.nvim evaluates this opts table at
-- startup, before config/lazy.lua's M.apply(...) call switches the actual
-- colorscheme, so this is the only place that can pick the right flavour
-- for whichever catppuccin-flavoured theme is currently active. Falls
-- back to "macchiato" if the current theme isn't a catppuccin one at all
-- (this plugin's config still loads either way, just unused).
local current_theme = require("config.current-theme")
local profile = require("config.theme").PROFILES[current_theme]
local flavour = (profile and profile.flavour) or "macchiato"

return {
  "catppuccin/nvim",
  lazy = false,
  name = "catppuccin",
  priority = 1000,
  opts = {
    flavour = flavour,
    transparent_background = true,
    -- transparent_background strips background from more than just the
    -- editor area -- WinBar (vim.opt.winbar = "%t" in config/options.lua)
    -- gets no background at all otherwise, rendering as an unstyled
    -- blank/white strip instead of matching the rest of the UI.
    custom_highlights = function(colors)
      return {
        WinBar = { bg = colors.mantle, fg = colors.text },
        WinBarNC = { bg = colors.mantle, fg = colors.overlay0 },
      }
    end,
  }
}
