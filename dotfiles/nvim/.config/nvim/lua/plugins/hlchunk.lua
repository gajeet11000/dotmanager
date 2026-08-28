-- ~/.config/nvim/lua/plugins/hlchunk.lua
local colors = require("catppuccin.palettes").get_palette("mocha")

local exclude_ft = {
	dashboard = true,
	snacks_dashboard = true,
	alpha = true,
	help = true,
	lazy = true,
	mason = true,
	notify = true,
	checkhealth = true,
	lspinfo = true,
	qf = true,
	terminal = true,
}

return {
	{
		"shellRaining/hlchunk.nvim",

		event = {
			"BufReadPre",
			"BufNewFile",
		},
		opts = {
			chunk = {
				enable = true,
				priority = 15,
				use_treesitter = true,
				straight = false,
				error_sign = true,
				textobject = "ic",
				max_file_size = 1024 * 1024,
				delay = 0,
				duration = 0,
				chars = {
					horizontal_line = "─",
					vertical_line = "│",
					left_top = "╭",
					left_bottom = "╰",
					right_arrow = "─",
				},
				style = {
					{ fg = "#9584CC" }, -- Nocturne structural purple
					{ fg = colors.red },
				},
				exclude_filetypes = exclude_ft,
			},

			indent = {
				enable = true,
				priority = 10,
				use_treesitter = false,
				ahead_lines = 8,
				delay = 0,
				chars = {
					"┊",
				},
				style = {
					{ fg = colors.surface1 },
				},
				exclude_filetypes = exclude_ft,
			},

			line_num = {
				enable = true,
				priority = 8,
				use_treesitter = true,
				style = {
					fg = colors.subtext1,
					bold = true,
				},
				exclude_filetypes = exclude_ft,
			},

			blank = {
				enable = false,
			},
		},
	},
}
