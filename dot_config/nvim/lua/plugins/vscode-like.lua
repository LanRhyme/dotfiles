-- VS Code-like mouse & UI experience for Neovim
return {
  -- Buffer tabs (top bar like VS Code)
  {
    "akinsho/bufferline.nvim",
    event = "VeryLazy",
    opts = {
      options = {
        mode = "buffers",
        diagnostics = "nvim_lsp",
        always_show_bufferline = false,
        offsets = {
          {
            filetype = "neo-tree",
            text = "File Explorer",
            highlight = "Directory",
            separator = true,
          },
        },
      },
    },
  },

  -- Status column: clickable line numbers + git/diagnostic signs
  {
    "luukvbaal/statuscol.nvim",
    event = "VeryLazy",
    config = function()
      local statuscol = require("statuscol")
      local builtin = require("statuscol.builtin")

      statuscol.setup({
        relculright = true,
        segments = {
          {
            sign = {
              name = { "Diagnostics" },
              maxwidth = 1,
              auto = true,
            },
            click = "v:lua.ScSa",
          },
          {
            sign = {
              name = { "GitSigns" },
              maxwidth = 1,
              auto = true,
            },
            click = "v:lua.ScSa",
          },
          {
            text = { builtin.lnumfunc, " " },
            click = "v:lua.ScLa",
          },
        },
      })
    end,
  },

  -- Scrollbar like VS Code
  {
    "petertriho/nvim-scrollbar",
    event = { "BufReadPost", "BufNewFile" },
    dependencies = { "kevinhwang91/nvim-hlslens" },
    config = function()
      require("scrollbar").setup({
        show = true,
        show_in_active_only = false,
        set_highlights = true,
        handle = { color = nil, blend = 30 },
        marks = {
          Search = { color = "yellow" },
          Error = { color = "red" },
          Warn = { color = "orange" },
          Info = { color = "blue" },
          Hint = { color = "cyan" },
          Misc = { color = "purple" },
        },
      })

      require("hlslens").setup()

      local kmap = vim.keymap.set
      kmap("n", "n", [[<Cmd>execute('normal! ' . v:count1 . 'n')<CR><Cmd>lua require('hlslens').start()<CR>]])
      kmap("n", "N", [[<Cmd>execute('normal! ' . v:count1 . 'N')<CR><Cmd>lua require('hlslens').start()<CR>]])
      kmap("n", "*", [[<Cmd>lua require('hlslens').start()<CR>]])
      kmap("n", "#", [[<Cmd>lua require('hlslens').start()<CR>]])
    end,
  },

  -- Smooth scroll like VS Code
  {
    "karb94/neoscroll.nvim",
    event = "VeryLazy",
    opts = {
      duration_multiplier = 1,
      easing = "quadratic",
    },
  },
}
