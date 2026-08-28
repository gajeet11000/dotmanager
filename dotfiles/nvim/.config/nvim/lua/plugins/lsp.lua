return {
  {
    "mason-org/mason.nvim",
    opts = {},
  },

  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    opts = {
      ensure_installed = {
        "prettierd",
        "stylua",
        "djlint",
      },
    },
  },

  {
    "mason-org/mason-lspconfig.nvim",
    opts = {
      ensure_installed = {
        "lua_ls",

        "jdtls",

        "basedpyright",
        "ruff",

        "ts_ls",
        "eslint",
        "html",
        "cssls",
        "emmet_language_server",

        "jsonls",
        "bashls",
        "jinja_lsp",

        "yamlls",

        "dockerls",
        "docker_compose_language_service",

        "marksman",
      }
    },
  },

  {
    "neovim/nvim-lspconfig",
    config = function()
      local settings = require("servers")
      for server, opts in pairs(settings) do
        vim.lsp.config(server, { settings = { [server] = opts } })
        vim.lsp.enable(server)
      end
    end,
  },
}
