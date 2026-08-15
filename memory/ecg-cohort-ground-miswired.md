---
name: ecg-cohort-ground-miswired
description: "2026-08-07 — the 7 new ECG mice were wired with the cerebellum ground on the wrong pin, leaving every animal floating; this explains the whole night and is fixable with a connector re-mate, no surgery"
metadata: 
  node_type: memory
  type: project
  originSessionId: a13e9044-6cc6-4f21-b8d5-7413872da116
  modified: 2026-08-07T13:02:29.001Z
---

**Section:** vault `05-experiments/active/2026-08-07-ecg-cohort-baseline.md`, final part.
Supersedes the short-in-the-tether reading in [[ecg-cohort-2026-08-07]].

🔴⭐⭐⭐ **ROOT CAUSE (andrea's, 2026-08-07 22:00): THE CEREBELLUM GROUND WENT TO THE WRONG PIN.**
It should mate to the **brown** wire → brown slip-ring line → **GND pad of the headstage adapter**.
Instead the dura pin was mated to the **orange** wire, floating at the far end, and the brown wire
in the GND pad **touches nothing on the mouse**. ⇒ **ALL SEVEN NEW MICE RECORDED WITH NO GROUND.**
Control (old B1, old tether) untouched, which is why it alone works.

⭐⭐ **IT EXPLAINS THE HUM COLLAPSE, WHICH NOTHING ELSE DID.** No ground ⇒ mains drives the WHOLE
ANIMAL as common mode ⇒ **a bipolar channel REJECTS common mode** ⇒ differential hum goes DOWN.
⚠️ **"Lose the ground, get huge hum" is true for SINGLE-ENDED referential recording, NOT for a
differential pair.** Low hum and absent signal have the SAME cause.

⭐⭐ **IT EXPLAINS THE PERFECT IMPEDANCE.** With GND floating the injected current returns through
**the other electrode of the pair** ⇒ measures electrode→tissue→electrode: real, stable, resistive,
100-360 kΩ. 🔑 **THE STABILITY IS THE TELL — every failure this rig ever had was intermittent;
7 channels at 100% duty with ZERO FLIPS is not how electrodes fail, it is how wiring errors
behave.** Also 7/7 identical, no ECG heartbeat anywhere, control unaffected on the same port.
⭐ **The 3 channels of each new mouse carry the SAME waveform** (mean broadband |r| 0.38, D1 =
0.79) vs control 0.13 — skull EEG and thoracic ECG share nothing unless all ride one floating
potential. ⚠️ partly confounded: a channel WITH signal is automatically less correlated.

⚠️ **DOESN'T FIT:** a missing bias return should push the amp out of linear range yet **railing
was 0.0%**. Not demonstrated.
🔴 **A PREDICTION FAILED TONIGHT — I said impedance phase would be ~-90° if the path were tether
capacitance; it came back ~2°/178°, PURELY RESISTIVE.** Capacitive-coupling idea dead.
🔑⭐ **THE PHASE COLUMN IN EVERY SWEEP CSV IS USEFUL AND WAS IGNORED FOR MONTHS.** Resistive ≈ 0°/180°,
electrode interface ≈ -20° to -60°, pure capacitance ≈ -90°.

🔴 **WITHDRAWN, both mine:** "bipolar pairs shorted in the unsoldered 8co tether" (andrea's
multimeter showed no conductor beeps against any other) and "conductive bridge / fluid under the
cement" — **and with them the suggestion to spend an isoflurane episode moving a mouse to an old
tether. DO NOT schedule that.** ⚠️ Still true and worth keeping: **a continuity beeper fires below
~30-50 Ω, so a tens-of-kΩ leak is SILENT on a DMM.**
✅ **FIX NEEDS NO ANAESTHESIA — it is a CONNECTOR RE-MATE, not the implanted electrode**, so the
standing "never reseat an electrode" rule does NOT apply here.

🗂️ **PRE-FIX BASELINE, KEEP: `allego_0__uid0807-19-14-58`**, 19:14:58→22:01, **2.768 h**, 10.44 GB,
`~/radix/data/`. Verified intact on stop (data and timestamp agree to the sample, 9,964,672 each,
0 remainder, no error). **Before-state for all 7 animals PLUS 2.8 h of the working control under
the identical floor.** andrea stopped the run and re-pins all seven on 2026-08-08.

📌 **TOMORROW:** re-pin all 7 → ⭐ **watch the live stream BEFORE committing to a night** (EEG
should appear in seconds) → fresh impedance block → overnight recording → score vs floor
`/4`-`/16`,`/36`-`/48` with **the heartbeat as the primary yes/no**.
⭐⭐ **PREDICTION TO CHECK: with the ground correct the impedances should get WORSE or change
character**, because the return path moves from the paired electrode to the ground electrode.
**If they stay identical at 100% duty with zero flips, the ground is STILL not connected.**

See also [[ecg-cohort-2026-08-07]], [[overnight-two-animals-tether-is-the-fix]].
