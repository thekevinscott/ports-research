# 2026-09-16T22:27Z whitelist placement decided

Kevin: "the whitelist should be made generic, and there should be a way to
define it from gbnf-experiment". The copy-by-allow-set step and its tests go in
porting-harness, which today receives a finished tree and does no assembly.
gbnf-experiment supplies the set and drops its three removers. Plan updated.
