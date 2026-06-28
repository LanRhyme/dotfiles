local M = {}

M.palette = {
  bg = "#1a1a18",
  bg_alt = "#222220",
  bg_highlight = "#2a2a28",
  bg_visual = "#3a3a35",
  bg_search = "#43423c",

  fg = "#f2f2f2",
  fg_alt = "#dededd",
  fg_dim = "#706e66",
  fg_bright = "#e8e8e7",

  rose = "#c25f63",
  rose_light = "#d47a7e",
  rose_dark = "#a04a4e",

  violet = "#afac9c",
  violet_light = "#c5c2b2",
  violet_dark = "#8a8878",

  mauve = "#c2725f",
  mauve_light = "#d4907e",
  mauve_dark = "#a05848",

  pink = "#b24355",
  pink_light = "#d06a7a",
  pink_dark = "#903040",

  green = "#a8aba0",
  green_light = "#c0c3b8",
  green_dark = "#888b80",

  blue = "#acac9f",
  blue_light = "#c4c4b7",
  blue_dark = "#8c8c7f",

  yellow = "#bdb79a",
  yellow_light = "#d5cfb2",
  yellow_dark = "#9d9780",

  orange = "#c2725f",
  orange_light = "#d4907e",
  orange_dark = "#a05848",

  red = "#b24355",
  red_light = "#d06a7a",
  red_dark = "#903040",

  cyan = "#acac9f",
  cyan_light = "#c4c4b7",
  cyan_dark = "#8c8c7f",

  -- Main accent color (green)
  accent = "#a8aba0",
  accent_light = "#c0c3b8",
  accent_dark = "#888b80",

  border = "#43423c",
  border_highlight = "#65635d",

  none = "NONE",
}

