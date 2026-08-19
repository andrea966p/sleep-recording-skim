---
name: recording-2026-08-18-eight-new-mice
description: "First 6.4 min screen of the 8 newly operated W-SD batch mice: 5 give clean EEG, 1 electrode open, 2 headstages floating, and the pooled floor in criteria.py gives the wrong answer"
metadata:
  type: project
---

⭐⭐ **`allego_0__uid0818-18-56-33`, 2026-08-18 18:56:33 KST, 6.43 min (386,048 samples), rung 0 INTACT.** **8 NEW mice, BATCH `W-SD`**, freshly operated, unrelated to every earlier cohort. ⭐ **Refer to them as `W-SD` + rig position: W-SD A1, W-SD A2, W-SD B1 ...** (user, 2026-08-18) — see [[cohort-identity-every-run-is-new-mice]]. Vault: `05-experiments/active/2026-08-18-W-SD-cohort-first-screen.md` + journal `2026-08-18`. **Still NO cohort manifest** — no animal ids, surgery dates, sex or tether arms yet.

**Layout read off the file: 2 roles, EEG `/1` `/33`, EMG `/2` `/34`. NO ECG this time** — `/3` and `/35` are bare floor on every grounded chip. Floor = `/3`-`/16`, `/35`-`/48`.

🔴🔴 **THE POOLED FLOOR IN `core/criteria.py` GIVES A WRONG ANSWER ON THIS FILE.** `floor_stats()` pools all 112 wire-free sites, but two headstages are floating and their unwired inputs are ~50x quieter AND steep, so pooled `slope_p1` = **−2.002**, steeper than every animal channel. Everything then scores 0.0-13.2% usable. ⭐ **Use a PER-CHIP floor** (the 14 wire-free sites of that same port+slot): per-chip falsification passes on all 8 chips, mean 0.00-0.38% against 1% expected by construction. **`criteria.py` needs a per-chip floor option; pooled is unsafe the moment any one headstage floats.**

**Per-chip verdict (100% of 38 epochs, zero railed anywhere):**
| pos | EEG slope | margin vs own chip floor | EEG | EMG rms/hum µV |
|---|---|---|---|---|
| A1 | −1.50 | −1.27 | 100% | 78.7 / 15.2 ✅ |
| A2 | −1.51 | −1.24 | 100% | 53.8 / 7.9 ✅ |
| B2 | −1.73 | −1.20 | 100% | 475.5 / 639.9 ❌ open |
| C1 | −1.69 | −1.53 | 100% | 21.9 / 27.5 ✅ |
| D2 | −1.72 | −1.16 | 100% | 13.9 / 11.5 ✅ |
| C2 | **−0.16** | +0.22 | **0%** | 61.9 / 78.4 |
| B1 | −1.85 | **+0.06** | unjudgeable | 29.0 / 28.8 |
| D1 | −1.82 | **+0.13** | unjudgeable | 1232 / 1644 |

⭐ **5 clean EEG (A1 A2 B2 C1 D2), delta share 0.34-0.38, lf/hf 13-27, band-limit guard `raw` on all.** 4 of them also have plausible EMG; **B2 is EEG only**. **C2 = single open electrode** on a properly grounded chip: quiet 122 µV AND flat −0.16, hum criterion says 86.8% usable so the hum-vs-slope guard fires CONTRADICT.

🔴 **B slot 1 and D slot 1 HEADSTAGES ARE FLOATING, AND IT IS NEW TODAY.** Floor 60 Hz per chip:
```
uid0818 A1=5192 A2=3952 B1= 162 B2=4132 C1=4596 C2=3088 D1=  82 D2=5006
uid0816 A1=5609 A2= 119 B1=4613 B2=3368 C1=3264 C2=5097 D1=3614 D2=1138
uid0814 A1=3785 A2= 114 B1=5592 B2=4555 C1=2846 C2=5153 D1=4443 D2=1278
uid0809 A1=1611 A2=4753 B1=3286 B2=3601 C1=1640 C2=4686 D1=4871 D2=4763
```
**A2 was the floating chip on 08-14 and 08-16; today A2 is fine and B1+D1 broke.** The fault follows whatever was re-plugged ⇒ same root cause as [[ecg-cohort-ground-miswired]], fixed by a **connector re-mate, no anaesthesia**. ⭐ **Verify the fix on the floor 60 Hz of that chip (want >~1000 µV), NOT on impedance.**

