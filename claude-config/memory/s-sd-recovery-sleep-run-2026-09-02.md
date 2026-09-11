---
name: s-sd-recovery-sleep-run-2026-09-02
description: The S-SD terminal recovery-sleep endpoint, Wed 2026-09-02 13:00 to Thu 09-03 09:00, its pre-flight screen and its AMBER go/no-go.
metadata:
  type: project
---

**Wednesday 2026-09-02 13:00 KST → Thursday 2026-09-03 09:00 KST, 20.0 h**, eight S-SD positions.
Animals **SAMPLED Thursday 13:00**, four hours after it stops ⇒ **UNREPEATABLE**. Scored Thursday.

🔑 **CSD is FINISHED across this window** — a true post-protocol endpoint. NOT the same as the W-SD
08-27 run, which sat after the PENULTIMATE bout with the protocol still running
([[w-sd-recovery-sleep-run-2026-08-27]]). Always write window + weekday + protocol state.

## The pre-flight screen finally GATED instead of annotating

Two short files, 2026-09-01: `allego_0__uid0901-12-24-03` (115.7 s, after replugging) and
`allego_1__uid0901-12-38-53` (84.6 s, after Andrea re-seated everything). 🛑 **8 QC epochs each —
no usable percentage may be quoted from either.**

✅ **The re-seat fixed ALL EIGHT chip grounds.** B2 **117 → 2486 µV**, D2 **1052 → 4541 µV**, D1's
floor stopped swinging 1734-4106. ⭐ Second batch running where a bench re-mate recovered chips the
code would otherwise call dead animals — see [[weak-chip-ground-hides-as-electrode-failure]].

🎉 **D2 (HLBCSD18) came back on BOTH roles and it was a GROUND fault**: EEG rms 114-153 µV, lf/hf
24-38 vs its own floor p99 3.33, above in 21/21 epochs; EMG locked at 50 µV. Fourth passing
recording in a row for D2.

🔑 **The surviving faults split two ways** — see [[flicker-discriminates-bend-from-break]]:
- 🔧 **torsion / bending, recoverable:** A1, C1, C2
- ❌ **continuous break, handling will NOT fix:** B1, B2, D1
- ✅ **solid:** A2 (EEG only — its EMG is a fixed 352-354 µV artefact), D2 (both roles)

🔴 **Go/no-go = AMBER, recorded in advance: n = 2 guaranteed, up to n = 5.** A **10 minute**
re-screen gates the start; every chip floor must read ≥ 2000 µV.

🔴 `FLOOR_MIN_HUM_UV = 800` let D2 through at 1052 µV while physically ungrounded — **fourth
recording where 800 is too low.** Proposed 2000, still not applied.

⚠️ D1's own wire-free floor is CONTAMINATED (lf/hf p99 4.6 here, 18-29 in longer files, other chips
2-7). Judge D1 on rms and slope, never its ratio.

⚠️ **`allego_0__uid0829-08-34-39` — 59.201 h, 223 GB, 08-29 08:34 → 08-31 19:46 — is NOT ours.**
Andrea says there was no 59 h run, so it is not in any manifest and no number from it is used. It is
not an empty rig though: 7 of 8 positions carry EEG above their own floors with zero railing across
all 59 h. Most likely Allego left recording unattended. Identify or delete before Thursday, 223 GB
of 1019 GB free.

Log: vault `05-experiments/active/2026-09-02-S-SD-recovery-sleep.md` and `04-journal/2026-09/2026-09-01.md`.

## From the memory index, trimmed there 2026-09-11 (kept here verbatim)

- ⏳🔴⭐⭐⭐ **[S-SD RECOVERY SLEEP — Wed 2026-09-02 13:00 → Thu 09-03 09:00, TERMINAL ENDPOINT](s-sd-recovery-sleep-run-2026-09-02.md). NEWEST, READ FIRST.** 20.0 h, **CSD FINISHED across the window**, animals SAMPLED Thu 13:00 ⇒ **UNREPEATABLE**; scored Thursday. ✅ **Pre-flight screen GATED for the first time and a bench re-seat fixed ALL EIGHT chip grounds** (B2 117→2486, D2 1052→4541 µV). 🎉 **D2 back on BOTH roles — a GROUND fault, not an electrode.** 🔑 Faults split: 🔧 torsion A1/C1/C2 · ❌ break B1/B2/D1 · ✅ A2 (EEG only), D2. 🔴 Go/no-go **AMBER, n=2 guaranteed up to n=5**; 10 min re-screen gates the start. ⚠️ `allego_0__uid0829-08-34-39` (59.2 h, 223 GB) is **NOT ours** — Andrea says no such run.