function M.setup()
  local p = M.palette

  local groups = {
    Normal = { fg = p.fg, bg = p.bg },
    NormalFloat = { fg = p.fg, bg = p.bg_alt },
    NormalNC = { fg = p.fg_alt, bg = p.bg },

    Cursor = { fg = p.bg, bg = p.green },
    CursorLine = { bg = p.bg_highlight },
    CursorLineNr = { fg = p.green_light, bold = true },
    CursorColumn = { bg = p.bg_highlight },

    LineNr = { fg = p.fg_dim },
    LineNrAbove = { fg = p.fg_dim },
    LineNrBelow = { fg = p.fg_dim },

    SignColumn = { bg = p.bg },
    SignColumnSB = { bg = p.bg_alt },

    StatusLine = { fg = p.fg, bg = p.bg_highlight },
    StatusLineNC = { fg = p.fg_dim, bg = p.bg_alt },

    WinSeparator = { fg = p.border },
    VertSplit = { fg = p.border },

    Pmenu = { fg = p.fg, bg = p.bg_alt },
    PmenuSel = { fg = p.fg_bright, bg = p.bg_visual, bold = true },
    PmenuSbar = { bg = p.bg_highlight },
    PmenuThumb = { bg = p.fg_dim },

    TabLine = { fg = p.fg_alt, bg = p.bg_alt },
    TabLineFill = { bg = p.bg_alt },
    TabLineSel = { fg = p.fg_bright, bg = p.bg, bold = true },

    Title = { fg = p.green_light, bold = true },
    Directory = { fg = p.blue_light },

    ErrorMsg = { fg = p.red_light, bold = true },
    WarningMsg = { fg = p.yellow_light, bold = true },
    MoreMsg = { fg = p.green_light },
    ModeMsg = { fg = p.fg, bold = true },
    Question = { fg = p.yellow_light },

    Search = { fg = p.fg_bright, bg = p.bg_search },
    CurSearch = { fg = p.fg_bright, bg = p.green_dark },
    IncSearch = { fg = p.fg_bright, bg = p.green_dark },
    Substitute = { fg = p.fg_bright, bg = p.red_dark },

    Visual = { bg = p.bg_visual },
    VisualNOS = { bg = p.bg_visual },

    MatchParen = { fg = p.green_light, bold = true },

    Comment = { fg = p.fg_dim, italic = true },

    Constant = { fg = p.mauve_light },
    String = { fg = p.green_light },
    Character = { fg = p.green_light },
    Number = { fg = p.mauve_light },
    Boolean = { fg = p.mauve_light },
    Float = { fg = p.mauve_light },

    Identifier = { fg = p.fg },
    Function = { fg = p.blue_light },
    Method = { fg = p.blue_light },
    Variable = { fg = p.fg },
    Parameter = { fg = p.fg_alt },
    Field = { fg = p.fg_alt },
    Property = { fg = p.fg_alt },

    Statement = { fg = p.rose_light },
    Conditional = { fg = p.rose_light },
    Repeat = { fg = p.rose_light },
    Label = { fg = p.rose_light },
    Operator = { fg = p.fg_alt },
    Keyword = { fg = p.rose_light },
    Exception = { fg = p.rose_light },

    PreProc = { fg = p.violet_light },
    Include = { fg = p.violet_light },
    Define = { fg = p.violet_light },
    Macro = { fg = p.violet_light },
    PreCondit = { fg = p.violet_light },

    Type = { fg = p.yellow_light },
    StorageClass = { fg = p.yellow_light },
    Structure = { fg = p.yellow_light },
    Typedef = { fg = p.yellow_light },

    Special = { fg = p.cyan_light },
    SpecialChar = { fg = p.cyan_light },
    Tag = { fg = p.cyan_light },
    Delimiter = { fg = p.fg_dim },
    SpecialComment = { fg = p.cyan_light, italic = true },
    Debug = { fg = p.cyan_light },

    Underlined = { underline = true },
    Bold = { bold = true },
    Italic = { italic = true },
    Strikethrough = { strikethrough = true },

    Error = { fg = p.red_light },
    Todo = { fg = p.yellow_light, bold = true },
    Note = { fg = p.blue_light, bold = true },
    Warning = { fg = p.orange_light, bold = true },

    DiffAdd = { bg = "#1a2a1a" },
    DiffChange = { bg = "#1a1a2a" },
    DiffDelete = { bg = "#2a1a1a" },
    DiffText = { bg = "#2a2a4a" },

    GitSignsAdd = { fg = p.green },
    GitSignsChange = { fg = p.blue },
    GitSignsDelete = { fg = p.red },

    DiagnosticError = { fg = p.red_light },
    DiagnosticWarn = { fg = p.orange_light },
    DiagnosticInfo = { fg = p.blue_light },
    DiagnosticHint = { fg = p.cyan_light },
    DiagnosticOk = { fg = p.green_light },

    DiagnosticSignError = { fg = p.red_light },
    DiagnosticSignWarn = { fg = p.orange_light },
    DiagnosticSignInfo = { fg = p.blue_light },
    DiagnosticSignHint = { fg = p.cyan_light },

    DiagnosticUnderlineError = { undercurl = true, sp = p.red_light },
    DiagnosticUnderlineWarn = { undercurl = true, sp = p.orange_light },
    DiagnosticUnderlineInfo = { undercurl = true, sp = p.blue_light },
    DiagnosticUnderlineHint = { undercurl = true, sp = p.cyan_light },

    LspReferenceText = { bg = p.bg_highlight },
    LspReferenceRead = { bg = p.bg_highlight },
    LspReferenceWrite = { bg = p.bg_highlight, underline = true },

    LspInfoBorder = { fg = p.border_highlight },

    TelescopeBorder = { fg = p.border, bg = p.bg_alt },
    TelescopePromptBorder = { fg = p.border, bg = p.bg_alt },
    TelescopeResultsBorder = { fg = p.border, bg = p.bg_alt },
    TelescopePreviewBorder = { fg = p.border, bg = p.bg_alt },
    TelescopeMatching = { fg = p.green_light, bold = true },
    TelescopePromptPrefix = { fg = p.green },
    TelescopeSelection = { bg = p.bg_visual, bold = true },
    TelescopeSelectionCaret = { fg = p.green },

    NeoTreeNormal = { fg = p.fg, bg = p.bg_alt },
    NeoTreeNormalNC = { fg = p.fg, bg = p.bg_alt },
    NeoTreeDimText = { fg = p.fg_dim },
    NeoTreeDirectoryName = { fg = p.fg },
    NeoTreeDirectoryIcon = { fg = p.blue },
    NeoTreeRootName = { fg = p.green_light, bold = true },
    NeoTreeFileName = { fg = p.fg },
    NeoTreeFileIcon = { fg = p.fg_alt },
    NeoTreeFileNameOpened = { fg = p.fg_bright },
    NeoTreeIndentMarker = { fg = p.fg_dim },
    NeoTreeGitAdded = { fg = p.green },
    NeoTreeGitConflict = { fg = p.red },
    NeoTreeGitDeleted = { fg = p.red },
    NeoTreeGitIgnored = { fg = p.fg_dim },
    NeoTreeGitModified = { fg = p.blue },
    NeoTreeGitUnstaged = { fg = p.orange },
    NeoTreeGitUntracked = { fg = p.yellow },
    NeoTreeGitStaged = { fg = p.green },

    CmpItemAbbr = { fg = p.fg },
    CmpItemAbbrDeprecated = { fg = p.fg_dim, strikethrough = true },
    CmpItemAbbrMatch = { fg = p.green_light, bold = true },
    CmpItemAbbrMatchFuzzy = { fg = p.green_light, bold = true },
    CmpItemKind = { fg = p.violet_light },
    CmpItemMenu = { fg = p.fg_dim },
    CmpItemKindText = { fg = p.fg },
    CmpItemKindMethod = { fg = p.blue_light },
    CmpItemKindFunction = { fg = p.blue_light },
    CmpItemKindConstructor = { fg = p.blue_light },
    CmpItemKindField = { fg = p.fg_alt },
    CmpItemKindVariable = { fg = p.fg },
    CmpItemKindClass = { fg = p.yellow_light },
    CmpItemKindInterface = { fg = p.yellow_light },
    CmpItemKindModule = { fg = p.yellow_light },
    CmpItemKindProperty = { fg = p.fg_alt },
    CmpItemKindUnit = { fg = p.mauve_light },
    CmpItemKindValue = { fg = p.mauve_light },
    CmpItemKindEnum = { fg = p.yellow_light },
    CmpItemKindKeyword = { fg = p.rose_light },
    CmpItemKindSnippet = { fg = p.cyan_light },
    CmpItemKindColor = { fg = p.cyan_light },
    CmpItemKindFile = { fg = p.fg },
    CmpItemKindReference = { fg = p.fg_alt },
    CmpItemKindFolder = { fg = p.blue },
    CmpItemKindEnumMember = { fg = p.yellow_light },
    CmpItemKindConstant = { fg = p.mauve_light },
    CmpItemKindStruct = { fg = p.yellow_light },
    CmpItemKindEvent = { fg = p.orange_light },
    CmpItemKindOperator = { fg = p.fg_alt },
    CmpItemKindTypeParameter = { fg = p.yellow_light },

    NotifyERRORBorder = { fg = p.red_dark },
    NotifyWARNBorder = { fg = p.orange_dark },
    NotifyINFOBorder = { fg = p.blue_dark },
    NotifyDEBUGBorder = { fg = p.fg_dim },
    NotifyTRACEBorder = { fg = p.mauve_dark },
    NotifyERRORIcon = { fg = p.red_light },
    NotifyWARNIcon = { fg = p.orange_light },
    NotifyINFOIcon = { fg = p.blue_light },
    NotifyDEBUGIcon = { fg = p.fg_dim },
    NotifyTRACEIcon = { fg = p.mauve_light },
    NotifyERRORTitle = { fg = p.red_light },
    NotifyWARNTitle = { fg = p.orange_light },
    NotifyINFOTitle = { fg = p.blue_light },
    NotifyDEBUGTitle = { fg = p.fg_dim },
    NotifyTRACETitle = { fg = p.mauve_light },

    WhichKey = { fg = p.fg },
    WhichKeyGroup = { fg = p.green_light },
    WhichKeyDesc = { fg = p.fg_alt },
    WhichKeySeparator = { fg = p.fg_dim },
    WhichKeyFloat = { bg = p.bg_alt },
    WhichKeyBorder = { fg = p.border },
    WhichKeyValue = { fg = p.fg_dim },

    RainbowDelimiterRed = { fg = p.red },
    RainbowDelimiterYellow = { fg = p.yellow },
    RainbowDelimiterBlue = { fg = p.blue },
    RainbowDelimiterOrange = { fg = p.orange },
    RainbowDelimiterGreen = { fg = p.green },
    RainbowDelimiterViolet = { fg = p.violet },
    RainbowDelimiterCyan = { fg = p.cyan },

    IblIndent = { fg = p.bg_highlight },
    IblWhitespace = { fg = p.bg_highlight },
    IblScope = { fg = p.fg_dim },

    MiniIndentscopeSymbol = { fg = p.fg_dim },
    MiniIndentscopePrefix = { nocombine = true },

    LazyVimSnacksIndent = { fg = p.bg_highlight },
    LazyVimSnacksDashboard = { bg = p.bg },
  }

  for group, settings in pairs(groups) do
    vim.api.nvim_set_hl(0, group, settings)
  end

  vim.g.colors_name = "morandi"
end

return M
