return {
  'akinsho/bufferline.nvim',
  lazy = false,
  opts = {
    options = {
      indicator = {
        icon = "▔",
        style = "underline",
      },
      show_close_icon = false,
      show_buffer_close_icons = false,
      max_name_length = 20,
      max_prefix_length = 15,
      truncate_names = true,
      diagnostics = "nvim_lsp",
      separator_style = "thick", -- visible divider between each tab
      offsets = {
        {
          filetype = "snacks_layout_box",
          text = "File Explorer",
          text_align = "center",
          separator = true,
        },
      },
    },
    highlights = {
      indicator_selected = {
        fg = "#cba6f7", -- catppuccin mocha mauve
      },
      separator = {
        fg = "#45475a", -- mocha surface1 — subtle divider between inactive tabs
      },
      separator_selected = {
        fg = "#cba6f7", -- mauve — divider next to the active tab matches the underline
      },
      separator_visible = {
        fg = "#45475a",
      },
    },
  },
  keys = {
    -- navigation
    { "<S-h>",      "<cmd>BufferLineCyclePrev<CR>",            desc = "Prev buffer" },
    { "<S-l>",      "<cmd>BufferLineCycleNext<CR>",            desc = "Next buffer" },

    -- reordering
    { "[B",         "<cmd>BufferLineMovePrev<CR>",             desc = "Move buffer prev" },
    { "]B",         "<cmd>BufferLineMoveNext<CR>",             desc = "Move buffer next" },

    -- pick / jump
    { "<leader>bj", "<cmd>BufferLinePick<CR>",                 desc = "Jump to buffer" },
    { "<leader>bc", "<cmd>BufferLinePickClose<CR>",            desc = "Pick buffer to close" },

    -- closing
    { "<leader>bl", "<cmd>BufferLineCloseLeft<CR>",            desc = "Close buffers to the left" },
    { "<leader>br", "<cmd>BufferLineCloseRight<CR>",           desc = "Close buffers to the right" },

    -- pinning
    { "<leader>bp", "<cmd>BufferLineTogglePin<CR>",            desc = "Toggle pin" },
    { "<leader>bP", "<cmd>BufferLineGroupClose ungrouped<CR>", desc = "Close all non-pinned buffers" },

    -- sorting
    { "<leader>be", "<cmd>BufferLineSortByExtension<CR>",      desc = "Sort by extension" },
    { "<leader>bD", "<cmd>BufferLineSortByDirectory<CR>",      desc = "Sort by directory" },
  },
}
