-- Only ever used in light mode here (see lua/config/theme.lua's
-- "github-light" profile), so the style is fixed at setup time rather
-- than switched at runtime.
return {
  "Mofiqul/vscode.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    require("vscode").setup({
      style = "light",
    })
  end,
}
