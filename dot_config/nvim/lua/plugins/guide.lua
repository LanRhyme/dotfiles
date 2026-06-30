return {
  -- 1. Precognition: 移动提示向导
  -- 当你不知道按什么键能最快到达某个位置时，它会在代码上显示提示
  -- 比如它会告诉你按 'w' 可以跳到下一个词，按 'e' 可以跳到词尾
  {
    "tris203/precognition.nvim",
    event = "VeryLazy",
    opts = {
      startVisible = true,
      showBlankVirtLine = true,
      highlightColor = { link = "Comment" },
      hints = {
        Caret = { text = "^", prio = 2 },
        Dollar = { text = "$", prio = 1 },
        MatchingPair = { text = "%", prio = 5 },
        Zero = { text = "0", prio = 1 },
        w = { text = "w", prio = 10 },
        b = { text = "b", prio = 9 },
        e = { text = "e", prio = 8 },
        W = { text = "W", prio = 7 },
        B = { text = "B", prio = 6 },
        E = { text = "E", prio = 5 },
      },
      gutterHints = {
        G = { text = "G", prio = 10 },
        gg = { text = "gg", prio = 9 },
        PrevParagraph = { text = "{", prio = 8 },
        NextParagraph = { text = "}", prio = 8 },
      },
    },
    keys = {
      { "<leader>cp", function() require("precognition").toggle() end, desc = "Toggle Precognition (Guide)" },
    },
  },

  -- 2. Vim Be Good: 动作练习小游戏
  -- ThePrimeagen 制作的 vim 练习插件，可以帮助你训练肌肉记忆
  {
    "ThePrimeagen/vim-be-good",
    cmd = "VimBeGood",
  },

  -- 3. Hardtime: 坏习惯纠正 (默认不启用，可根据需要打开)
  -- 阻止你连续按多次 j/k，强迫你使用跳跃命令
  {
    "m4xshen/hardtime.nvim",
    dependencies = { "MunifTanjim/nui.nvim", "nvim-lua/plenary.nvim" },
    opts = {
      disable_mouse = false,
      hint = true,
    },
    cmd = "Hardtime",
    keys = {
      { "<leader>ch", "<cmd>Hardtime toggle<cr>", desc = "Toggle Hardtime" },
    },
  },
}
