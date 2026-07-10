-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.g.lazyvim_news_email = false

-- Mouse support (VS Code-like experience)
vim.opt.mouse = "a"              -- enable mouse in all modes
vim.opt.mousemodel = "popup"     -- right-click shows popup menu
vim.opt.selectmode = "mouse"     -- mouse selects in visual mode

-- UI polish
vim.opt.cursorline = true        -- highlight current line
vim.opt.termguicolors = true     -- 24-bit color
vim.opt.scrolloff = 8            -- keep 8 lines above/below cursor
vim.opt.sidescrolloff = 8        -- keep 8 columns left/right of cursor
vim.opt.wrap = false             -- no line wrap (like VS Code default)
vim.opt.linebreak = true         -- break at word boundary when wrap on
vim.opt.foldcolumn = "0"         -- no fold column (avoid garbled chars)
vim.opt.foldlevel = 99           -- unfold all by default

-- Status line
vim.opt.laststatus = 3           -- global statusline

-- Chinese locale for UI
vim.opt.langmenu = "zh_CN.UTF-8"
vim.api.nvim_create_autocmd("VimEnter", {
  callback = function()
    vim.cmd("language messages zh_CN.UTF-8")
  end,
})
