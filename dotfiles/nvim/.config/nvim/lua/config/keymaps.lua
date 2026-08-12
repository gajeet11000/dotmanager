local utils = require "config.utils"
local map = vim.keymap.set


map("n", "<leader>rn", vim.lsp.buf.rename, { desc = "Rename symbol" })
map("n", "<leader>ca", vim.lsp.buf.code_action, { desc = "Code action" })
map("n", "<leader>cf", function() vim.lsp.buf.format({ async = true }) end, { desc = "Format document" })
map("n", "K", vim.lsp.buf.hover, { desc = "Hover docs" })

map("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })
map("n", "[d", vim.diagnostic.goto_prev, { desc = "Previous diagnostic" })
map("n", "<leader>dd", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
map("n", "<leader>dl", function() Snacks.picker.diagnostics() end, { desc = "Diagnostics list" })

map("n", "<C-w>h", "<C-w>s", { desc = "Open horizontal split" })

map("n", "<leader>wf", utils.toggle_zoom_tab, { desc = "Zoom/unzoom split" })

map("n", "<leader>tc", "<cmd>tabclose<CR>", { desc = "Close tab" })
map("n", "<leader>to", "<cmd>tabonly<CR>", { desc = "Close other tabs" })
map("n", "<leader>tn", "<cmd>tabnew<CR>", { desc = "New tab" })

local sunglasses_enabled = true  -- plugin dims by default on startup with no setup needed

local function toggle_sunglasses()
  sunglasses_enabled = not sunglasses_enabled
  vim.cmd("SunglassesEnableToggle")

  if sunglasses_enabled then
    -- just turned dimming ON globally — immediately un-dim the window we're sitting in
    vim.cmd("SunglassesToggle")
  end
end

vim.keymap.set("n", "<leader>ws", toggle_sunglasses, { desc = "Toggle dimming (current window stays clear)" })
