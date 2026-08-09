local utils = require "config.utils"

return {
  'stevearc/oil.nvim',
  lazy = false,

  ---@module 'oil'
  ---@type oil.SetupOpts
  opts = {
    default_file_explorer = false,
    view_options = {
      show_hidden = true,
    },
    float = {
      padding = 2,
      max_width = 90,
      max_height = 0,
      border = "rounded",
      win_options = {
        winblend = 0,
      },
    },
  },

  keys = {
    { "<leader>O", utils.toggle_oil_current_file_directory, desc = "Open Oil (current file directory)" },
  }

}
