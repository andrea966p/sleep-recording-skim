---
name: allegoserver-runaway-thread-thermal
description: "2026-08-23: allegoserver left one thread spinning 100 % of a P-core after the Allego GUI closed (+10 W, +11 C), triggering Netdata CPU temperature warnings; plain kill fixes it."
metadata:
  type: project
---

**2026-08-23:** `nvr_cpu_temperature` Netdata warnings on e10 were one spinning `allegoserver` thread (100 % of a P-core for ~23 h, idle, all ports R_OFF, no syscalls). Closing the Allego GUI does NOT kill `allegoserver`. Plain `kill <pid>` (no -9) fixed it: package 71 -> 59-61 C, 27.8 -> 17.0 W. If it returns on a fresh launch it is reproducible and worth reporting to Kontex.

Details: [[allegoserver-runaway-thread-thermal]]

Diagnostic gotchas: `ps -eo pcpu` is a LIFETIME average (use `top -b -n2`, read the second sample); load average here is inflated by D-state i915 kworkers; the co-firing `nvr_swap_usage` warning is a false positive (si/so = 0).
