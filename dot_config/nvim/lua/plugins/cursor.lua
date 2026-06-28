return {
  {
    "karb94/neoscroll.nvim",
    opts = {},
  },
  {
    "sphamba/smear-cursor.nvim",
    lazy = false,
    priority = 1000,
    opts = {
      cursor_color = "#a8aba0",
      smear_between_buffers = true,
      smear_between_windows = true,
      smear_when_dragging = true,
      smear_when_composing = true,
      smear_terminal_mode = true,
      legacy_computing_symbols_support = false,
      stiff = 0.6,
      trailing_stiff = 0.13,
      distance_stop_animating = 0.5,
      etale = 0.5,
    },
  },
}
