---
type: reference
area: eeg-rig
status: active
tags: [procedure, eeg, emg, signal-quality, mains-hum, 60hz, critical, discovery]
created: 2026-07-05
priority: critical
---

# ⚠️🔴 CRITICAL DISCOVERY — Korea mains is 60 Hz, NOT 50 Hz. Weeks of "bad electrodes" were mostly 60 Hz hum + a wrong notch.

> [!warning] Updated 2026-10-22: The 60 Hz fact stands. The "pad0−pad1" bipolar difference here was EEG minus EMG under the old channel map (corrected 2026-08-01), and the 2026-07-31 no-wire control showed most railing legs really were not connected. [[2026-08-01-channel-mapping-correction-first-sleep]]

> [!danger] READ THIS BEFORE JUDGING ANY EEG/EMG SIGNAL AGAIN
> For weeks every rig session was judged with a **50 Hz** notch and a "50 Hz (Korea)" assumption. **South Korea mains is 60 Hz** (220 V / 60 Hz, nationwide). The notch was on the wrong line the entire time, so the real interference — **60 Hz mains hum** — was **never removed**. Channels drowning in 60 Hz common-mode hum looked "railed / open / bad contact," and we concluded the mice were badly implanted. **That conclusion was largely WRONG.** The dominant problem was environmental 60 Hz + the wrong notch, a **single systematic issue**, not 8 independent bad surgeries. Measured and confirmed 2026-07-05 ([[2026-07-05]]).

> [!quote] Paper-ready
> Line interference in the recording environment is at 60 Hz (South Korean mains). Earlier analyses applied a 50 Hz notch, leaving the 60 Hz component and its harmonics unattenuated; single-ended channels were consequently dominated by common-mode mains interference (up to several millivolts), which was initially misattributed to poor electrode contact. Bipolar re-referencing with a 60 Hz notch recovers physiological EEG on the majority of channels.

---

## 1. What actually happened (plain language)

- Every recording channel picks up the building's **mains hum**. In Korea that hum is at **60 Hz**.
- We had the software's **notch filter set to 50 Hz**, and all our "is the signal good?" checks assumed 50 Hz. So the 60 Hz hum sailed straight through, untouched.
- On a **single** electrode wire, that 60 Hz hum is **huge — around 10 millivolts** (the real brain signal is only tens of *micro*volts, ~1000× smaller). So a single channel looks like a giant 60 Hz sine wave slamming up and down = what we kept calling **"railing / open / no contact."**
- We saw that on almost every channel of almost every mouse and concluded: **all the mice are badly implanted.** Understandable — but wrong. It was the **same 60 Hz hum on all of them**, because it's environmental, not per-animal.

## 2. Why the real signal was hidden — and how it comes back

The EEG is recorded **bipolar**: EEG = (frontal electrode − parietal electrode). Mains hum arrives on both electrodes almost equally (**common-mode**), so **subtracting the pair cancels most of the hum** and leaves the brain signal. Two things were stopping us from seeing that:

1. We were looking at **single channels**, not the **difference** of the pair.
2. The **notch was on 50 Hz**, so even the leftover hum wasn't filtered.

Do it right — **bipolar difference + a 60 Hz notch** — and real, delta-rich EEG appears on most mice (see §4).

## 3. The one real limit that remains: clipping

The amplifier only sees **±6.4 mV**. When the 60 Hz hum on a high-impedance electrode is bigger than that, the signal **clips (saturates)** — those samples are **flat-topped and gone forever**. No filter recovers clipped data. So:

- **Low-hum electrodes** (good ground, low impedance): hum stays small, nothing clips, bipolar + notch → clean EEG. **Record.**
- **High-hum electrodes**: hum saturates the amp → that leg is lost **until the hum is reduced at the source** (grounding / shielding). This is why ~3 of 8 mice still have unusable legs — not bad surgery, **too much 60 Hz**.

**Hum size tracks grounding quality.** Measured common-mode 60 Hz ranged **15 µV to ~4900 µV** across electrodes. Mouse **A1 (M1)** — our known-good animal — rejects the hum (~88 µV) and gives clean EEG, proving the rig *can* do it. The noisy ones need a better ground path, not a re-do of the implant.

## 4. Evidence (measured live 2026-07-05, all 8 mice, 4-port C3442)

- **Dominant frequency = 59.9 Hz on every channel** — clean and "railing" alike. The tell that it's 60 Hz mains.
- "Railing" channels: **~100 % of the power is at 60 Hz**, ~0 % in the 1–45 Hz EEG band → it's hum, not broadband open-input noise.
- After **60 Hz notch + bipolar difference (pad0−pad1)**:

| Mouse | recovered EEG (µV RMS) | leg clipping | verdict |
|---|---|---|---|
| M1 (A1) | 310 | 0 % | usable |
| M3 | 202 | 8 % | usable |
| M4 | 56 (delta-rich) | 5 % | **clear real EEG** |
| M5 | 134 | 1 % | usable |
| M6 | 703 | 4 % | usable |
| M2 | 84 | **17 %** | clipped — cut hum first |
| M7 | 133 | **16 %** | clipped |
| M8 | 364 | **11 %** | clipped |

→ **5 of 8 mice give usable EEG right now** with correct 60 Hz handling; the other 3 need the hum reduced before their legs are recoverable.

## 5. What to do

1. **Set the Allego notch to 60 Hz** (System / Signal Processing) — not 50. Immediate, biggest single win.
2. **Fix all analysis to 60 Hz** — every notch, every `iirnotch`/band-exclude in the scripts, every "50 Hz" in the procedure docs (sweep list in §6).
3. **Reduce 60 Hz at the source** so nothing clips:
   - **Grounding is the main lever** — each animal's ground electrode must be low-impedance and solidly on headstage `GND`. A1 proves a good ground kills the hum.
   - Check for **ground loops** — the mini-PC, cameras, and rig sharing mains; a single clean ground reference.
   - Consider **shielding** (Faraday) and moving cabling away from mains/PSU.
