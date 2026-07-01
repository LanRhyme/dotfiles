return {
  {
    "goolord/alpha-nvim",
    event = "VimEnter",
    opts = function()
      local dashboard = require("alpha.themes.dashboard")
      
      dashboard.section.header.val = {
        "                                                     ",
        "  ███╗   ██╗███████╗ ██████╗ ██╗   ██╗██╗███╗   ███╗",
        "  ████╗  ██║██╔════╝██╔═══██╗██║   ██║██║████╗ ████║",
        "  ██╔██╗ ██║█████╗  ██║   ██║██║   ██║██║██╔████╔██║",
        "  ██║╚██╗██║██╔══╝  ██║   ██║╚██╗ ██╔╝██║██║╚██╔╝██║",
        "  ██║ ╚████║███████╗╚██████╔╝ ╚████╔╝ ██║██║ ╚═╝ ██║",
        "  ╚═╝  ╚═══╝╚══════╝ ╚═════╝   ╚═══╝  ╚═╝╚═╝     ╚═╝",
        "                                                     ",
      }
      
      dashboard.section.buttons.val = {
        dashboard.button("f", "  Find file", ":Telescope find_files <CR>"),
        dashboard.button("e", "  New file", ":ene <BAR> startinsert <CR>"),
        dashboard.button("r", "  Recently used files", ":Telescope oldfiles <CR>"),
        dashboard.button("t", "  Find text", ":Telescope live_grep <CR>"),
        dashboard.button("c", "  Configuration", ":e ~/.config/nvim/init.lua <CR>"),
        dashboard.button("l", "  Lazy", ":Lazy<CR>"),
        dashboard.button("q", "  Quit Neovim", ":qa<CR>"),
      }
      
      local function footer()
        local total_plugins = #require("lazy").plugins()
        local datetime = os.date(" %Y-%m-%d   %H:%M:%S")
        return "   " .. total_plugins .. " plugins loaded" .. datetime
      end
      
      dashboard.section.footer.val = footer()
      
      dashboard.section.footer.hl = "Type"
      dashboard.section.header.hl = "Include"
      dashboard.section.buttons.hl = "Keyword"
      
      dashboard.opts.opts.noautocmd = true
      
      return dashboard
    end,
    config = function(_, dashboard)
      local alpha = require("alpha")
      alpha.setup(dashboard.opts)
      
      vim.api.nvim_create_autocmd("User", {
        pattern = "LazyVimStarted",
        callback = function()
          local total_plugins = #require("lazy").plugins()
          local datetime = os.date(" %Y-%m-%d   %H:%M:%S")
          dashboard.section.footer.val = "   " .. total_plugins .. " plugins loaded" .. datetime
          pcall(vim.cmd.AlphaRedraw)
        end,
      })
    end,
  },
}
