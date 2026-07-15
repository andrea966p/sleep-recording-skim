---
tags: [decision, council, audit, review, eeg, grounding, sleep-scoring]
date: 2026-07-15
created: 2026-07-15
type: technical-review
status: open (diagnosis converged; bench tests + record corrections pending)
sourced-from: 04-journal/2026-07/2026-07-15.md
---

# LLM Council — Earth/Grounding Root Cause + Sleep-Recording Usability (2026-07-15)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A zero-bias, high-rigor review of two questions by 5 independent LLM advisors (electrical-first-principles, contrarian/null-hypothesis, signal-metrologist, bench-experimentalist, sleep-EEG-scoring), each reasoning alone on the same raw evidence, three of them re-analysing the raw `.xdat` files themselves. A chairman synthesised. See [[01-infrastructure/system-overview]] for the big picture.
>
> **Why it exists.** After an electrician bonded a wall-earth to the XDAQ on 2026-07-14 and one 42-second clip looked clean, the vault recorded "earthing fix VALIDATED." On 2026-07-15 the hum was back and squeezing the ground clip did nothing. This review was called to decide, without bias, what is actually wrong and whether ANY sleep data is scoreable.
>
> **How to read this page.** [[#Chairman verdict]] is the answer. [[#The decisive bench tests]] is what to physically do next. [[#Go / No-Go gate]] is the checklist before any real recording. [[#What the council forces us to retract]] lists the overstated claims we must correct. Advisor positions are kept verbatim-in-summary for provenance.

> [!quote] Paper-ready
> "The 60 Hz contamination of the EEG was characterised by single-ended per-electrode spectral decomposition. A single mains source drove all channels (phase-locking value = 1.00 across connected and open inputs), but the bipolar montage failed to reject it because electrode-impedance imbalance converted the common-mode field to a differential signal (bipolar/common-mode 60 Hz ratio ≈ 2). Usability was therefore governed multiplicatively by both an incompletely-earthed acquisition system (setting the common-mode floor) and per-electrode contact balance (setting the day-to-day and channel-to-channel variance); of the two, electrode contact was the binding, controllable variable."

---

## Mandate

User request, verbatim intent: *"summon the council to evaluate the earth issue and analyze the sleep recordings. Needs to be done absolutely precisely… no bias, absolute scientific rigor."* Two questions:

- **Q1 — Grounding.** Actual root cause of the 2026-07-15 60 Hz hum; decisive fix. Squeezing the GND-to-earth clip between two runs changed nothing. Hypotheses left OPEN: H1 global earth lost, H2 per-electrode contact, H3 both, H4 other (display/RustDesk/analysis artifact).
- **Q2 — Usability.** Is any recording scoreable for sleep staging? Recoverable by filtering, or unusable? Go/no-go for a real overnight run.

## Method

5 advisors dispatched in parallel, no cross-talk, each handed the same neutral evidence packet (raw QC across all runs 2026-07-10 → 07-15, hardware facts, competing hypotheses framed as open) plus the vault. Advisors were explicitly told to re-derive, not trust prior vault conclusions, and to challenge the packet itself. Three (electrical, contrarian, metrologist) wrote their own analysis scripts and recomputed the numbers from the raw `.xdat` files rather than trusting the packet's summary metrics. Chairman (main thread) synthesised. This mirrors the [[2026-05-01-llm-council-review]] methodology.

---

## Chairman verdict

**Q1 — root cause is H3 (both), and the two "camps" were measuring two factors of one multiplicative product, not contradicting each other.**

The physics that unifies every advisor's numbers:

```
differential_60Hz_at_amplifier  ≈  common_mode_mains_voltage  ×  electrode_impedance_imbalance
                                     ^^^^ H1 term (the floor) ^^^^   ^^^^ H2 term (the variance) ^^^^
```

- **The common-mode field is real and present in every run (H1 floor).** Independently measured, not inferred: phase-locking value = 1.00 across all 8 slots including never-connected ones (metrologist) → one mains source. Connected electrode A1 sat at ~3 mV *single-ended* 60 Hz, common-mode ≈ 2951 µV (electrical) — a solidly-earthed dural electrode physically cannot do that; the input island is swinging in the mains field. Squeezing the clip left the untouched floating-slot common-mode unchanged (1841→1834 µV), i.e. **the earth as currently wired does not control the system common-mode today.** The system is effectively floating again on 07-15.
- **But the montage does NOT reject it, because the hum is DIFFERENTIAL at the amplifier (H2 the binding variable).** bipolar/common-mode 60 Hz ratio ≈ 1.6–2.0 on essentially every slot (metrologist); diff/cm up to 6.1 with grossly asymmetric legs on A2 (electrical). A perfect common-mode signal would cancel in F−P (ratio→0); ratio≈2 means the two legs see 60 Hz at unequal amplitude/phase → subtraction *adds* it. That asymmetry is electrode-impedance mismatch / one open leg.
- **Within-run variance proves electrode contact is the actionable lever.** Same run, same instant, same earth: 07-14 A2 legs 16/5 µV (balanced, clean, real EEG) while A1 was 220/460 µV (dirty). Identical earth, opposite outcome → the variable that flips a channel clean↔dirty is the electrode, not the global earth. Confirmed by drift: 07-15 A2 60 Hz climbed 5000→7800 µV over 12 min untouched (contact drying/movement) while an open slot sat flat.

**Where the advisors genuinely disagreed** (this is the honest part, not smoothed over): the *relative weight* of earth vs contact. Bench leaned global-earth-primary (~55%). Contrarian leaned contact-primary (~55%) and raised a hypothesis nobody else did — that the electrician's new permanent wall-earth→Chassis-GND bond created a **ground loop** raising 60 Hz *above* the pre-fix floating baseline (07-15 bipolar 2.3–7.8 mV vs 72 h floating 0.5–1.9 mV; a *lost* earth returns you to ~2 mV, not 3–4× past it). Electrical and metrologist put it at H3-both with contact as the variance and earth as the floor. **Chairman resolution:** all four measured the same product; the disagreement dissolves once you stop asking "earth OR contact" and read it as "earth sets the floor, contact sets whether you clear it." The ground-loop hypothesis is a live minority (~20%) that a single earth-lift test settles for free (below). H4 is rejected ~90% by three advisors: the hum is present from the START of the 09:35 run, before RustDesk connected at 09:53; PLV=1 is a mains signature, not a USB/HDMI digital artifact; files are byte-perfect.

**Q2 — zero scoreable sleep data exists, and the current state is NO-GO for a real run. Unanimous (5/5).**

- The only physiological trace in the entire dataset is A2 of `uid0714-16-58-16`: post-notch 126–137 µV, **delta 60% / theta 10%** — genuine delta-dominant cortical EEG. But it is **~42 seconds** long → cannot stage sleep (needs continuous Wake/NREM/REM cycling over minutes-hours). Real signal, not a dataset.
- **The rest is not "hum over buried biology" — the biology is absent.** Killer test (metrologist): 07-15 connected mouse A2 (residual 183 µV, beta 40%, delta 16%) is spectrally indistinguishable from the OPEN, wire-to-nowhere floating slot C1 (181 µV, beta 39%, delta 11%). A connected animal and an unconnected input produce the same residual. Post-hoc filtering cannot recover what isn't there.
- **These recordings are differential (bip/cm≈2), same regime as the failed 72 h/20 h runs → notch+bipolar CANNOT rescue them.** Add irreversible rail-clipping (legs clip ±6390 µV 4–8% of the time on 07-15) — clipped samples are gone.

---

## The decisive bench tests

Run in this order. Each is cheap, non-invasive, and does NOT touch the acquisition server. NEVER call `GetIntanImpedance` while streaming. Command style: bare, one step at a time, expected reading stated.

**TEST 1 — GUI-paused per-electrode impedance (the H2 discriminator that was NEVER done before the 07-15 runs).**
In Allego, pause acquisition, run the built-in impedance measurement. Read BOTH legs (EEG_F and EEG_P) of A1 and A2 individually.
- Good contact = 0.1–1 MΩ; open = ≫5 MΩ; legs of a pair should be within ~2–3× of each other.
- Prediction (H2): at least one leg on the dirty pairs reads >5 MΩ or the pair is imbalanced >3×.
- Falsifier: if BOTH legs read <1 MΩ and balanced, yet bipolar 60 Hz is still >500 µV → H2 is wrong and it's earth-dominant (H1). Go to TEST 2/3.

**TEST 2 — verify a REAL earth, then the single-ended collapse test (the H1 discriminator, done right).**
The prior "squeeze the clip" test was uninformative because it re-seated an unverified (possibly fake) earth and watched the *bipolar* (which is dominated by mismatch). Do it properly:
1. DMM continuity, wall-socket round earth pin ↔ known building earth (a second earthed socket / grounded conduit): expect ~0 Ω. The Korean multitap side-clip is flagged in `02-procedures/earthing-60hz-hum-fix.md` as possibly fake — verify, don't assume.
2. With the animal connected and hum live in Allego, clip XDAQ **Chassis GND port → that verified earth** and watch the **raw SINGLE-ENDED 60 Hz on a connected leg** (A1's legs, ~2.3–3.8 mV now), NOT the bipolar.
   - Collapses ~10× (→ <300 µV) ⇒ system was floating, earth is the fresh break (H1 confirmed).
   - Barely moves ⇒ earth already effective, chase electrodes (H2).

**TEST 3 — the cleanest single physics discriminator (metrologist).** Short EEG_F and EEG_P to the headstage GND pad and record a short clip.
- Shorted input STILL shows mV-scale 60 Hz ⇒ pickup is upstream common-mode (H1, earth).
- Shorted input goes quiet ⇒ hum enters through electrode impedance (H2, contact).

**TEST 4 — settle the ground-loop minority hypothesis (contrarian).** Temporarily lift the electrician's wall-earth→Chassis-GND bond, re-measure a floating slot's 60 Hz.
- DROPS ⇒ the bond formed a ground loop; the "fix" was backfiring. Re-wire to a single earth point.
- RISES ⇒ earth was helping; keep it, make it permanent.

**Make the earth permanent regardless:** ring terminals (not hand-clips) under the Chassis-GND screw and the verified-earth screw; single-point Chassis↔Sys GND bond; star-ground cage/rack/commutator to that one node; strain-relieve so handling/KVM-switch/reboot can't lift it. Per `02-procedures/earthing-60hz-hum-fix.md`.

---

## Go / No-Go gate

Before committing animals to ANY overnight/multi-day run, EVERY line must pass on EACH connected pair, live, and hold ≥10 min untouched:

- [ ] GUI impedance both legs **0.1–1 MΩ**, legs within **~2–3×**.
- [ ] Single-ended raw 60 Hz **< 50 µV both legs**; **rail% ≈ 0** (no clipping).
- [ ] bipolar/common-mode 60 Hz ratio **< ~0.3** (proves it's actually common-mode and rejected).
- [ ] Post-notch bipolar residual **< 150 µV RMS**.
- [ ] Residual spectrum **delta-dominant (θ/δ < 1)** — guards against a quiet floating input scoring high on phys%.
- [ ] **Stable ≥10 min, animal untouched, no clean→bad swing** — this is the exact line the 07-14 "USABLE" clips FAILED (A2 swung 11%→80% in minutes). A channel that can't hold 10 min will not hold 12 h.
- [ ] EMG bipolar shows **movement-modulated tone** on a nudge test — REQUIRED before any REM call (see below).
- [ ] Allego mode/rate/channel-select re-set after any re-enumeration (`XDAQ_ONE_REC`, ≥1000 S/s, correct sites — it forgets on every re-enum).
- [ ] If video correlation matters: confirm Frigate recording is actually ON (it was silently OFF for the 72 h run).

Current best channel (07-15) fails the first five by an order of magnitude. **NO-GO.** Two prior multi-day runs (72 h, 20 h) burned live animals for 0/4 and 0/8 scoreable EEG — that is the cost of skipping this gate.

## Data verdict — salvage vs discard

- **72 h, 20 h, both 07-15 runs, all 07-14 A1, and 07-14 A2 at 17:04/17:09/19:06:** 0 scoreable → **discard as sleep data.** Keep as endurance proof (byte-perfect 72 h) and engineering/QC record only.
- **07-14 A2 at 16:58 & 17:16 (the two "USABLE" clips):** genuinely scoreable-QUALITY EEG, but 42–54 s long and intermittent → **methods proof that the rig CAN reach scoreable EEG, not a dataset.** Discard as sleep data.
- **Net yield to date: zero scoreable sleep recordings.** High confidence, 5/5.

## Publication-integrity constraints (sleep advisor)

- **EMG/REM hazard:** 60 Hz harmonics (120/180/240 Hz) fall INSIDE the EMG band (10–300 Hz); the comb-notch carves holes in the EMG spectrum. If EMG is hum-dominated, the "atonia" that defines REM becomes a filter artifact. The QC verdict never gates on EMG → any USABLE call certifies **Wake/NREM only, never REM** unless EMG is independently validated.
- **State-correlated dropout = the architecture-killer.** A2 swung 11%→80% untouched; quality is non-stationary from unknown causes. If contact quality correlates with behavioral state (movement/REM posture changes lead impedance), excluding bad epochs BIASES the state proportions → %REM/%NREM and bout/latency endpoints become unpublishable. Clean islands can still contribute to *spectral* endpoints (pooled NREM delta power), never to *architecture* endpoints, until the dropout mechanism is known.
- **Honest cleanup line:** linear, time-fixed, outcome-blind filters (comb-notch, bipolar subtraction, fixed bandpass) are legitimate and do not distort staging features. Adaptive per-epoch hum subtraction, rail interpolation, or post-hoc clean-window selection = fabrication. θ/δ cycling must exist in the RAW bipolar before any processing.
- **Scorer handoff:** EDF+, bipolar derivations labelled, correct µV units, decimated with anti-alias (method recorded), filter provenance in methods + annotations, explicit "Korea mains = 60 Hz" (the 50-vs-60 error already cost weeks), agreed epoch length, artifact-exclusion channel, RAW XDAT master preserved, impedance log.

---

## What the council forces us to retract

The mandate was zero bias. The council independently flagged five overstated claims in our own vault/QC — these must be corrected for the scientific record:

1. **"Earthing fix VALIDATED 2026-07-14 / paper-ready" (journal `2026-07-14.md`, `earthing-60hz-hum-fix.md`, MEMORY.md) is OVERSTATED.** It rests on 2 of 5 sub-minute clips where A2 was clean while A1 was simultaneously MARGINAL on the same earthed system, and A2 itself swung to HUM within minutes. That proves *a matched electrode rejects common-mode*, NOT that the earth fix works system-wide. The earth's effect was never isolated — no single-ended common-mode was logged before/after the electrician's bond.
2. **The "matched before/after pair" is NOT a controlled comparison.** The AFTER changed two variables (earth AND which electrode happened to be clean); A1 stayed dirty in the same clip. Attributing the difference to earthing alone is unsupported.
3. **Floating slots B/C/D are NOT a valid "floating-baseline control"** (this was in the evidence packet — a chairman error). Open, unconnected high-impedance inputs antenna mains 60 Hz regardless of system-earth state. Their loudness says nothing about the earth. Only CONNECTED channels are diagnostic. Flagged by all five advisors independently.
4. **`60Hz%raw` is the wrong primary metric.** It is a power *fraction* — denominator-confounded (a real clean channel reads "11%" because signal fills the denominator; a dead-quiet input reads ~100% while harmless). Replace with **absolute single-ended 60 Hz per leg (µV) + leg-imbalance ratio + notch-residual µV + delta-dominance (θ/δ)**.
5. **`multimouse_scan.py` has two verified statistical defects.** (a) `scan()` concatenates 40 heavily-overlapping windows before Welch → understates variance ~20× and makes fractions look far more settled than they are. (b) Sub-minute clips have effective independent coverage n_eff ≈ 2–4, not 40 → the celebrated 07-14 numbers are spot readings, not validated states. Also: the `USABLE` threshold allows `eeg_rms_n < 800 µV` (real mouse bipolar EEG is <300 µV) and never gates on EMG. Tighten USABLE to residual <250 µV AND delta-dominant; add an EMG gate or relabel USABLE as "Wake/NREM-usable."

---

## Advisor positions (provenance)

- **Electrical first-principles** — H3 ~80%; ran `cm_test.py` single-ended decomposition. A1 legs ~3 mV CM (floating signature), A2 diff/cm=6 (mismatch signature), both live at once. Falsifier: verified-earth clip watching single-ended CM. Corrected the "low notch-residual ⇒ common-mode ⇒ rescuable" misread (a notch kills a 60 Hz line whether CM or differential; differential-ness is measured by bip/cm, not notch residual).
- **Contrarian / null-hypothesis** — H2 ~55%, ground-loop-from-the-fix ~20%, H1 only ~15%; ran `diag.py`/`diag2.py`. Key: 07-15 is WORSE than pre-fix floating baseline (a lost earth can't explain that); per-leg asymmetric + non-stationary + divergent within-run drift = contact, not stable earth. "Squeeze did nothing" = the clip isn't the lever.
- **Signal-metrologist** — H3, H2 = variance / H1 = floor; ran `probe.py`/`discrim.py`/`timecourse.py`. PLV=1.00 (one source), bip/cm≈2 (differential), connected-A2 ≡ open-C1 spectrally (no buried biology), only A2-0714 is real EEG (42 s). Found the Welch-concatenation variance bug and n_eff=2–4 on sub-minute clips.
- **Bench-experimentalist** — leaned H1/H3 ~55%; delivered the one-step-at-a-time DMM earth-chain protocol and the GO/NO-GO gate. First measurement = Chassis-GND→verified-earth continuity to split {H1,H3} from {H2,H4}.
- **Sleep-EEG scoring** — Q2 lead. Only 140 µV/97% clip is scoreable-quality (but 42 s); 300–800 µV/7–25% definitely not. Raised the EMG-harmonic/REM hazard and the state-correlated-dropout architecture-killer. phys% is necessary not sufficient.

## Related
- [[2026-07-13-72h-4mouse-recording-audit]] — the 72 h floating-hum audit this extends.
- [[earthing-60hz-hum-fix]] · [[signal-quality-and-grounding]] · [[grounding-reference-noise-concepts]] · [[60hz-mains-hum-discovery]] · [[multimeter-guide]]
- [[2026-05-01-llm-council-review]] — prior council, same methodology.
