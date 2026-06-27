---
tags:
  - procedure
  - radiens
  - allego
  - signal-quality
  - grounding
  - eeg
  - emg
  - onboarding
created: 2026-06-19
status: complete
---

# Signal Quality & Grounding — Is the Signal Good Enough to Record?

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A plain guide to two things you do *after* the channels are mapped: (1) connect the **ground** properly, and (2) **look at the live signal** and decide whether it's good enough to start real recordings.
>
> **Why it exists.** Two mice are wired into **one** Intan headstage — which Intan never designed for. So we don't assume it works; we **look at the actual signal and decide.** This page tells you exactly what to look at, what "good" vs "bad" looks like, and the order to do things.
>
> **How to read this page.** Do the steps top to bottom. §1 = a quick selection trap to avoid. §2 = the grounding fix (the big one). §3 = how to judge the signal. §4 = the decision. Maps first: [[signal-mapping-guide]]. Software: [[radiens-software-reference]].

---

## The short version (if you read nothing else)

1. **Select the right channels** — with our custom map, pick **sites 1–8** (not 1–4 + 9–12). See §1.
2. **Fix the ground** — the green animal-ground wire must go to the board's **GND pad**, not a signal pad. See §2. *This is almost certainly why the signal looks noisy/flat-topped right now.*
3. **Then look at the signal** the right way — differences of pairs, not single wires — and check the two mice don't bleed into each other. See §3–§4.

---

## 1. First, a selection trap (sites vs. channel numbers)

When you load our custom sensor (`2mice32`), Allego **renumbers** the channel chips in the System tab by **site number**, not by the headstage's own channel number. That changes which chips you tick:

| Mouse | Signal | Pick this **site** | (headstage native ch) |
|---|---|---|---|
| 1 | EEG +/−, EMG +/− | **1, 2, 3, 4** | 0,1,2,3 |
| 2 | EEG +/−, EMG +/− | **5, 6, 7, 8** | 8,9,10,11 |

