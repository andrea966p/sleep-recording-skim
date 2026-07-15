---
tags: [procedure, eeg, grounding, mains-hum, reconciliation, history]
created: 2026-07-15
status: active
priority: high
---

# Why early bring-up worked WITHOUT the earth wire — floating common-mode vs electrode contact (reconciliation)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** An answer to a real doubt: if the recording system was floating (no earth) the whole time, how did the early troubleshooting (channel mapping, "one mouse per headstage", grounding topology, even the 2026-07-05 "5 of 8 mice usable" result) ever produce sensible signals? See [[01-infrastructure/system-overview]] for the big picture.
>
> **Why it exists.** So this apparent contradiction does not resurface and get mis-diagnosed later. It also cross-checks that the "floating system" diagnosis and the newer "contact is the binding variable" verdict are the SAME physics, not two competing stories.
>
> **How to read this page.** The one equation below explains everything. The rest is the evidence that the floating problem was always present but MASKED whenever electrode contacts happened to be good.

> [!quote] Paper-ready
> The acquisition system was electrically floating throughout early development, yet physiological EEG was recoverable on a subset of channels because a well-matched, low-impedance bipolar electrode pair rejects even a large common-mode mains voltage. Usability was therefore governed by electrode-impedance balance (the variable term) against a constant floating common-mode background (the floor), so the floating condition remained undiagnosed until multi-day recordings exhausted the margin that good contacts provided.

---

## The doubt

The 60 Hz hum on 2026-07-15 was traced to a floating acquisition system plus per-electrode contact problems. But the system was floating (no earth wire on the XDAQ) for ALL of the early work too. So how did we ever conclude anything back then, map channels, decide one mouse per headstage, and get "5 of 8 mice usable" on 2026-07-05, without the earth wire?

## The one equation that resolves it

```
differential_hum_at_amplifier  ≈  common_mode_mains_voltage  ×  electrode_impedance_imbalance
                                    ^^^ floor: floating = big ^^^   ^^^ variable: contact quality ^^^
```

A floating system always sits in the building's 60 Hz field, so the common-mode (CM) voltage on every input is large (measured 15 µV to ~4900 µV across electrodes on 2026-07-05, up to 2–5 mV on the multi-day runs). Bipolar recording (frontal − parietal) rejects the CM, but only as well as the two legs are impedance-matched. So:

- **Good, low-impedance, matched pair** → imbalance ≈ 0 → differential hum ≈ 0 → clean EEG, EVEN on a floating system.
- **Open / high-impedance / mismatched pair** → the big CM converts to real differential hum that no notch or bipolar can remove → unusable.

Whether any given channel looked fine depended entirely on the CONTACT term. The floating CM was a constant background the whole time.

## Two independent reasons the early conclusions held

**1. Most early conclusions never needed clean EEG at all** — they are hum-independent, read from DC/rail state, enumeration, impedance, and which channel responds:
- "railing = open input" (later refined by the 60 Hz discovery), the natives 16–31 quiet-means-grounded floor, bottom-SPI-socket-only, `XDAQ_ONE_REC` mode, and the whole sleep64 channel map.
- **The "one mouse per headstage" decision (2-mice-share-GND retracted) is a HARDWARE fact**, not a signal-quality one: the RHD2216 is a single 16-channel bipolar chip with `REF` empty by design, so two animals cannot cleanly share it. That is read off the chip and which natives are populated, and is completely independent of the hum.

**2. The early "usable" signals came from good-contact animals.** On 2026-07-05 ([[60hz-mains-hum-discovery]] §3–4), on a floating system, 5 of 8 mice gave usable EEG after a 60 Hz notch + bipolar. The known-good animal M1 sat at ~88 µV CM and was clean; the unusable ones were multi-mV and clipped. That is exactly the equation above: the good animals had low imbalance, so the floating CM got rejected. The floating problem was present but MASKED by good contacts.

## Why it only became the headline later

Two confounds were tangled early and both were bypassed by good contacts:
- the **50 Hz → 60 Hz notch error** (wrong mains line made good electrodes look "railed"), and
- the **floating common-mode** (rejected fine whenever contacts were good).

The floating condition only became the identified root cause when the 72 h and 20 h multi-day runs needed ALL channels stable for DAYS. At that scale and duration the good-contact margin ran out, small impedance mismatches converted enough of the large CM to differential hum (and some legs clipped the ±6.4 mV rail irreversibly), and the runs came back 0/4 and 0/8 scoreable. See [[2026-07-13-72h-4mouse-recording-audit]] and [[earthing-60hz-hum-fix]].

## Consistency check — the story is one story

The 2026-07-15 council ([[2026-07-15-earth-and-sleep-council]]) concluded **contact is the binding variable, earth is the floor**. The 2026-07-05 data said the same thing a different way: usability tracked contact quality against a constant floating CM. Same physics, same equation, no contradiction. The earth wire was never needed to derive the layout and hardware facts, and it was never the ONLY lever — a good contact could always beat the floating floor, which is precisely why the floating system hid for so long.

## Practical takeaway

- Do not treat "we got clean data once without earth" as evidence the system is not floating. A single good-contact channel proves only that ITS pair is matched, not that the system is earthed.
- Conversely, do not treat one bad multi-day run as proof of a NEW fault. The floor was always there. Fix BOTH: earth the XDAQ to lower the floor, and get every EEG leg to 0.1–1 MΩ matched within 2–3× to keep the variable term near zero.

## Related
- [[60hz-mains-hum-discovery]] — the 2026-07-05 measurement this reconciles.
- [[earthing-60hz-hum-fix]] — earthing the floor.
- [[2026-07-15-earth-and-sleep-council]] — the council that formalised the equation.
- [[grounding-reference-noise-concepts]] · [[signal-quality-and-grounding]].
