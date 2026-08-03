---
tags: [decision, eeg, impedance, electrodes, literature, methods, critical]
created: 2026-08-03
status: active
priority: critical
---

# 2026-08-03 — Literature check: our impedances, our failure mode, and what six papers say about both

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Six primary papers on mouse EEG/EMG electrodes read against our
> own data, to test whether our interpretation of the rig holds up.
>
> **The headline.** Our interpretation mostly survives, but **one central
> assumption is now in doubt**: we have been treating "EMG works, EEG doesn't" as
> proof that the fault is in our wiring. The literature says epidural electrodes
> fail on their own at a very high rate, while muscle wires do not — so the
> asymmetry may be normal biology, not a solder fault.
>
> **The number that matters.** A published mouse chronic-EEG study lost at least
> one electrode in **82% of animals within three weeks**, using the same class of
> electrode we use.

Papers in `~/Desktop/andrea/papers/`. Evaluated against
[[2026-08-03-two-8-mouse-runs]] and [[pipeline/README]].

## The six papers

| # | Paper | What we took from it |
| --- | --- | --- |
| 1 | **Hsieh et al., *eNeuro* 11(2), 2024** — open-source mouse chronic EEG array, MXene skull electrodes | electrode **loss rates**, chronic impedance stability |
| 2 | **Kim et al., *Sci Data* 9, 2022** — nine-day continuous mouse EEG under sleep restriction | screw impedance values, acquisition filter chain |
| 3 | **Choi et al., *J Neurophysiol* 104, 2010** — high-resolution EEG in freely moving mice | impedance benchmarks, EEG dynamic range |
| 4 | **Kappenman & Luck, *Psychophysiology* 47, 2010** — impedance vs data quality | whether impedance actually hurts, and how |
| 5 | **Oishi et al., *JoVE* 107, 2016** — polygraphic sleep recording in mice | the standard EEG/EMG protocol, habituation |
| 6 | **Needle-electrode preprint, 2026** | screw vs needle, signal quality vs impedance |

## 1. Published impedance values, against ours

| source | electrode | impedance | frequency |
| --- | --- | --- | --- |
| Choi 2010 | nanofabricated microelectrode | **2–3.5 kΩ** | 10–10⁴ Hz |
| Choi 2010 | skull screw | **< 100 kΩ** | 30 Hz |
| Hsieh 2024 | epidural 0.1 mm / MXene, in use | **10–29 kΩ** | 1 kHz |
| Kim 2022 | stainless screw 0.8 mm | **10–50 kΩ** | 1 kHz |
| Kim 2022 | HD-EEG contact, chronic | **~100 kΩ** | 1 kHz |
| **ours — best channel in the whole fleet** | dura pin | **73 kΩ** | 1 kHz |
| **ours — C1 EEG, our best animal** | dura pin | **465 kΩ** | 1 kHz |
| **ours — typical "open"** | dura pin | **4 000–9 000 kΩ** | 1 kHz |

> [!danger] Our single best channel sits at the literature's *worst* acceptable value
> 73 kΩ is roughly where Kim 2022's chronically-implanted HD contacts end up
> (~100 kΩ) and just under Choi 2010's screw ceiling (<100 kΩ). **Everything else
> we have is worse than anything published.** C1 — the animal that produced the
> project's only defensible sleep — was at **465 kΩ**, five to fifty times the
> published good range.
>
> This **confirms and sharpens** the correction already made to
> [[electrode-connection-state-test]]: our 2 MΩ "connected" bar is not a quality
> threshold, it is an open-circuit detector. The literature has no category for a
> 465 kΩ epidural electrode being *good*.

## 2. 🔴 The finding that changes our interpretation

> [!important] Hsieh et al. 2024, *eNeuro*, N = 11 per group
> > "**82% of the epidural 0.1 mm preparations lost at least one electrode within
> > 3 weeks of surgery**, only 18% of the MXene implants lost at least one
> > electrode at 3 weeks."
>
> And for high-density channels: dislodgement probabilities of **0.38 and 0.31 in
> week 1 alone**.

**Progressive, irreversible loss of epidural electrodes is the documented baseline
for this electrode class.** It is not an anomaly, not evidence of a bad surgeon,
and not evidence of a rig fault.