> [!warning] The mistake to avoid
> Mouse 2 is on **sites 5–8** — **not** 9–12. Sites 9–32 are the **unused/parked** channels. If you tick `1,2,3,4,9,10,11,12` (the habit from the plain "passthrough" numbering), you record **Mouse 1 plus junk**, and **Mouse 2 never streams**. Always pick the contiguous block **sites 1–8**.
> *(How to tell it went wrong: the Signal Metrics or a quick check shows Mouse 2's channels reading exactly 0.)*

---

## 2. Grounding — the one connection that makes or breaks the signal

### What "ground" does, in one sentence
The amplifier can only see voltages in a narrow window (about ±5 millivolts). If the **animal isn't connected to the headstage's ground**, the whole animal "floats" and drifts out of that window — so the traces **slam to the top/bottom (saturate)** and pick up big wall-power hum. Connecting the animal to ground holds it in the window.

### Our chip needs GND, but NOT a reference electrode
- Our headstage chip is the **RHD2216**, which is a **bipolar** chip: every channel already measures the **difference** between its own `+` and `−` wire. Each pair is its own reference.
- Because of that, the RHD2216 has **no "reference electrode" input** (that `ref_elec` pad only exists on the *unipolar* RHD2132). **So the adapter's `REF` pad is not used — leave it unconnected.** *(Confirmed in the Intan RHD2000 datasheet.)*
- What it **does** need is **GND** — the animal tied to the chip's ground.

### The fix (the "GND bridge")
- The adapter board (Intan **C3410**) has dedicated **`REF`** and **`GND`** pads, separate from the numbered signal pads.
- Right now **both green animal-ground wires are soldered to signal pads** — M1 green on **signal pad 5**, M2 green on **signal pad 13** — those are amplifier **inputs**, not ground. So **both animals are floating** (live 2026-06-22: all 4 M2 channels + M1 EMG− railed at 9–11.5 mV pk-pk).
- **→ Move BOTH greens off the signal pads to the shared `GND` net.** Leave `REF` empty.

> [!important] Two mice, one headstage = ONE shared ground net
> The RHD2216 has exactly **one** ground. Both animals must tie to it — there is no independent per-mouse ground without a second headstage. So both greens land on the **same** `GND` net. This is also why you **cannot** fully separate the mice electrically; if the cross-talk nudge test (§3e) fails, the shared ground is inherent and the real fix is one headstage per mouse.

### How we wire the shared ground — brass busbar star node (2026-06-23)
Rather than cram two thin wires onto the tiny C3410 `GND` pad, use a **5-position brass grounding busbar** (electrical ground/neutral bar — all 5 screw holes are one common brass strip = one electrical node) as a clean **star hub**:

```
M1 slip-ring GND ──► end screw 1 ┐
                                 ├─ common brass bar (star) ──► center screw ──► C3410 GND pad
M2 slip-ring GND ──► end screw 5 ┘
```

- Both mice's grounds + the single wire to the C3410 `GND` pad all meet on the common brass = the star node. Electrically identical to soldering all three onto the `GND` pad, but screw-terminal (no solder on the tiny pad, swappable).
- **The busbar does NOT separate the mice** — all 5 holes are common brass = one net. Same shared-ground caveat above applies.
- **Build checklist:**
  1. **Desolder** M1 green from C3410 **pad 5** and M2 green from **pad 13** (they go to the busbar now, not the signal pads). Afterward `pri_5`/`pri_13` inputs float — fine, they're parked/deselected (sites 10/14, not recorded).
  2. **Clamp thin wires properly** — tin the tip or fold double so the screw bites; fine-gauge tether wire slips out otherwise.
  3. **One wire** from the busbar center screw → C3410 `GND` pad.
  4. **DMM continuity** end-to-end: screw1 ↔ center ↔ screw5 ↔ C3410 `GND` pad all **~0 Ω**.
  5. **Mount the busbar close to the headstage** — short ground leads = smaller loop = less 50 Hz pickup.
  6. **Keep the bar isolated** — brass/screws must not touch other conductive parts (it sits at ground; a stray short to a signal pad is bad).

> [!note] How we know grounding is the problem right now
> Live metrics (2026-06-19) on Mouse 1: EEG+ and EMG+ read a sensible ~60–100 µV, but **EMG− was pegged at ~11.6 mV peak-to-peak — slammed against the rail** — and the green "ground" channel itself was railing. A railing channel that should be ground = the classic "animal is floating" signature. Expect this to calm down once the green wire is on the real `GND` pad.

---

## 3. How to look at the signal (the right way)

> Stream (don't Record) while you do this. **Record** starts a real session + video.

### a) Look at *differences*, not single wires
Your real signals are **pairs**:
- **EEG** = EEG+ minus EEG− (Mouse 1: sites 1 minus 2)
- **EMG** = EMG+ minus EMG− (Mouse 1: sites 3 minus 4)

A single wire on its own carries a lot of shared junk (hum, drift). Subtracting the pair cancels that junk and leaves the real brain/muscle signal. In Allego: **Signal Processing → Reference Types → Paired Reference** — set the `−` channel as the reference for its `+` partner. *(Manual p70.)* A healthy pair gets much cleaner after subtraction.

### b) Check for saturation (the deal-breaker)
In **Monitor**, no wired channel should sit **flat against the top or bottom** of its lane. Flat-topped = saturated = unusable (and usually a grounding problem). After the GND fix, the traces should sit in the middle and wiggle.

### c) Check the wall-power hum (50 Hz in Korea)
Turn on the **50 Hz notch** (Signal Processing) or look at the frequency view. A little hum is normal; a giant 50 Hz that buries the signal means grounding/shielding still needs work.

### d) Check the signals are real (a gentle nudge test)
- **EMG**: lightly move the animal (or the EMG lead) → the EMG trace should jump.
- **EEG**: slower, smaller waves that change with sleep/wake.
If a channel reacts to the *right* stimulus, it's wired to what you think it is.

### e) The two-mice question — check for cross-talk
This is the whole reason the professor said "look first." Because both animals share one headstage and one ground, **one mouse's signal can leak into the other's channels.**
- With both mice grounded and streaming, **nudge Mouse 1 only** and watch **Mouse 2's** four channels.
- **No reaction on Mouse 2** = good, the animals are independent.
- **Mouse 2 echoes Mouse 1** = they're coupled through the shared headstage → the two-mice setup isn't clean.

---

## 3b. The quality standard — good vs bad, with numbers

Two fixed anchors never change (they're set by the hardware), and everything is judged between them:

- **The noise floor ≈ 2–5 µV.** The RHD amplifier's own noise is about **2.4 µV RMS**. Nothing can be quieter than that. A dead-quiet, well-grounded channel reads a few µV.
- **The ceiling (rail) = ±5 mV = 5000 µV.** The amplifier physically cannot see past this. **Peak-to-peak ≈ 10 000 µV (10 mV) means the channel is pegged = saturated = useless.**

Real mouse signals live comfortably between those:
- **EEG** (brain): roughly **20–300 µV** amplitude; slow waves in sleep can reach several hundred µV.
- **EMG** (muscle): **~10–50 µV at rest**, jumping to hundreds of µV–~1 mV during movement.

### The cheat-sheet table

| What you measure | ✅ Good | 🟡 Marginal | 🔴 Bad |
|---|---|---|---|
| **Peak-to-peak** (Monitor, or `MAX_MIN_DIFF_ABS`) | < ~1–2 mV and **not clipping** | 2–5 mV | **≥ ~10 mV = saturated/railed** |
| **RMS / noise** (Signal Metrics, µV) | tens of µV (≈10–150) | few hundred µV | **> ~1000 µV (1 mV) = floating / hum** |
| **The trace looks like** (Monitor) | centered in its lane, wiggling | wiggling + visible hum | **flat line pinned at top/bottom** (saturated), or **dead-flat** (no connection), or a **fat 50 Hz sine** (hum) |
| **50 Hz wall hum** | small next to the signal | about the same size | **buries the signal** — toggling the 50 Hz notch changes the whole trace |
| **Does it react?** | EMG jumps when the animal moves; EEG changes with sleep/wake | weak/slow reaction | **no reaction to anything** |
| **Subtract the pair** (Paired Reference) | pair gets noticeably **cleaner** | small change | **can't recover** — one side is railed |
| **Two-mice cross-talk** | nudge Mouse 1 → Mouse 2 **doesn't move** | tiny echo | **Mouse 2 mirrors Mouse 1** |

> [!tip] The 3 numbers to memorize
> **~3 µV** = the quietest possible (noise floor). **tens–hundreds of µV** = healthy biological signal. **~10 000 µV (10 mV) peak-to-peak** = railed/dead. If a channel is reading thousands of µV RMS, it is **not** signal — it's a floating ground or hum.

### Where each number lives in Allego
- **Monitor tab** → the live picture. Watch for clipping (flat top/bottom) and set the µV/division scale so you can see the wiggle.
- **Signal Metrics tab** → the **numbers**: RMS and noise (µV) per channel. This is your quantitative judge. Set the bandpass first.
- **Signal Processing tab** → apply the right **bandpass** (EEG ≈ 0.5–30 Hz, EMG ≈ 10–300 Hz), the **50 Hz notch**, and **Paired Reference** for the +/− pairs.
- **HD Snapshot** → save a still image of a good (or bad) trace for your records.

---

## 3c. Your every-session 5-minute check (do this each time)

1. **Bandpass + notch on.** Signal Processing: EEG band on the EEG channels, EMG band on the EMG channels, 50 Hz notch on.
2. **Glance at Monitor.** Any channel flat-pinned at top/bottom? → saturated, stop and fix grounding. Any dead-flat line? → broken connection.
3. **Read Signal Metrics.** Background RMS in **tens of µV** = good. **Thousands of µV** = floating/hum, fix before recording.
4. **Pair-subtract (Paired Reference)** the EEG and EMG pairs — they should get cleaner.
5. **Nudge test.** Move the animal → EMG jumps (proves it's alive and correctly mapped). For two mice: nudge one, confirm the **other doesn't move** (no cross-talk).

If all five pass → record. If any fails → fix that first (usually grounding or a loose wire).

---

## 4. The decision

Do it in this order — each step unblocks the next:

1. **Select sites 1–8** (so both mice actually stream). §1
2. **Move the green wire to the `GND` pad** (so the animal is grounded). §2
3. **Re-look at the signal** — differences of pairs, no saturation, hum under control. §3a–d
4. **Run the cross-talk nudge test.** §3e

**Then decide:**
- Pairs look clean, no saturation, manageable hum, **and** the mice don't bleed into each other → **good to record.**
- Mice cross-talk, or channels still saturate after grounding → the one-headstage-two-mice idea doesn't hold; options are separate grounds, or one headstage per mouse. Bring this back to the professor with the specific finding.

> [!important] Don't judge too early
> You **cannot** fairly judge the two-mice setup while channels are saturating from a missing ground — the saturation hides everything. Ground first, *then* evaluate.

---

## Appendix — reading the signal numbers without the GUI (optional, technical)

You can pull per-channel quality numbers headless via the Radiens Python SDK (`signal_metrics().get_metrics(...)`), which returns RMS, noise, peak-to-peak, and SNR per channel.

> [!bug] SDK quirk (radiens 4.0.0 + NumPy 2.x)
> `get_metrics()` crashes with `module 'numpy' has no attribute 'NAN'` because the SDK uses the old `np.NAN` (removed in NumPy 2.x). Work around it by shimming before the call:
> ```python
> import numpy as np
> if not hasattr(np, "NAN"): np.NAN = np.nan
> from radiens import AllegoClient
> sm = AllegoClient().signal_metrics().get_metrics(time_range=2.0, plot=False)
> # sm.val is shape (1, 32, 6); columns = RMS, NOISE_UV, MAX_MIN_DIFF_ABS, SNR, EVENT_RATE, EVENT_MEAN
> ```
> Peak-to-peak (`MAX_MIN_DIFF_ABS`) near ~10–12 mV = a railed/saturated channel.

---

## Related
- [[grounding-reference-noise-concepts]] — ⭐ ground vs reference vs tissue noise vs environmental noise (kept strictly separate); the copper-coil environmental reference; the slip-ring green↔orange color-swap defect (animal ground → nothing; rebuild required)
- [[signal-mapping-guide]] — map channels to electrodes first (sites, EEG/EMG, csv2sensor)
- [[radiens-software-reference]] — Allego/Videre reference (referencing p70, manual embedded)
- [[first-headstage-connection]] — bring-up + this rig's channel map
