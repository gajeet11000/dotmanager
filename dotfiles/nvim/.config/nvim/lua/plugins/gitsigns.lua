return {
  "lewis6991/gitsigns.nvim",
  lazy = false,
  opts = {},
  keys = {
    { "<leader>gp", function() require("gitsigns").preview_hunk_inline() end,       desc = "Preview hunk inline (git)" },
    { "<leader>gb", function() require("gitsigns").toggle_current_line_blame() end, desc = "Toggle line blame" },
    { "<leader>gs", function() require("gitsigns").stage_hunk() end,                desc = "Stage hunk" },
  }
}
