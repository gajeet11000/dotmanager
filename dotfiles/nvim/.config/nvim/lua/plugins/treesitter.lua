return {
	"nvim-treesitter/nvim-treesitter",
	lazy = false,
	build = ":TSUpdate",

	opts = {
		auto_install = true,
		ensure_installed = {
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
		},
	},

	init = function()
		vim.api.nvim_create_autocmd("FileType", {
			pattern = { "<filetype>" },
			callback = function()
				vim.treesitter.start()
				vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
			end,
		})
	end,
}
