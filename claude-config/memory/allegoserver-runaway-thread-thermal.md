---
name: allegoserver-runaway-thread-thermal
description: allegoserver leaves a thread spinning 100% of a P-core after the Allego GUI closes, which is what triggered the Netdata CPU temperature warnings on 2026-08-23
metadata:
  type: project
---

On 2026-08-23 the recurring `nvr_cpu_temperature` Slack/Netdata warnings on `e10ubuntu`
were traced to `allegoserver`, NOT to Frigate, the desktop, or the known cooling limit.

`/opt/allego/resources/radix/allegoserver/allegoserver hardware` (started 2026-08-18 18:40)
had ONE thread pinned at 100.0% of a single P-core for ~23 h continuously. Confirmed by
`top -H -p <pid>`: hot thread state `R`, TIME+ 24h24m, while its 7 sibling threads had
~11 min each. `nr_voluntary_switches` delta = 0/s and only ~4 switches/s total, so it is a
true spin loop — no syscalls, no I/O, not waiting on anything.

Key facts:
- **Closing the Allego GUI does NOT kill `allegoserver`.** It kept spinning after the
  window was closed. Check for the orphan explicitly.
- It was spinning while **idle** — all 4 radiens ports `R_OFF`, no `.xdat` written.
- `kill <pid>` (plain SIGTERM) was enough. No `-9`.

Measured effect of that one core, on a package capped at PL1 20 W:

| | with spinning thread | after kill |
|---|---|---|
| package temp | 71 °C (peaked 80-81) | 59-61 °C |
| package power | 27.8 W | 17.0 W |
| `nvr_cpu_temperature` | latched WARNING | cleared |

So ~10 W and ~10-12 °C from one stuck thread — the difference between normal and the alarm.

Diagnostic gotchas found along the way:
- **`ps -eo pcpu` is a LIFETIME AVERAGE, not current load.** It made the desktop stack
  (Xorg/GNOME/RustDesk/Obsidian) look like the heat source when it was not. Use
  `top -b -n2` and read the SECOND sample for instantaneous CPU.
- **Load average is misleading here.** It sat at ~6 with the CPU 86% idle, because
  D-state `kworker/u76:*+i915_flip` threads count toward Linux loadavg. Same source as the
  persistent ~10% iowait. Not real load.
- Alarm has hysteresis: `warn: $this > (($status >= $WARNING) ? (75) : (85))` in
  `/etc/netdata/health.d/nvr-alerts.conf:168`. Fires at 85 °C, only clears below 75 °C,
  so it stays latched through the 80 °C range.
- The co-firing `nvr_swap_usage` warning is a FALSE POSITIVE: ~6-7 GiB swapped but
  `si/so = 0` and 25 GiB available. Stale pages, biggest holder is Frigate's own main
  process. Warns >50%, clears <40%, so it stays lit and can be ignored.

If the spin returns on the next Allego launch, it is reproducible and worth reporting to
Kontex. See [[eeg-rig-current-state]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐ **[allegoserver spins a core after the GUI closes](allegoserver-runaway-thread-thermal.md)** — +10 W/+11 °C. `ps %CPU` = lifetime avg, misleads.
