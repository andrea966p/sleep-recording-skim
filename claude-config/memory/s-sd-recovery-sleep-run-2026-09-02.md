---
name: s-sd-recovery-sleep-run-2026-09-02
description: "The S-SD terminal endpoint 2026-09-02 (unrepeatable). OUTCOME 2026-09-26: n = 0 scoreable at every S-SD timepoint; D2/HLBSSD18 passes rung 2 but has a EMG with NO MUSCLE-BAND modulation (not proven dead)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 96a1ed89-9db0-4f3f-bf96-57a4fbc53432
  modified: 2026-09-14T07:49:25.467Z
---

🔴🔴 **OUTCOME, 2026-09-26 (stage 3 run for the first time): S-SD recovery sleep is n = 0.**
No animal reaches ladder rung 3 at ANY S-SD timepoint (08-25, 08-26, 09-02); the endpoint has
none even in stage 3. 🔑 **D2/HLBSSD18 passes rung 2 everywhere but its EMG has NO
MUSCLE-BAND modulation**: after the 10–300 Hz band-pass p95/p5 1.41–1.75 (working 4–6), p5 ~30 µV
(working 7–9), no light/dark change. Stage 3 rejects it for wake 0.2–1.6%. 🔴 NOT proven dead:
the RAW broadband rms rises 33→75 µV at night and raw p95/p5 does not separate from working EMGs;
`D/34` has an EEG-like slope, so that rise is low-frequency of unknown origin. Rung 2 judges EMG
on hum+rms only and cannot see any of this.


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

🎉 **D2 (HLBSSD18) came back on BOTH roles and it was a GROUND fault**: EEG rms 114-153 µV, lf/hf
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

## The recording file, found 2026-09-14

Never catalogued — page sat in `active/` at `status: planned` for 12 days after sampling. Confirmed
on `e10ubuntu` at `/home/skimlab/radix/data/allego_2__uid0902-13-00-28_data.xdat`, **75.7 GB**
(75,749,372,928 B), start `13-00-28` and mtime 09-03 09:05 matching the planned 20.0 h window.
Companions `_timestamp.xdat` (578 MB) and `.xdat.json` (metadata). **Not yet scored, not moved to
NAS** — this is unscored raw data, not a completed analysis.

Log: vault `05-experiments/completed/2026-09-02-S-SD-recovery-sleep.md` (moved from `active/`
2026-09-14) and `04-journal/2026-09/2026-09-01.md`.

## From the memory index, trimmed there 2026-09-11 (kept here verbatim)

- ⏳🔴⭐⭐⭐ **[S-SD RECOVERY SLEEP — Wed 2026-09-02 13:00 → Thu 09-03 09:00, TERMINAL ENDPOINT](s-sd-recovery-sleep-run-2026-09-02.md). NEWEST, READ FIRST.** 20.0 h, **CSD FINISHED across the window**, animals SAMPLED Thu 13:00 ⇒ **UNREPEATABLE**; scored Thursday. ✅ **Pre-flight screen GATED for the first time and a bench re-seat fixed ALL EIGHT chip grounds** (B2 117→2486, D2 1052→4541 µV). 🎉 **D2 back on BOTH roles — a GROUND fault, not an electrode.** 🔑 Faults split: 🔧 torsion A1/C1/C2 · ❌ break B1/B2/D1 · ✅ A2 (EEG only), D2. 🔴 Go/no-go **AMBER, n=2 guaranteed up to n=5**; 10 min re-screen gates the start. ⚠️ `allego_0__uid0829-08-34-39` (59.2 h, 223 GB) is **NOT ours** — Andrea says no such run.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴🔴⭐⭐⭐ **[S-SD RECOVERY SLEEP — 2026-09-02](s-sd-recovery-sleep-run-2026-09-02.md).** Animals SAMPLED ⇒ UNREPEATABLE. ❌ **OUTCOME 2026-09-26: n = 0 scoreable at every S-SD timepoint.** D2/HLBSSD18 passes rung 2 but its EMG has NO MUSCLE-BAND modulation (p95/p5 1.41–1.75 after 10–300 Hz band-pass). ⚠️ NOT proven dead: raw broadband rms rises at night. Rung 2 cannot see it; rung 3 can.
