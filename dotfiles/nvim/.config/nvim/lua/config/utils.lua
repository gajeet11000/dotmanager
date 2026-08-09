local M = {}

function M.toggle_oil_current_file_directory()
  local dir = vim.fn.expand("%:p:h")
  require("oil").open_float(dir)
end

function M.open_oil_using_explorer(picker, item)
  if not item then
    return
  end

  local dir

  if item.dir then
    dir = item.file
  else
    dir = vim.fn.fnamemodify(item.file, ":p:h")
  end

  require("oil").open_float(dir)
end

function M.toggle_zoom()
  if vim.t.zoom_winrestcmd then
    vim.cmd(vim.t.zoom_winrestcmd)
    vim.t.zoom_winrestcmd = nil
  else
    vim.t.zoom_winrestcmd = vim.fn.winrestcmd()
    vim.cmd("wincmd |")
    vim.cmd("wincmd _")
  end
end

return M
