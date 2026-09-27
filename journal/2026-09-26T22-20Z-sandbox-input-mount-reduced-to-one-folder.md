# 2026-09-26T22:20Z sandbox input mount reduced to one folder

Issue #74 changes the sandbox run contract to one required input folder, mounted
read-only at `/input`. The caller's prompt describes its contents. The sandbox
rejects a missing path or a regular file before Docker can create or mount an
unintended source. The sandbox unit suite passed after a red test established
the old multi-mount API did not accept the new argument.
