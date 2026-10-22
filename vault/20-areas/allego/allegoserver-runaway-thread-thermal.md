---
type: incident
area: allego
status: active
status-note: "recurs after the GUI closes; seen again 2026-09-29 (a core spinning for 6 days)"
created: 2026-08-23
tags: [allego, allegoserver, thermal, incident, nvr]
---

# allegoserver leaves a thread spinning a core after the GUI closes

> [!abstract] TL;DR
> **What broke.** On 2026-08-23 the recurring `nvr_cpu_temperature` warnings on `e10ubuntu` were traced to `allegoserver`, not to Frigate, the desktop or the known cooling limit. One thread was pinned at 100 % of a P-core for about 23 h, after the Allego GUI had been closed.
> **Fix.** `kill <pid>` (plain SIGTERM) was enough. Check for the orphan explicitly after closing Allego.

> [!info] Promoted from a Claude memory file on 2026-10-22
> Written from the memory note `allegoserver-runaway-thread-thermal` (saved 2026-08-23). The earlier, different April event is [[2026-04-02-allegoserver-thermal-spikes]]. The journal of 2026-09-29 records the spin returning and running for 6 days without affecting that day's work ([[2026-09-29]]).

## Investigation

`/opt/allego/resources/radix/allegoserver/allegoserver hardware` (started 2026-08-18 18:40) had one thread pinned at 100.0 % of a single P-core for about 23 h. `top -H -p <pid>` showed the hot thread in state `R`, TIME+ 24h24m, while its 7 sibling threads had about 11 min each. `nr_voluntary_switches` delta was 0 per second and only about 4 switches per second in total, so it is a true spin loop: no syscalls, no I/O, not waiting on anything.

- **Closing the Allego GUI does not kill `allegoserver`.** It kept spinning after the window was closed ([[allego-orphaned-server-blocks-the-rig]]).
- It was spinning while idle: all 4 radiens ports `R_OFF`, no `.xdat` written.
- `kill <pid>` (plain SIGTERM) was enough. No `-9`.

## Measured effect (package capped at PL1 20 W)

| | with spinning thread | after kill |
|---|---|---|
| package temp | 71 °C (peaked 80-81) | 59-61 °C |
| package power | 27.8 W | 17.0 W |
| `nvr_cpu_temperature` | latched WARNING | cleared |

About 10 W and 10-12 °C from one stuck thread: the difference between normal and the alarm.

## Diagnostic gotchas

- **`ps -eo pcpu` is a lifetime average, not current load.** It made the desktop stack (Xorg, GNOME, RustDesk, Obsidian) look like the heat source when it was not. Use `top -b -n2` and read the second sample.
- **Load average is misleading here.** It sat at about 6 with the CPU 86 % idle, because D-state `kworker/u76:*+i915_flip` threads count toward Linux loadavg. Same source as the persistent about 10 % iowait. Not real load.
- The alarm has hysteresis: `warn: $this > (($status >= $WARNING) ? (75) : (85))` in `/etc/netdata/health.d/nvr-alerts.conf` line 168. It fires at 85 °C and clears only below 75 °C, so it stays latched through the 80 °C range.
- The co-firing `nvr_swap_usage` warning is a false positive: about 6-7 GiB swapped but `si/so = 0` and 25 GiB available; stale pages, the biggest holder being Frigate's own main process. It warns above 50 % and clears below 40 %.

If the spin returns on the next Allego launch it is reproducible and worth reporting to Kontex.
