-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.g.lazyvim_news_email = false

-- Line numbers
vim.opt.number = true
vim.opt.relativenumber = false

-- Chinese locale for UI
vim.opt.langmenu = "zh_CN.UTF-8"
vim.api.nvim_create_autocmd("VimEnter", {
  callback = function()
    vim.cmd("language messages zh_CN.UTF-8")
  end,
})