Our Run 1 → Run 2 observation — **EEG impedance rose on 8 of 8 animals, none
improved, and C1 went 0.465 → 5.720 → 7.929 MΩ and never came back** — is exactly
the shape of that published failure. We had been describing it as a mystery. The
literature describes it as expected.

The same paper also reports the fix: **1.0 mm epidural electrodes are more stable
than 0.1 mm**, and MXene-coated skull electrodes drop the 3-week loss rate from
82% to 18%. That is an *electrode-design* fix, not a surgical-technique fix.

## 3. ⚠️ The EMG-works/EEG-fails asymmetry is weaker evidence than we thought

This is the correction that matters most, because it currently drives our
top-priority action.

**Our standing argument** ([[electrode-connection-state-test]], and the tier-1
plan): A1 and D1 have perfect EMG and zero EEG through the *same* tether, slip
ring, board, headstage and port; therefore that shared path is proven good;
therefore the fault is in the EEG-specific segment — the C3410 pad 0/1 solder or
the two EEG slip-ring wires.

**The first half still holds.** A working EMG really does prove the shared path
carries signal. That inference is sound and unaffected.

**The second half does not follow.** The two channels do not use the same
electrode at the animal end:

| | EEG | EMG |
| --- | --- | --- |
| our electrode | **dura pin, epidural contact** | **stripped wire sewn into neck muscle** (Oishi 2016 §1.1.3, §2.5) |
| published failure rate | **82% lose ≥1 electrode in 3 weeks** (Hsieh 2024) | not reported as a common failure |
| failure mechanism | dislodgement, bone regrowth, CSF/air at the interface | mechanically anchored in tissue |

So there are **two explanations** for "EMG fine, EEG open", and our data does not
yet distinguish them:

1. **A cold joint on C3410 pads 0/1** or a broken EEG slip-ring wire — our
   current hypothesis, free to test.
2. **The dura pins have dislodged** — the literature's default expectation for
   this electrode type, and consistent with the one-way irreversible degradation
   we measured.

> [!warning] What this changes, and what it does not
> **Do the tier-1 bench test anyway.** It is free, it takes an afternoon, it
> touches no animal, and it cleanly separates the two hypotheses: if pads 0/1 and
> the slip-ring wires read good on a DMM, explanation 1 is dead and the fault is
> at the electrode.
>
> **But stop describing it as the likely cause.** Our vault framed the asymmetry
> as near-proof of a rig-side fault. On the published base rates, explanation 2 is
> at least as likely. Update the expectation, not the plan.

## 4. Impedance and 60 Hz hum — our claim is ours alone, and that is fine

We report that hum amplitude is a direct readout of contact: **connected 9–90 µV,
open 1000–4700 µV**, cleanly bimodal with the valley at 134 µV.

Kappenman & Luck 2010 is the standard citation for impedance vs quality, and it
**does not support a link between impedance and line noise**:

> "The present study found no detectable impact of electrode impedance on 60-Hz
> line noise, but the recording environment was so well shielded that the line
> noise was too small to be measured."

They could not test it, and they note a prior study (Ferree 2001) also found none.

> [!note] Why this does not contradict us — and how to phrase it
> Kappenman compared **5 kΩ vs 50 kΩ**: two *connected* electrodes an order of
> magnitude apart. We are comparing **~10² kΩ vs ~10⁴ kΩ** — connected versus
> **open circuit**. Those are different regimes, and an open input is not a
> high-impedance input; it is no input.
>
> **Do not cite Kappenman in support of our hum finding.** Present it as our own
> empirical result — a bimodal separation measured over 1,137,955 epochs in 41
> animal-recordings — and note that the literature has not characterised this
> regime. That is an honest and defensible position, and it is a genuine
> methodological contribution rather than a borrowed one.

Two further Kappenman points that *do* apply to us:

- **High impedance is workable with modern amplifiers**, with effects mitigated by
  high-pass filtering and artifact rejection. This is consistent with C1 giving
  good data at 465 kΩ, and it means a marginal channel is not automatically lost.
- **Warm, humid conditions make high-impedance recordings substantially worse.**
  We have never logged temperature or humidity in the animal room. Worth adding.

## 5. Protocol comparison — where we differ from the standard

