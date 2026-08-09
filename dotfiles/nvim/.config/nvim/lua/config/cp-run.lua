-- lua/config/cp-run.lua

local function get_run_cmd(file)
  local ft = vim.bo.filetype
  local escaped_file = vim.fn.shellescape(file)
  if ft == "cpp" then
    local out = vim.fn.expand("%:p:r")
    local escaped_out = vim.fn.shellescape(out)
    return string.format("g++ -std=c++20 -O2 -Wall %s -o %s && %s", escaped_file, escaped_out, escaped_out)
  elseif ft == "python" then
    return "python3 -u " .. escaped_file
  elseif ft == "java" then
    return "java " .. escaped_file
  else
    vim.notify("No run command for filetype: " .. ft, vim.log.levels.WARN)
    return nil
  end
end

local function is_valid(win)
  return win and vim.api.nvim_win_is_valid(win)
end

-- wipe every previously tracked cp input/output buffer except the current pair
local function cleanup_old_cp_buffers(keep_input, keep_output)
  vim.t.cp_tracked_bufs = vim.t.cp_tracked_bufs or {}
  for _, bufnr in ipairs(vim.t.cp_tracked_bufs) do
    if vim.api.nvim_buf_is_valid(bufnr) then
      local name = vim.api.nvim_buf_get_name(bufnr)
      if name ~= keep_input and name ~= keep_output then
        pcall(vim.api.nvim_buf_delete, bufnr, { force = true })
      end
    end
  end
  vim.t.cp_tracked_bufs = {}
end

local function run_in_float(cmd, output_file, run_mode)
  local width = math.floor(vim.o.columns * 0.7)
  local height = math.floor(vim.o.lines * 0.7)
  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_open_win(buf, true, {
    relative = "editor",
    width = width,
    height = height,
    row = math.floor((vim.o.lines - height) / 2),
    col = math.floor((vim.o.columns - width) / 2),
    style = "minimal",
    border = "rounded",
    title = " Running: " .. vim.fn.expand("%:t") .. " in " .. run_mode .. " ",
    title_pos = "center",
  })

  vim.fn.termopen(cmd)
  vim.cmd("startinsert")

  vim.api.nvim_create_autocmd("TermClose", {
    buffer = buf,
    once = true,
    callback = function()
      local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
      vim.fn.writefile(lines, output_file)
      if is_valid(vim.t.cp_output_win) then
        vim.api.nvim_win_call(vim.t.cp_output_win, function()
          vim.cmd("edit! " .. vim.fn.fnameescape(output_file))
        end)
      end
    end,
  })
end

function CpRunFile(MODE)
  local code_win = vim.api.nvim_get_current_win()
  local stem = vim.fn.expand("%:t:r"):gsub("[%s]+", "_")
  local input_file = "/tmp/" .. stem .. "_input.txt"
  local output_file = "/tmp/" .. stem .. "_output.txt"

  if MODE == "FILE IO" then
    if vim.fn.filereadable(input_file) == 0 then vim.fn.writefile({}, input_file) end
  end
  if vim.fn.filereadable(output_file) == 0 then vim.fn.writefile({}, output_file) end

  local cmd = get_run_cmd(vim.fn.expand("%:p"))
  if not cmd then return end
  local full_cmd = (MODE == "FILE IO") and (cmd .. " < " .. vim.fn.shellescape(input_file)) or cmd

  cleanup_old_cp_buffers(input_file, output_file)

  -- force a full rebuild if the mode changed since the last run,
  -- since FILE IO and INTERACTIVE need structurally different layouts
  local mode_changed = vim.t.cp_mode ~= MODE
  vim.t.cp_mode = MODE

  local layout_ok = not mode_changed and is_valid(vim.t.cp_output_win)
      and (MODE ~= "FILE IO" or is_valid(vim.t.cp_input_win))

  if not layout_ok then
    vim.cmd("only")
    vim.cmd("vsplit")
    vim.cmd("vertical resize " .. math.floor(vim.o.columns * 0.3))

    if MODE == "FILE IO" then
      vim.t.cp_input_win = vim.api.nvim_get_current_win()
      vim.cmd("edit " .. vim.fn.fnameescape(input_file))
      vim.cmd("split")
    else
      vim.t.cp_input_win = nil
    end

    vim.t.cp_output_win = vim.api.nvim_get_current_win()
    vim.cmd("edit " .. vim.fn.fnameescape(output_file))
  else
    if MODE == "FILE IO" then
      vim.api.nvim_win_call(vim.t.cp_input_win, function()
        if vim.api.nvim_buf_get_name(0) ~= input_file then
          vim.cmd("edit " .. vim.fn.fnameescape(input_file))
        end
      end)
    end
  end

  vim.t.cp_tracked_bufs = {
    vim.fn.bufnr(input_file),
    vim.fn.bufnr(output_file),
  }

  vim.api.nvim_set_current_win(code_win)
  run_in_float(full_cmd, output_file, MODE)
end

vim.keymap.set("n", "<leader>(", function() CpRunFile("INTERACTIVE") end,
  { desc = "Run interactively (floating terminal + file output)" })
vim.keymap.set("n", "<leader>)", function() CpRunFile("FILE IO") end, { desc = "Run (floating terminal + file output)" })
