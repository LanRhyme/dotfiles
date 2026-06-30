return {
  -- Smooth scrolling like VS Code
  {
    "karb94/neoscroll.nvim",
    config = function()
      require("neoscroll").setup({})
    end,
  },

  -- Peek definition/references (similar to VS Code's Alt+F12)
  {
    "dnlhc/glance.nvim",
    cmd = "Glance",
    keys = {
      { "gD", "<cmd>Glance definitions<CR>", desc = "Glance Definitions" },
      { "gR", "<cmd>Glance references<CR>", desc = "Glance References" },
      { "gY", "<cmd>Glance type_definitions<CR>", desc = "Glance Type Definitions" },
      { "gM", "<cmd>Glance implementations<CR>", desc = "Glance Implementations" },
    },
    config = function()
      require("glance").setup({})
    end,
  },

  -- VS Code like Outline / Symbol explorer
  {
    "stevearc/aerial.nvim",
    opts = function()
      local icons = require("lazyvim.config").icons
      local icons_empty = {}
      for key, _ in pairs(icons.kinds) do
        icons_empty[key] = ""
      end
      return {
        attach_mode = "global",
        backends = { "lsp", "treesitter", "markdown", "man" },
        show_guides = true,
        layout = {
          max_width = { 40, 0.2 },
          width = nil,
          min_width = 30,
          default_direction = "right",
        },
        icons = icons.kinds,
        filter_kind = false,
        guides = {
          mid_item = "├ ",
          last_item = "└ ",
          nested_top = "│ ",
          whitespace = "  ",
        },
      }
    end,
    keys = {
      { "<leader>co", "<cmd>AerialToggle<cr>", desc = "Aerial (Symbols Outline)" },
    },
  },

  -- VS Code like horizontal terminal at the bottom
  {
    "akinsho/toggleterm.nvim",
    version = "*",
    opts = {
      size = 15,
      open_mapping = [[<c-\>]], -- Toggle terminal with Ctrl+\
      direction = "horizontal",
    }
  },

  -- Auto restore previous sessions like VS Code does
  {
    "rmagatti/auto-session",
    lazy = false,
    opts = {
      log_level = "error",
      auto_session_suppress_dirs = { "~/", "~/Projects", "~/Downloads", "/" },
    }
  },

  -- VS Code like live rename (F2 style)
  {
    "smjonas/inc-rename.nvim",
    cmd = "IncRename",
    config = true,
    keys = {
      {
        "<leader>rn",
        function()
          return ":IncRename " .. vim.fn.expand("<cword>")
        end,
        expr = true,
        desc = "Rename",
      },
    },
  },

  -- GitLens like inline blame annotations
  {
    "f-person/git-blame.nvim",
    event = "VeryLazy",
    opts = {
      enabled = true,
      message_template = " <author> • <date> • <summary>",
      date_format = "%Y-%m-%d",
    }
  },

  -- VS Code like scrollbar with diagnostic marks
  {
    "petertriho/nvim-scrollbar",
    event = "BufReadPost",
    config = function()
      require("scrollbar").setup()
    end,
  }
}
