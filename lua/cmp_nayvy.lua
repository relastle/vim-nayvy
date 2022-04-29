local cmp = require('cmp')
local source = {}

vim.api.nvim_command("python3 from nayvy_vim_if import *")

source.new = function()
  local self = setmetatable({}, { __index = source })
  return self
end

---Return this source is available in current context or not. (Optional)
---@return boolean
function source:is_available()
  return true
end

---Return the debug name of this source. (Optional)
---@return string
function source:get_debug_name()
  return 'debug name'
end

---Return keyword pattern for triggering completion. (Optional)
---If this is ommited, nvim-cmp will use default keyword pattern. See |cmp-config.completion.keyword_pattern|
---@return string
-- function source:get_keyword_pattern()
--   return [[\k\+]]
-- end

---Return trigger characters for triggering completion. (Optional)
-- function source:get_trigger_characters()
--   return { '.' }
-- end
--
local nayvy_single_import_to_item = function(single_import)
  return {
    insertText = single_import.name;
    filterText = single_import.name;
    label = single_import.name .. string.format('  (%s)', single_import.trimmed_statement),
    statement = single_import.statement;
    level = single_import.level;
    kind = 14,
    documentation = single_import.info;
  }
end

---Invoke completion. (Required)
---@param params cmp.SourceCompletionApiParams
---@param callback fun(response: lsp.CompletionResponse|nil)
function source:complete(params, callback)
  local single_imports = vim.fn.pyeval("nayvy_list_imports(80)")
  local res = {}
  for key, single_import in pairs(single_imports) do
    table.insert(res, nayvy_single_import_to_item(single_import))
  end
  callback(res)
end

---Resolve completion item. (Optional)
---@param completion_item lsp.CompletionItem
---@param callback fun(completion_item: lsp.CompletionItem|nil)
function source:resolve(completion_item, callback)
  completion_item.documentation = {
    kind = cmp.lsp.MarkupKind.Markdown,
    value = completion_item.documentation,
  }
  callback(completion_item)
end


---Execute command after item was accepted.
---@param completion_item lsp.CompletionItem
---@param callback fun(completion_item: lsp.CompletionItem|nil)
function source:execute(completion_item, callback)
  vim.fn.pyeval(string.format("nayvy_import_stmt('%s', %s)", completion_item.statement, completion_item.level))
  callback(completion_item)
end

---Register custom source to nvim-cmp.
return source
