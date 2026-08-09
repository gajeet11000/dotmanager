local utils = require "config.utils"
return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  ---@type snacks.Config
  opts = {
    -- your configuration comes here
    -- or leave it empty to use the default settings
    -- refer to the configuration section below
    bigfile = { enabled = true },
    dashboard = { enabled = true },
    explorer = { enabled = true },
    indent = { enabled = true },
    input = { enabled = true },

    picker = {
      enabled = true,
      sources = {
        explorer = {
          hidden = true,
          actions = {
            open_oil_float = utils.open_oil_using_explorer
          },
          win = {
            list = {
              keys = {
                ["O"] = "open_oil_float"
              }
            }
          }
        }
      },
      win = {
        input = {
          keys = {
            ["<C-h>"] = { "edit_split", mode = { "i", "n" } },
            ["<C-v>"] = { "edit_vsplit", mode = { "i", "n" } },
          },
        },
        list = {
          keys = {
            ["<C-h>"] = "edit_split",
            ["<C-v>"] = "edit_vsplit",
          },
        },
      },
    },
    notifier = { enabled = true },
    quickfile = { enabled = true },
    scope = { enabled = true },
    scroll = { enabled = true },
    statuscolumn = { enabled = true },
    words = { enabled = true },
  },

  keys = {
    -- Top Pickers & Explorer
    { "<leader><space>", function() Snacks.picker.smart() end,                  desc = "Smart Find Files" },
    { "<leader>,",       function() Snacks.picker.buffers() end,                desc = "Buffers" },
    { "<leader>/",       function() Snacks.picker.grep() end,                   desc = "Grep" },
    { "<leader>:",       function() Snacks.picker.command_history() end,        desc = "Command History" },
    { "<leader>n",       function() Snacks.picker.notifications() end,          desc = "Notification History" },
    { "<leader>e",       function() Snacks.explorer() end,                      desc = "File Explorer" },

    -- find
    { "<leader>ff",      function() Snacks.picker.files({ hidden = true }) end, desc = "Find Files" },
    { "<leader>fg",      function() Snacks.picker.git_files() end,              desc = "Find Git Files" },
    { "<leader>fp",      function() Snacks.picker.projects() end,               desc = "Projects" },
    { "<leader>fr",      function() Snacks.picker.recent() end,                 desc = "Recent" },

    -- git
    { "<leader>gB",      function() Snacks.picker.git_branches() end,           desc = "Git Branches" },
    { "<leader>fgl",     function() Snacks.picker.git_log() end,                desc = "Git Log" },
    { "<leader>fgL",     function() Snacks.picker.git_log_line() end,           desc = "Git Log Line" },
    { "<leader>fgs",     function() Snacks.picker.git_status() end,             desc = "Git Status" },
    { "<leader>fgS",     function() Snacks.picker.git_stash() end,              desc = "Git Stash" },
    { "<leader>fgd",     function() Snacks.picker.git_diff() end,               desc = "Git Diff (Hunks)" },
    { "<leader>fgf",     function() Snacks.picker.git_log_file() end,           desc = "Git Log File" },

    -- gh
    -- { "<leader>gi", function() Snacks.picker.gh_issue() end, desc = "GitHub Issues (open)" },
    -- { "<leader>gI", function() Snacks.picker.gh_issue({ state = "all" }) end, desc = "GitHub Issues (all)" },
    -- { "<leader>gp", function() Snacks.picker.gh_pr() end, desc = "GitHub Pull Requests (open)" },
    -- { "<leader>gP", function() Snacks.picker.gh_pr({ state = "all" }) end, desc = "GitHub Pull Requests (all)" },

    -- Grep
    { "<leader>sb",      function() Snacks.picker.lines() end,                  desc = "Buffer Lines" },
    { "<leader>sB",      function() Snacks.picker.grep_buffers() end,           desc = "Grep Open Buffers" },
    { "<leader>sw",      function() Snacks.picker.grep_word() end,              desc = "Visual selection or word", mode = { "n", "x" } },

    -- search
    { '<leader>s"',      function() Snacks.picker.registers() end,              desc = "Registers" },
    { '<leader>s/',      function() Snacks.picker.search_history() end,         desc = "Search History" },
    { "<leader>sb",      function() Snacks.picker.lines() end,                  desc = "Buffer Lines" },
    { "<leader>sC",      function() Snacks.picker.commands() end,               desc = "Commands" },
    { "<leader>sd",      function() Snacks.picker.diagnostics() end,            desc = "Diagnostics" },
    { "<leader>sD",      function() Snacks.picker.diagnostics_buffer() end,     desc = "Buffer Diagnostics" },
    { "<leader>sh",      function() Snacks.picker.help() end,                   desc = "Help Pages" },
    { "<leader>si",      function() Snacks.picker.icons() end,                  desc = "Icons" },
    { "<leader>sj",      function() Snacks.picker.jumps() end,                  desc = "Jumps" },
    { "<leader>sk",      function() Snacks.picker.keymaps() end,                desc = "Keymaps" },
    { "<leader>sm",      function() Snacks.picker.marks() end,                  desc = "Marks" },
    { "<leader>su",      function() Snacks.picker.undo() end,                   desc = "Undo History" },
    { "<leader>uC",      function() Snacks.picker.colorschemes() end,           desc = "Colorschemes" },

    -- LSP
    { "gd",              function() Snacks.picker.lsp_definitions() end,        desc = "Goto Definition" },
    { "gD",              function() Snacks.picker.lsp_declarations() end,       desc = "Goto Declaration" },
    { "gr",              function() Snacks.picker.lsp_references() end,         nowait = true,                     desc = "References" },
    { "gI",              function() Snacks.picker.lsp_implementations() end,    desc = "Goto Implementation" },
    { "gy",              function() Snacks.picker.lsp_type_definitions() end,   desc = "Goto T[y]pe Definition" },
    { "gai",             function() Snacks.picker.lsp_incoming_calls() end,     desc = "C[a]lls Incoming" },
    { "gao",             function() Snacks.picker.lsp_outgoing_calls() end,     desc = "C[a]lls Outgoing" },
    { "<leader>ss",      function() Snacks.picker.lsp_symbols() end,            desc = "LSP Symbols" },
    { "<leader>sS",      function() Snacks.picker.lsp_workspace_symbols() end,  desc = "LSP Workspace Symbols" },

    -- Other
    { "<leader>z",       function() Snacks.zen() end,                           desc = "Toggle Zen Mode" },
    { "<leader>.",       function() Snacks.scratch() end,                       desc = "Toggle Scratch Buffer" },
    { "<leader>n",       function() Snacks.notifier.show_history() end,         desc = "Notification History" },
    { "<leader>bd",      function() Snacks.bufdelete() end,                     desc = "Delete Buffer" },
    { "<leader>cR",      function() Snacks.rename.rename_file() end,            desc = "Rename File" },
    -- { "<leader>gB",      function() Snacks.gitbrowse() end,                    desc = "Git Browse",               mode = { "n", "v" } },
    { "<leader>gg",      function() Snacks.lazygit() end,                       desc = "Lazygit" },
    { "]]",              function() Snacks.words.jump(vim.v.count1) end,        desc = "Next Reference",           mode = { "n", "t" } },
    { "[[",              function() Snacks.words.jump(-vim.v.count1) end,       desc = "Prev Reference",           mode = { "n", "t" } },

    {
      "<leader>bo",
      function()
        local current = vim.api.nvim_get_current_buf()
        Snacks.bufdelete({
          filter = function(buf)
            return buf ~= current
          end,
        })
      end,
      desc = "Close Other Buffers (keep splits)",
    }
  }
}
