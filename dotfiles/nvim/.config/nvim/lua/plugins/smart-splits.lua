return {
  "mrjones2014/smart-splits.nvim",
  lazy = false,
  keys = {
    { "<A-h>",             function() require("smart-splits").resize_left() end,  desc = "Resize split left" },
    { "<A-j>",             function() require("smart-splits").resize_down() end,  desc = "Resize split down" },
    { "<A-k>",             function() require("smart-splits").resize_up() end,    desc = "Resize split up" },
    { "<A-l>",             function() require("smart-splits").resize_right() end, desc = "Resize split right" },

    { '<leader><leader>h', function() require('smart-splits').swap_buf_left() end},
    { '<leader><leader>j', function() require('smart-splits').swap_buf_down() end},
    { '<leader><leader>k', function() require('smart-splits').swap_buf_up() end},
    { '<leader><leader>l', function() require('smart-splits').swap_buf_right() end},
  },
}
