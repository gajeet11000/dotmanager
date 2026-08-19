return {
  "nvim-treesitter/nvim-treesitter",
  lazy = false,
  build = ":TSUpdate",

  config = function()
    local ts = require("nvim-treesitter")

    ts.install({
      "lua",
      "python",
      "java",
      "bash",
      "json",
      "markdown",
      "markdown_inline",
      "html",
      "css",
      "javascript",
      "typescript",
      "tsx",
      "vim",
      "vimdoc",
    })

    vim.api.nvim_create_autocmd("FileType", {
      callback = function(args)
        pcall(vim.treesitter.start, args.buf)
      end,
    })
  end,
}
