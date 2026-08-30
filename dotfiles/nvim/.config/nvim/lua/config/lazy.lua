-- Bootstrap lazy.nvim

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = "https://github.com/folke/lazy.nvim.git"
  local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
  if vim.v.shell_error ~= 0 then
    vim.api.nvim_echo({
      { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
      { out,                            "WarningMsg" },
      { "\nPress any key to exit..." },
    }, true, {})
    vim.fn.getchar()
    os.exit(1)
  end
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup("plugins")

-- Opens an RPC socket per session so `dotmanager theme set` can live-reload
-- this instance's colorscheme without a restart -- see
-- core/theme_appliers/nvim_theme.py and lua/config/theme.lua.
local sockets_dir = vim.fn.stdpath("cache") .. "/dotmanager-sockets"
vim.fn.mkdir(sockets_dir, "p")
vim.fn.serverstart(sockets_dir .. "/" .. vim.fn.getpid() .. ".sock")

require("config.theme").apply(require("config.current-theme"))
