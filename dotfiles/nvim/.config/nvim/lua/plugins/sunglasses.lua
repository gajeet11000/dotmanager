return {
	"miversen33/sunglasses.nvim",
	opts = {
		filter_type = "SHADE",
		filter_percent = 0.50,
		excluded_filetypes = {
			"snacks_picker_list",
		},
	},

	config = function(_, opts)
		require("sunglasses").setup(opts)

		-- Start with dimming disabled
		vim.cmd("SunglassesDisable")
	end,
}