| | published | ours | verdict |
| --- | --- | --- | --- |
| epoch | 10 s (Oishi 2016, Kim 2022), 5 s (needle 2026) | **4 s** | fine — finer end of the accepted range, we never report bouts < 2 epochs |
| EEG band | 0.5–64 Hz (Oishi), 0.3–100 Hz (Kim) | **0.5–30 Hz** | fine for sleep; we lose nothing above 30 Hz that staging uses |
| EMG band | **16–64 Hz** (Oishi) | **10–300 Hz** | ours is much broader; more movement artefact, more mains |
| delta | 0.5–4 Hz | 0.5–4 Hz | matches |
| theta | 6–10 Hz (Oishi), 5–10 Hz (needle) | **6–9 Hz** | matches |
| 60 Hz notch | **hardware notch at acquisition** (Kim 2022) | **none** — display only | deliberate, see below |
| montage | frontal + parietal one hemisphere, bilateral neck EMG | same | matches |

**On the notch.** Kim 2022 applies a 60 Hz hardware notch during acquisition. We
verified in 2026-07-31 that Allego's notch is display-only and never reaches the
saved data. Adopting a hardware notch would clean the traces — **and would destroy
our single best contact diagnostic**, since hum amplitude is how we detect an open
electrode. Recommendation: **keep acquisition raw**, notch at analysis time if a
figure needs it.

**On the EMG band.** Narrowing from 10–300 Hz toward Oishi's 16–64 Hz is worth
testing offline on C1 — it would reduce mains contamination of the EMG channel,
which currently participates in our OPEN test. Cheap to check, no re-recording
needed.

## 6. ❓ Habituation — an open question we cannot answer from the data

Oishi 2016 specifies **habituate the mouse 2–3 days in the recording chamber**
before recording. Our own [[tsukuba-sleep-recording-method]] is stricter:
**recover ≥5 days, acclimate to the recording cage ≥7 days, ≥14 days from implant
to recording.**

Two things follow, and both need an answer from the bench, not from me:

1. **Was the habituation schedule followed for Runs 1 and 2?** If recording began
   sooner, the sleep numbers are depressed by stress and the 2026-06-29 animal
   (95% awake, 2.56 h continuous wake bout) is fully explained rather than
   "probably acclimatisation".
2. **How many days post-implant were these runs?** Hsieh 2024 puts peak
   dislodgement probability in **week 1**. If we are recording inside that window,
   we are sampling exactly when electrodes are most likely to fail — which would
   explain the degradation without invoking any rig fault at all.

Neither is recorded anywhere in the vault. **Start logging implant date and
tethering date per animal.**

## 7. What survives, what changes

**Survives unchanged**
- C1 is real sleep. Nothing in these papers weakens it; Choi 2010's "mouse EEG
  dynamic range within 100 µV" matches C1's 52–70 µV rms.
- Contact is the bottleneck.
- Hum is a valid contact readout (as our own result).
- Impedance predicts class, not yield.
- The rig is exonerated — 9 µV hum, 100% gate pass on 2026-06-29.

**Changes**
- 🔴 **The EMG/EEG asymmetry is no longer strong evidence of a rig-side fault.**
  Different electrode types with very different published failure rates.
- 🔴 **Progressive EEG loss is the expected baseline for epidural electrodes**
  (82% in 3 weeks), not an anomaly needing a special explanation.
- ⚠️ **Even our best channels are poor by published standards** — 73 kΩ best,
  465 kΩ on C1, against 10–50 kΩ published.
- ⚠️ **Do not cite Kappenman for the hum result.** Different impedance regime.

**New actions**
1. **Tier-1 bench test** — unchanged in priority, now also a discriminator between
   the two hypotheses rather than a confirmation of one.
2. **Record implant date and tethering date per animal.** Cannot interpret
   degradation without them.
3. **Consider a different electrode for the next cohort** — 1.0 mm epidural rather
   than fine pins, per Hsieh 2024. This is the literature's own answer to our
   exact failure, and it is a design change, not a surgical-skill issue.
4. **Log animal-room temperature and humidity** (Kappenman: warm/humid degrades
   high-impedance recordings, and all our channels are high-impedance).
5. **Test a 16–64 Hz EMG band offline on C1.**
6. **Keep acquisition un-notched.**
