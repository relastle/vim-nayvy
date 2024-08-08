if vim.g.nayvy_cmp_enabled ~= 1 then
	return
end

require("cmp").register_source("nayvy", require("cmp_nayvy").new())
