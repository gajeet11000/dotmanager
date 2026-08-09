return {
  'nvim-focus/focus.nvim',
  version = '*',
  event = "VeryLazy", -- load at startup (deferred slightly), not only on first keypress
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
  keys = {
    { "<leader>F", "<cmd>FocusToggle<CR>", desc = "Toggle Split Auto Focus" }
  }
}
