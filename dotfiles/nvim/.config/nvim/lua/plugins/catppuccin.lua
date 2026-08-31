return { 
  "catppuccin/nvim",
  lazy = false,
  name = "catppuccin",
  priority = 1000,
  opts = {
    flavour = "macchiato",
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

