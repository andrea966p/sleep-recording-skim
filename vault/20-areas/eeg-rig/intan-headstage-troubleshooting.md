---
type: incident
area: eeg-rig
status: active
status-note: "complete"
tags:
  - procedure
  - headstage
  - intan
  - allego
  - radiens
  - eeg
  - emg
  - onboarding
created: 2026-06-27
---

# Intan Headstage Troubleshooting — Symptom → Cause → Fix

> [!warning] Updated 2026-10-22: Sleep runs record at 1000 Hz, not 30000; channel selection is `/1`, `/2` (`/33`, `/34`) with no Paired Reference. Later fault signatures (weak chip ground, chewed or bending tether) are in [[per-animal-failure-signatures]] and [[weak-chip-ground-vs-open-electrode]]

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The master symptom-lookup for the Intan/XDAQ recording rig: the headstage won't appear in Allego, or it appears but every trace is garbage. Find your symptom, read the most likely cause, apply the fix.
>
> **Why it exists.** We have repeatedly burned days chasing the wrong cause — a "dead headstage" that was really the wrong software mode, a "broken solder joint" that was really a missing animal-ground electrode. This page captures the verified cases from our own bench logs so the next person jumps straight to the real fix.
>
> **How to read this page.** §1 = the one-glance master table. §2–§6 = the deep dive per symptom, each linking the dedicated guide. Tests live in [[multimeter-guide]]; assembly in [[rig-assembly-guide]]. Big picture: [[nvr-system-overview]].

> [!important] Two independent questions — never conflate them
> **(1) Does the headstage enumerate?** = a bus-powered SPI chip-ID read; **independent of the electrode/GND/animal side.** A bare headstage with nothing on the electrode inputs still reports its channels.
> **(2) Is the signal good?** = needs grounding, mapping, filtering.
> A railing trace is **not** an enumeration problem, and a `{}` port is **not** a grounding problem. Decide which question you're on **first**.

---

## 1. Master table

| # | Symptom | Most likely cause | Fix | Source |
|---|---|---|---|---|
| a | **Port shows 0 channels / `port_num_channels={}` / `priSigs=0`** | **Wrong Allego mode** (`SMARTBOX_PRO`) — connects + scans but reports 0 with our hardware | Set mode = **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`); restore sample rate to 30000; re-check on every relaunch | [[first-headstage-connection]] (RESOLVED 06-19) |
| a2 | **Still 0 after mode fixed** | SPI **signal-pin** contact fault (headstage Omnetics **or** SAdpt socket / HDMI path) — only visible under clocking | **Socket-swap test** (below); inspect Omnetics under magnifier | [[2026-06-26]], [[2026-06-27]] |
| b | **ALL channels railed ~10–12 mV pk-pk** (both mice together) | **Animal floats** — no animal-ground tie (missing GND electrode, or broken ground chain, or slip-ring green↔orange swap) | Tie a dura pin → tether green → busbar → C3410 `GND`; beep the chain; rebuild slip ring if swapped | [[2026-06-27]], [[signal-quality-and-grounding]] |
| c | **One/few channels railed**, others fine | **Open electrode contact** / unwired pad (bipolar open input floats to rail) | Confirm that channel is actually wired; reflow/repair its joint; deselect truly-unused pads | [[2026-06-27]], [[signal-quality-and-grounding]] |
| d | **Allego spams dozens of "notifications" full of code/garbage dates** | **allegoserver (Radiens backend) crashed** under heavy sensor-reload / channel-select churn; port 50051 refused | Restart Allego; re-set mode + electrodes + channel selection; daemon re-pairs automatically | [[signal-mapping-guide]] §10 |
| e | **Sample rate dropped to 1000** | A **mode switch reset it** | Set sample rate back to **30000** (do this every time you change mode) | [[first-headstage-connection]] §8 |
| f | **Every channel pure noise/hum, none mapped right** | Ground not connected **or** wrong channel selection (sites vs `D/n`) | Fix ground; select **sites 1–8** (not `D/1–D/8`) with custom map | [[signal-quality-and-grounding]], [[signal-mapping-guide]] |

---

## 2. Symptom A — port shows 0 channels / not detected

**Evidence to confirm:** `port_num_channels = {}` from the headless probe, and `priSigs=0` across all ports in `~/.local/state/radiens/logs/allegoserver.log`. Onboard GPIO (`GPIO-AIN/DIN/DOUT=2`) still enumerating = the XDAQ core is healthy and sweeping the bus; nothing is *answering*.

```bash
/opt/neurosurveillance/venv/bin/python -c "from radiens import AllegoClient; print(AllegoClient().get_status().port_num_channels)"
grep priSigs ~/.local/state/radiens/logs/allegoserver.log | tail
```

**Fix order:**

1. **Check the Allego mode FIRST.** Must be **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`). `SMARTBOX_PRO` shares the same USB3 backend so it *connects and scans*, but reports `priSigs=0` because the headstage profile is wrong. This was the **entire** root cause of the 2026-06-18 two-day teardown.

> [!warning] The mode silently reverts
> `XDAQ_ONE_REC` has flipped back to `SMARTBOX_PRO` after an Allego relaunch. **Re-verify the mode every launch** before suspecting hardware. Switching mode also resets sample rate → restore **30000**.

2. **Verify bus power** (rules out a power-rail fault): DMM at headstage VDD↔GND while streaming = **~3.57 V** ([[multimeter-guide]] §3a). Power has never been the fault here.

3. **Socket-swap test (decisive for a real SPI fault).** With mode confirmed and power good, if still `{}`:
   - Move the **undetected** headstage → the **other (known-good)** SPI socket of the SAdpt bridge; move a **working** headstage → the suspect socket.
   - **Fault follows the headstage** → the headstage is bad (vendor RMA — KC Kong / Kontex).
   - **Fault stays on the socket** → that SAdpt socket / HDMI path is bad.
   - Probe after each move with the command above; **re-check mode = `XDAQ_ONE_REC`** each relaunch.

