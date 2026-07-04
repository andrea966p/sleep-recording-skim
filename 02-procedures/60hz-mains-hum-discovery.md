---
tags: [procedure, eeg, emg, signal-quality, mains-hum, 60hz, critical, discovery]
created: 2026-07-05
status: active
priority: critical
---

# ⚠️🔴 CRITICAL DISCOVERY — Korea mains is 60 Hz, NOT 50 Hz. Weeks of "bad electrodes" were mostly 60 Hz hum + a wrong notch.

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

## Related
- [[2026-07-05]] — the session where this was found (full log + measurements)
- [[eight-mouse-acquisition-setup]] — 8-mouse map + channel selection (now correct)
- [[signal-quality-and-grounding]] — signal-eval guide (being corrected 50→60 Hz)
- [[grounding-reference-noise-concepts]] — ground vs reference vs noise (the hum-rejection physics)
