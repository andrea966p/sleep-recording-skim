---
name: electrode-failure-literature
description: "Six primary papers on mouse EEG electrode impedance and failure rates, and how they change our interpretation of the rig"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T02:56:39.040Z
---

Papers in `~/Desktop/andrea/papers/`. Full evaluation: vault
`06-references/electrode-failure-and-impedance-literature.md`.

🔴⭐ **THE KEY NUMBER — Hsieh et al., *eNeuro* 11(2), 2024, N=11/group:
"82% of the epidural 0.1 mm preparations lost at least one electrode within
3 weeks of surgery, only 18% of the MXene implants."** Per-channel dislodgement
probability **0.38 / 0.31 in WEEK 1**. **Progressive irreversible epidural
electrode loss is the DOCUMENTED BASELINE, not an anomaly and not a surgical
skill problem.** Their fix is a **different electrode** (1.0 mm epidural is more
stable than 0.1 mm; MXene 82%→18%), not better surgery.

🔴 **THIS WEAKENS OUR TIER-1 ARGUMENT.** We said: EMG works + EEG open through
the same tether/slip-ring/board/port ⇒ shared path good ⇒ fault is the C3410
pad 0/1 solder. **First half holds, second half does NOT follow** — EEG and EMG
do not share an electrode: **EEG = dura pin (82% 3-week failure), EMG = stripped
wire anchored in muscle (no comparable published failure rate).** Two live
hypotheses, not one. **Still do the free bench test — but as a DISCRIMINATOR,
not a confirmation.**

⚠️ **OUR IMPEDANCES ARE POOR BY PUBLISHED STANDARDS.** Literature @1 kHz:
epidural/MXene in use **10-29 kΩ** (Hsieh 2024); stainless screw 0.8 mm
**10-50 kΩ**, HD contact chronic **~100 kΩ** (Kim 2022, *Sci Data*); skull screw
**<100 kΩ** @30 Hz, nanofab **2-3.5 kΩ** (Choi 2010, *J Neurophysiol*).
**Ours: best in fleet 73 kΩ; C1 (our best animal) 465 kΩ.** Our single best
channel sits at the literature's WORST acceptable value.

⚠️ **DO NOT CITE KAPPENMAN & LUCK 2010 for our hum-vs-contact result.** They
found **NO detectable effect of impedance on 60 Hz line noise** — but compared
**5 kΩ vs 50 kΩ** in a well-shielded room and say explicitly they could not test
it. We compare connected vs **OPEN CIRCUIT** (~10² vs ~10⁴ kΩ) — different
regime; an open input is not a high-impedance input. Our bimodal 9-90 /
1000-4700 µV separation is **our own empirical finding**. Kappenman DOES support:
high Z is workable with modern amps (C1 gave good data at 465 kΩ), and
**warm/humid conditions make high-Z recordings much worse** (we log neither).

🛑 **FRONTAL-SINUS HYPOTHESIS DROPPED ENTIRELY** — built on the wrong channel
map; there is no frontal-vs-parietal asymmetry, only EEG `/1` vs EMG `/2`.

**Protocol deltas:** Oishi 2016 *JoVE* = **habituate 2-3 days**, EEG 0.5-64 Hz,
**EMG 16-64 Hz** (ours 10-300 — worth testing narrower offline), 128 Hz, 10 s
epochs. Kim 2022 uses a **60 Hz HARDWARE notch at acquisition** — we deliberately
do not, since hum is our contact diagnostic; keep acquisition raw. Needle 2026:
needle ≈ screw quality, 5 s epochs. Choi 2010: "mouse EEG dynamic range within
100 µV" (matches C1's 52-70 µV rms).

✅ **TIMELINE (answered 2026-08-03): surgery 21-23 Jul, tethered Thu 30 Jul.
Run 1 = 31 Jul = day 8-10 post-op, ~28 h tethered. Run 2 = 2 Aug = day 10-12.
BOTH WERE RIG COMMISSIONING TESTS.** Our own SOP (`tsukuba-sleep-recording-method`)
wants **≥14 d implant→recording + ≥7 d cage acclimatisation**; Oishi wants 2-3 d
habituation. **Both runs miss all three (2-6 d early, ~1 d habituation).**
🛑 **STOP QUOTING "~6% yield"** — it describes an under-habituated cohort recorded
early during commissioning, NOT the rig. ⭐ **C1 is MORE impressive for it: 66.9%
light-phase sleep on its SECOND DAY tethered.** 06-29 fully explained.
⭐ **CHEAPEST DECISIVE EXPERIMENT: re-run the SAME animals at ≥14 d post-op /
≥7 d tethered.** We have NEVER recorded a cohort under our own protocol.

