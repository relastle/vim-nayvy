vim.api.nvim_command("python3 from nayvy_vim_if.config import CONFIG")
local nayvy_cmp_enabled = vim.fn.py3eval('CONFIG.cmp_enabled')
if nayvy_cmp_enabled ~= 1 then
    return
end

require('cmp').register_source('nayvy', require('cmp_nayvy').new())