4. **Re-record / re-evaluate** — with 60 Hz notch + good ground, re-check all 8; record the non-clipping mice now.

## 6. Correction sweep — every "50 Hz" is wrong

> [!warning] These docs were written under the 50 Hz error and are being corrected to 60 Hz
> Active procedure/analysis docs to fix: [[signal-quality-and-grounding]], [[signal-mapping-guide]], [[grounding-reference-noise-concepts]], [[eeg-emg-data-guide]], [[sleep-recording-operator-manual]], [[rig-assembly-guide]], [[intan-headstage-troubleshooting]], and `eeg-data-analysis/03-scripts-and-usage`, `04-processing-guidelines` (+ any hardcoded 50 Hz in the analysis scripts). **Journals are historical and left as-is** (they record what we believed at the time).

## 7. What this reverses

> [!important] Refines a durable "fact" we had wrong
> Earlier durable claim: *"a railing wired channel = OPEN input / no electrode contact."* **Partly wrong.** A railing single channel was usually **60 Hz common-mode hum**, present even on well-contacted electrodes. Contact still matters (it sets how much hum a channel picks up and whether it clips), but "railing ≠ automatically a dead electrode." Judge the **bipolar difference with a 60 Hz notch**, not the raw single channel.

## 8. Hum-reduction troubleshooting checklist (do at the rig, in order)

> [!important] The notch does NOT reduce hum
> Allego's 60 Hz notch runs **after** the amplifier — it cleans the display/output but the hum still enters the amp, so it **cannot stop clipping**. Everything below reduces 60 Hz **at the source, before the amp** — the only thing that recovers the clipping mice (M2, M7, M8).

> [!note] Anchor facts (measured this rig, 2026-07-05)
> Common-mode 60 Hz ranged **15 µV → ~4900 µV** across electrodes and **tracks ground quality**: A1/M1 (good ground) = ~88 µV → clean EEG; M2/M6/M7/M8 = thousands → clipping the **±6.4 mV** amp rail. Same room, same field — the difference is the ground. So **fix grounds first**, and **fix the high-hum animals first** (M2, M6, M7, M8). Clipped samples are unrecoverable; reducing hum below ±6.4 mV is what matters.

### A. Grounding — biggest lever, start here (per animal)
- [ ] Verify the ground path is electrically solid: animal ground (green) → slip-ring → brass busbar → C3410 `GND`. **DMM continuity end-to-end ≈ 0 Ω** (per [[signal-quality-and-grounding]] §2 busbar checklist).
- [ ] **Measure the GROUND electrode's own impedance** (Allego GUI, paused — never SDK while streaming). A high-impedance ground is the usual cause of big common-mode. Want it **low** (signal electrodes good < ~1 MΩ; a ground ideally lower still). If the ground reads open/high, the animal isn't held at amp ground → hum everywhere on that animal.
- [ ] Confirm the ground electrode makes real low-impedance tissue contact (bone screw to dura/CSF, not loose in dry bone).
- [ ] Confirm `REF` left empty (RHD2216 is bipolar — correct) and the green is on `GND`, not a signal pad.
- [ ] Confirm **floor channels quiet** while streaming (HS-A natives 16–31, HS-B 48–63): quiet ⇒ grounded, all-railing ⇒ that animal floats.

### B. Ground loops + nearby mains sources (free, do next)
- [ ] Inspect for multiple earth paths around one animal (mouse earthed through more than one device) → aim for a **single ground reference**.
- [ ] Check for mains sources near the cage/tether and move them ≥ ~1 m: **power-supply bricks, wall-warts, PoE injectors, the mini-PC PSU, camera power adapters, chargers, fluorescent/LED drivers**.
- [ ] Route the tether / SPI cable **away from and not parallel to power cords** (cross at 90° if unavoidable).

### C. Shielding (Faraday) — if A+B leave residual hum
- [ ] Enclose the cage/recording area in a **grounded conductive shield** (copper mesh / aluminum sheet or foil / metal enclosure), tied to **amplifier ground** (single point, no loop).

### D. Lead hygiene (cheap wins)
- [ ] **Twist each +/− pair** (EEG frontal/parietal, EMG L/R) so both wires pick up identical hum → better common-mode cancellation.
- [ ] Keep ground leads **short**, minimize loop area (mount busbar close to the headstage).
- [ ] If the copper-coil environmental reference (orange → pad 6) is wired, keep it — it can subtract ambient noise.

### E. Verify each fix worked
- [ ] Re-check the **per-mouse 60 Hz level** after each change (live meter available via SDK on request, or watch the frequency view in Allego). Target: hum small enough that **no leg clips** and the **bipolar difference (60 Hz notch on)** shows clean tens-of-µV EEG.
- [ ] Re-run impedance (GUI, paused) + the bipolar-difference check on all 8; record the mice that no longer clip.

> [!warning] Don't blame surgery until hum is handled
> Given A1 proves the rig can reject the hum, treat railing/clipping as a **60 Hz + grounding** problem first. Only after A–D are done and hum is low should a still-bad electrode be attributed to contact/implant.

## Related
- [[2026-07-05]] — the session where this was found (full log + measurements)
- [[eight-mouse-acquisition-setup]] — 8-mouse map + channel selection (now correct)
- [[signal-quality-and-grounding]] — signal-eval guide (corrected 50→60 Hz)
- [[grounding-reference-noise-concepts]] — ground vs reference vs noise (the hum-rejection physics)