🛑 **NOT A PASS. 6.43 min is the whole file, so the longest unbroken usable block is 6.3 min against the rung-2 bar of 15 min ⇒ verdict INSUFFICIENT, not PASS.** Contact flips within minutes on this rig ([[movement-dependent-contact-root-cause]]). Re-record ≥1 h after the ground fix; prefer a ZT0 start if it runs over a day.


## ⭐⭐ THE 1 h RUN AFTER THE ELECTRODE RE-SEAT (same evening)

**`allego_1__uid0818-20-50-26`, 20:50:26-21:50:39 KST, 1.004 h, 3.79 GB, INTACT** (3,612,928 = 3,612,928, remainders 0). Stopped deliberately at 1 h.

✅ **Re-seat FIXED D slot 1** (82 -> 4456 µV). 🔴 **B slot 1 still PARTIAL at 453 µV** and **NOT intermittent** — 481/473/476/473/451/449 µV across six 10-min chunks vs 5009-4919 on A1 ⇒ **ground PIN POSITION wrong, not a loose plug.**

✅⚠️ **RETRACTION: W-SD C2 was NOT an animal-side open electrode.** Slope −0.16 → **−1.07** after the re-seat. **NEVER call a channel animal-side before a re-seat + re-record.** Still only intermittent (39.3%, 8.7 min block, 0.9% railing, rms 297 µV).

**EEG alone, per-chip floor, 361 epochs, rung-2 bar 15 min:** ⭐ **A1 100% / 60.2 min unbroken, C1 100% / 60.2 min, D2 99.4% / 52.8 min, A2 99.4% / 34.3 min, B2 97.8% / 15.8 min = FIVE PASS**, zero railed epochs. C2 39.3%/8.7, D1 29.4%/2.0, B1 0.3%/0.2 fail.

🔑 **THE STRICT LADDER GATE IS THE AND OF EEG *AND* EMG IN THE SAME EPOCH** (`cards/ladder.py:rung2_connection`), then the 15-min bar on that combined block. **ONLY W-SD A2 PASSES (92.2%, 24.2 min).** 🟡 **D2 94.7%/13.5, A1 92.8%/13.5, C1 83.4%/14.0 — miss by ~1 min because of short EMG dropouts, NOT the same as failing.** ❌ B2 0.0 (EMG open, 443 µV), B1 0.0, D1 0.0. 📌 **Always say WHICH number you quote, EEG-only or combined.**

**Tonight's standing: good = A1, A2, C1, D2. EEG-only = B2. Intermittent = C2. Not usable = B1 (chip ground), D1 (chip now grounded and STILL fails ⇒ first possible genuine animal-side fault in this cohort).**

Scratch scripts used (per-chip floor, blind 256-channel scan) were written outside the repo and are not committed. Engine: [[animal-card-verdict-ladder]]. 📌 **Andrea checks the B1+D1 connector seating on the morning of 2026-08-19.**


---

🔴🔴 **2026-08-19 17:16: W-SD B1 CHEWED AND CUT ITS TETHER. THE ANIMAL IN B1 IS NOW A DIFFERENT
MOUSE** (a pre-tethered one from the habituation rack). ⛔ **EVERY B1 VERDICT ABOVE BELONGS TO THE
OLD ANIMAL — DO NOT CARRY IT.** B1's failure was animal-side ground wiring, so a fresh animal there
is a real test: **if the new B1 is ALSO dead, the fault is the RIG POSITION, not the mouse** — that
would be a new finding. ⚠️ The chewed tether is damaged hardware, repair not yet logged.
Runs: `allego_0__uid0819-09-00-00` (09:00-17:16, 8.27 h, 31.2 GB, 8 mice, old B1) then
`allego_1__uid0819-17-25-20` (17:25 Wed → 09:00 Fri, ~39.6 h, new B1).