🔴🔴 **WE HAVE ONLY EVER MEASURED HALF OF EACH ELECTRODE PAIR.** RHD2216 is
bipolar — each amp has TWO electrode pins (`inX+`, `inX-`), both real electrodes.
**The chip CAN test either: datasheet Register 5 bit `Zcheck pol sel`** (0 = inX+,
1 = inX-); the differential subtraction is irrelevant because the test injects
current into ONE input pin and reads back through that same amp. **RADIENS DOES NOT EXPOSE IT** — verified at SOURCE level across 4 sources
(installed `radiens`, Radiens Tech Doc PDF, online `radiens-core` API ref, and the
**`radiens-core` 0.0.8 wheel source**): `get_intan_impedance(port)` is the ONLY
impedance method on the whole `AllegoClient`; `ImpedanceRequest` has only `port`;
`ImpedanceValue` has only `ntv_chan_idx, magnitude_ohm, phase_deg`. 🔑 **And there
is NO Intan register-write path at all** — `load_all_mosi`/`transmit_mosi`/
`read_wire_out`/`flash_sinaps` are **Sinaps-probe specific**, cannot reach the RHD
chip. **No back door exists.** Docs: https://neuronexus.github.io/radiens-core-python/dev/ Chip default `pol sel=0` ⇒ **all our
numbers are the POSITIVE input; the NEGATIVE electrode of every pair has NEVER
been measured.** ⭐ **EXPLAINS B1** (0.133 MΩ best-in-fleet yet fully open 21.7 h
— `inX-` could have been open all along). **Explains class-not-yield**: our
`differential_60Hz ≈ common_mode × Z_imbalance` needs BOTH inputs; we never had
them. **FIX: DMM each C3410 pad vs animal GND pad** (free, per-electrode, sees
the negative side) → ask Kontex to expose `Zcheck pol sel` → check Open Ephys GUI.

⭐ **WHICH ELECTRODE EACH NUMBER IS (pad map + pol_sel=0):** pads pair into amps —
**pad0 `in0+` = EEG frontal-L / pad1 `in0−` = EEG parietal-L → amp0 = `/1`**;
**pad2 `in1+` = EMG-L / pad3 `in1−` = EMG-R → amp1 = `/2`**. So `/1`,`/2`
(+`/33`,`/34`) selection is **CONFIRMED CORRECT** — the whole montage is 2
channels. **Every "EEG impedance" we ever quoted is the FRONTAL electrode only;
parietal never measured. "EMG impedance" = EMG-L only.** ⭐ **This likely
reconciles the old "frontal open / parietal fine" claim — those were probably
`/1` vs `/2` (EEG amp + vs EMG amp +) mislabelled**, i.e. our current
EEG-open/EMG-works finding. Removes the last support for frontal-sinus.
🔴 Fixed a wrong instruction in `grounding-reference-noise-concepts` §2 which
still said "recorded pads = 0,1,2,3,4,6, select pads explicitly" + "differential
pairs **in software**" — pre-08-01 leftovers in the page labelled *definitive*.
⚠️ `/3`,`/4` = **half-wired on the single-mouse 8-pin rig** (pad4 real dura
frontal-R vs open; pad6 copper vs open) but **genuinely empty on the 8-mouse
rig** (4 electrodes + ground only). Datasheet: RHD2216 = 16 amps, `in0+/in0−…`;
"32 amplifiers … only channels 0-15 active" ⇒ why Allego shows 32 slots/port.
See [[eeg-analysis-pipeline]], [[light-schedule-and-circadian-validation]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⚠️ [82% of epidural electrodes fail in 3 weeks](electrode-failure-literature.md) — real literature, ❌ NOT our failure mode.
