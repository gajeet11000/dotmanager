local palette = require("catppuccin.palettes").get_palette("mocha")
return {
  "nvim-zh/colorful-winsep.nvim",
  event = { "WinNew" },
  enabled = false,
  opts = {
    border = "single",
    excluded_ft = { "TelescopePrompt", "mason", "snacks_picker", "snacks_terminal" },
    colors = {  palette.mauve },
    animate = {
      enabled = false,
    }
  },
}
