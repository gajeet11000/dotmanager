return {
  'nvim-focus/focus.nvim',
  version = '*',
  keys = {
    { "<leader>F", "<cmd>FocusToggle<CR>", desc = "Toggle Split Auto Focus" }
  },
  opts = {
    autoresize = {
      minwidth = 12,
      minheight = 5,
      focusedwindow_minwidth = 100,
      focusedwindow_minheight = 200,
    },
    ui = {
      relativenumber = true,
      absolutenumber_unfocussed = true,
    }
  },
  config = function(_, opts)
    require("focus").setup(opts)
    vim.cmd("FocusDisable")   -- explicitly disable via command, not opts.enable
  end,
}