4. **Inspect the SPI Omnetics** under a magnifier (bent/recessed/burned/oxidized signal pin), and beep adjacent pins for shorts ([[multimeter-guide]] §3d).

> [!note] What the DMM CAN'T settle here
> Bench DMM tests (VDD↔GND no short; adjacent SPI pins no short; pins visually straight) all came back clean on 2026-06-27 yet the headstage still didn't enumerate. A **signal-pin contact** fault only shows under live SPI clocking → the **socket-swap**, not the meter, is the decisive test. The analog side (slip ring / tether / electrode) is **downstream of the RHD chip → irrelevant to enumeration.**

---

## 3. Symptom B — all channels railed ~10–12 mV (animal floating)

**Signature:** ~all channels pegged at **10–12.6 mV pk-pk** (amp window is ±5 mV ≈ 10 mV pk-pk), **both mice rail together**, values wander between reads. This is the classic **floating-animal** fingerprint, not "bad electrodes."

**Cause:** the animal's body has **no DC tie to headstage GND**. Grounding the busbar/system is *not* enough — an **electrode must carry GND into the mouse.** Sub-causes:
- No dedicated animal-ground electrode at implant (the 2026-06-27 root cause).
- A **broken link** in the ground chain (cold joint, loose busbar screw).
- The **slip-ring green↔orange swap** sending tether green (ground) to a dead line ([[grounding-reference-noise-concepts]] §3).

**Fix:**
1. Assign a **spare dura-contacting skull pin** as animal ground → tether green → busbar → C3410 `GND`.
2. **Beep the whole chain** power-off, end-to-end, with a wiggle test ([[multimeter-guide]] §3b).
3. Confirm **`REF` empty** (bipolar).
4. If the slip ring is the green↔orange-swapped unit → **build a new slip ring** (resin-potted, not re-pinnable).
5. Stream **raw** → railing should collapse.

> [!example] Verified outcome (2026-06-27)
> After tying tether green → right-caudal dura pin: railing **collapsed**, a noise floor appeared, and native ch1 read **RMS 30 µV / pk-pk 178 µV / SNR 11.7** = a genuinely clean channel. The animal ground was the unlock.

---

## 4. Symptom C — one or a few channels railed, the rest fine

**Cause:** an **open input** — that channel's electrode isn't actually making contact, or the pad is **unwired**. On a bipolar RHD, an open/unconnected input floats to the rail (single-mouse rigs only wire a few pads; the rest legitimately float).

**Fix:**
- Confirm the channel is supposed to be wired. If it's an **unused pad**, that's expected — **deselect** it (it won't be recorded).
- If it *should* be a real electrode: reflow/repair its joint, check tether continuity, check the electrode-to-tissue contact.
- Don't judge until **raw** looks grounded, then apply bandpass + 60 Hz notch + Paired Reference — hum on open inputs dominates raw.

---

## 5. Symptom D — Allego spams notification stack dumps

**Signature:** dozens of "notifications" full of code/gibberish with random dates (1970, 5897…), often after rapid sensor reloads + channel select/deselect; port 50051 may refuse.

**Cause:** the **allegoserver (Radiens backend) crashed** and dumped its Go stack trace into the notification area. It is **software, not your hardware/wiring** — sensor files on disk are safe.

**Fix:** restart Allego, then re-set **Mode + Electrodes + channel selection** and Stream. The session daemon re-pairs automatically (fail-open, no phantom session). Avoid rapid-fire sensor reloads — apply once and let it settle. See [[signal-mapping-guide]] §10.

---

## 6. Symptom E — sample rate dropped to 1000

**Cause:** **switching the Allego system mode resets the sample rate to 1000.** Easy to miss right after fixing Symptom A.

**Fix:** set the sample rate back to **30000** (30 kHz) every time you change mode. Verify in the System tab beside the Mode dropdown.

---

## Appendix — SDK metrics shim (radiens 4.0.0 + NumPy 2.x)

`signal_metrics().get_metrics()` crashes with `module 'numpy' has no attribute 'NAN'`. Shim before calling:

```python
import numpy as np
if not hasattr(np, "NAN"): np.NAN = np.nan
from radiens import AllegoClient
sm = AllegoClient().signal_metrics().get_metrics(time_range=2.0, plot=False)
# sm.val shape (1, 32, 6): RMS, NOISE_UV, MAX_MIN_DIFF_ABS, SNR, EVENT_RATE, EVENT_MEAN
# MAX_MIN_DIFF_ABS ≈ 10–12 mV = a railed/saturated channel
```

> [!note] `HAL:cc22 "unable to send to listener"` log warnings
> These are MQTT stream-subscriber noise in `allegoserver.log` — **unrelated to SPI/detection.** Ignore them when diagnosing Symptom A.

---

## Related
- [[first-headstage-connection]] — full bring-up + the wrong-mode root cause (Symptom A)
- [[multimeter-guide]] — DMM tests (power, continuity, short, SPI pins) the fixes reference
- [[rig-assembly-guide]] — assembly order + pre-power checklist (prevents most of these)
- [[signal-quality-and-grounding]] — railing/floating signatures + grounding fix (Symptoms B/C)
- [[grounding-reference-noise-concepts]] — slip-ring green↔orange defect; ground vs reference vs noise
- [[signal-mapping-guide]] — channel selection + §10 allegoserver-crash case (Symptom D)
- [[radiens-software-reference]] — Allego mode, sample rate, referencing (manual p70)
- [[2026-06-26]] · [[2026-06-27]] — the bench sessions these cases come from
