---
tags: [experiment, eeg, electrodes, impedance, contact, intermittency]
created: 2026-08-04
status: completed
---

# 2026-08-04 — The electrodes are good. The contact is intermittent. The trigger is unknown.

> [!abstract] TL;DR
> **The good news, and it is big.** One EEG channel measured **0.052 MΩ** today,
> the best value ever recorded on this rig and inside the range published in the
> literature. Mouse **D2** recovered completely from fully open and stayed clean
> in every sweep. **The electrodes and the implants are good. No surgery is
> warranted.**
>
> **The problem, restated correctly.** The contact is **intermittent**. B1's EEG
> read 6.236, then 0.052, then 8.649, then 0.177 MΩ across 23 minutes. So a single
> impedance sweep cannot tell us whether an electrode is good. It only reports the
> state of a contact at that instant, and that state changes within minutes.
>
> **What I got wrong today, and corrected the same day.** I proposed that movement
> causes the loss of contact, on the strength of one still versus moving pair. I
> then tested it and **it failed**. Movement is not established as the trigger.
> The trigger is still unknown.
>
> **What is still open.** What flips the contact, and whether the slip ring is
> involved. §7 has the plan.

---

## 1. The session, in order

Seven sweeps in 23 minutes, all in
`~/Downloads/impedance measurments/2026-08-04/`. Full register with file names:
[[impedance-sweep-register]].

| # | time | configuration | why I ran it |
| --- | --- | --- | --- |
| 1 | 16:33 | 8 mice, 64 ch/port | first sweep after the DMM test and a full restart |
| 2 | 16:40 | D2 alone, port D | is D2's recovery real |
| 3 | 16:42 | D1 alone, port D | did D1's EMG really die |
| 4 | 16:44 | B1 alone, **port D** | port swap control |
| 5 | 16:47 | B1 alone, port B, **MOUSE STILL** | ⭐ the best measurement of the day |
| 6 | 16:48 | B1 alone, port B, **MOUSE MOVING** | generated the movement hypothesis |
| 7 | 16:56 | 8 mice, **B1 B2 C1 moving, five still** | ⚠️ the test of that hypothesis |

Preceding all of this: the DMM continuity test passed on the whole fleet
([[dmm-eeg-path-continuity-test]]), so the boards, pads, solder joints and the
statically rotated slip ring were already clean before any of these sweeps.

## 2. ⭐ The result that matters most: the electrodes are good

**Sweep 5. B1 alone on port B, mouse holding still: EEG `B/1` = 0.052 MΩ @ 179.7°.**

That is the **best impedance ever recorded on this rig**, EEG or EMG. The previous
best were C1 EMG at 0.051 MΩ and A1 EMG at 0.073 MΩ, both EMG; the best EEG we had
ever seen was B1 itself at 0.133 MΩ. 0.052 MΩ sits inside the 10 to 50 kΩ band
reported for epidural electrodes in [[electrode-failure-and-impedance-literature]].

**A degraded, failed or badly implanted electrode cannot produce that number.**

**Mouse D2 says the same thing independently.** It read 9.200 MΩ, fully open, after
Run 2. Today it was connected on **both** channels in **every** sweep:

| D2 | sweep 1 (16:33) | sweep 2 (16:40, alone) | sweep 7 (16:56) |
| --- | --- | --- | --- |
| EEG | 0.352 | 0.459 | 0.400 |
| EMG | 0.233 | 0.270 | 0.088 |

D2 is the only animal that managed that, and it was streaming a clean signal.
**Channels that read open recover completely.** Whatever is wrong is not
destructive and not permanent.

> [!danger] Therefore: NO SURGERY, and the reason is now positive
> Previous versions of this argument said "do not operate, we have not excluded
> the cheap explanations yet". That is no longer the argument. **We have positive
> evidence that the implants work**, from two independent animals. Do not schedule
> surgeries, and do not use the 82% epidural failure literature to explain our
> numbers.

## 3. The problem, stated correctly: fast reversible intermittency

**B1's EEG channel, one afternoon, 23 minutes:**

| 16:33 | 16:47 | 16:48 | 16:56 |
| --- | --- | --- | --- |
| 6.236 (8 mice) | **0.052** (alone, still) | 8.649 (alone, moving) | **0.177** (8 mice, moving) |

**166× spread, four values, one electrode.** No fixed property of an electrode can
produce this.

**D1's EMG makes the same point.** It read 8.203 MΩ in sweep 1 and I logged it as a
control channel that had died during the multimeter work. Nine minutes later, alone,
it read **0.688 MΩ**. It never died.

Consequences:

1. **A single sweep cannot rank, screen or classify a channel.** It is a 20 second
   snapshot of something that changes within minutes.
2. **Comparing sweeps across days compares two moments, not two conditions.** This
   kills the "EEG got worse on 8 of 8 animals across Run 2" trend in
   [[2026-08-03-two-8-mouse-runs]]: that was sampling, not degradation.
3. **The contact recovers on its own.** Loss is not cumulative.

## 4. The movement hypothesis, and why it failed

### What suggested it

Sweeps 5 and 6, one minute apart, same animal, same port, only the animal's
behaviour differing:

| B1, port B | EEG `B/1` | EMG `B/2` |
| --- | --- | --- |
| **mouse still** (16:47) | **0.052 MΩ @ 179.7°** | 2.099 @ 168.6° |
| **mouse moving** (16:48) | **8.649 MΩ @ 54.6°** | 5.805 @ 33.2° |

Both channels moved together and the phase tracked the magnitude, from near 180°
(connected, capacitive) to 30 to 55° (the open signature). It looked decisive.

### The test, prediction registered first

Sweep 7. 8 mice, **B1, B2 and C1 moving**, **A1, A2, C2, D1 and D2 still**.
Prediction: movers open, still animals connected.

| animal | state | EEG | EMG |
| --- | --- | --- | --- |
| B1 | **MOVED** | **0.177 CONNECTED** | 8.693 open |
| B2 | **MOVED** | 5.406 open | 7.765 open |
| C1 | **MOVED** | **0.584 CONNECTED** | **0.644 CONNECTED** |
| A1 | still | 5.989 open | **0.327 CONNECTED** |
| A2 | still | 6.221 open | 3.639 open |
| C2 | still | **0.411 CONNECTED** | **0.122 CONNECTED** |
| D1 | still | 4.926 open | 5.557 open |
| D2 | still | **0.400 CONNECTED** | **0.088 CONNECTED** |

**Moved: 3 of 6 connected. Still: 5 of 10 connected. 50% against 50%.**

### Reading this honestly, in both directions

**The group comparison is weak evidence.** It is unpaired, three animals against
five, each with its own baseline propensity, at a ~50% base rate. That design has
very little power and its null does not refute much.

**What actually damages the hypothesis is B1 contradicting itself.** B1 read
8.649 MΩ moving in sweep 6 and **0.177 MΩ connected while moving** in sweep 7. Same
animal, same stated condition, opposite result, nine minutes apart. That is a
within animal contradiction and no argument about pairing rescues it.

**And animals that were definitely still went open**: A2 on both channels, D1 on
both. Whatever flips the contact is not gated on gross movement.

> [!important] A sweep takes about 20 seconds
> Measured at the bench today. So the animal's state held for the whole
> measurement, and the failed replication **cannot** be explained away as a sweep
> averaging over mixed postures. An earlier draft of this page claimed it could.
> That was wrong and is retracted.

**Status: movement is a plausible contributor, not an established cause.** The way
to settle it is a paired design run properly, alternating still and moving on the
same animal several times. See §7.

## 5. What the other sweeps established

**Sweep 4, B1 alone in port D:** `D/1` 0.873, `D/2` 0.325. B1 works in a port other
than its own, so **the port, the splitter and the XDAQ path are not the variable**.
This discharges step 2 of the §6 escalation ladder in
[[dmm-eeg-path-continuity-test]] without having to run it deliberately.

**Sweep 2, D2 alone:** confirms D2's recovery is real and not a splitter artefact.

### Channels to ignore when reading the single animal files

With one headstage and no splitter an animal lands on `/1` and `/2` of its port,
**not** `/33` and `/34`.

- `/3` through `/16`: 0.6 to 9 MΩ. **Unwired pads** on the C3410. Open is correct.
- `/18` through `/32`: near 0.01 MΩ. The RHD2216 is a **16 channel** part. Not real
  inputs.

## 6. Where this leaves each hypothesis

| Hypothesis | Status |
| --- | --- |
| Electrodes degraded or failing | ☠️ **DEAD.** 0.052 MΩ, and D2 fully recovered |
| Implant failure, "make new mice" | ☠️ **DEAD.** Positive evidence the implants work |
| Cold solder joint on pad 0 or 1 | ☠️ **DEAD.** DMM test, fleet wide |
| Solder bridge or leakage on the board | ☠️ **DEAD.** Inspected fleet wide, no cross contamination |
| Fault is per pad, not per channel type | ☠️ **DEAD.** B1 passed on pads 2/3 |
| Port, splitter or XDAQ | ☠️ **DEAD.** B1 works in port B and port D |
| Slip ring, as a statically broken conductor | ☠️ **DEAD.** 360° rotation clean, fleet wide |
| **Slip ring, under load or in motion** | ❓ **OPEN.** Never tested under load. Next test |
| **Tether construction** (thin heatshrink joints) | ❓ **OPEN.** Rebuild planned |
| **Implantation depth**, pin marginally on the dura | ❓ **OPEN.** See caution below |
| **Movement as the trigger** | ⚠️ **TESTED AND NOT CONFIRMED** |
| Room electrical interference | ❓ **OPEN.** Room stripped today, see §8 |

> [!warning] On the implantation depth idea
> A pin resting marginally on the dura, making and breaking with sub millimetre
> motion, is consistent with everything here, including flips while the animal is
> still, since breathing and pulsation never stop. **But note two things.** First,
> depth alone cannot explain a channel that reaches 0.052 MΩ, so it would have to
> be the marginal contact version, not simple "too shallow". Second, **it cannot
> help the current cohort** — you cannot re lower an implanted pin — so it is a
> protocol change for a future surgery batch and it does not unblock the animals
> we have. Decide it after the tests in §7, not before.

## 7. Next tests

### 1. Sweep loop, planned for 2026-08-05

**Repeated sweeps every ~30 s for 20 minutes on one animal**, logged with time, to
measure the **flip rate** rather than a single state. Radiens has a Python API. This
is the instrument every remaining question needs, because:

- At a ~50% base rate, **one sweep reading "good" proves nothing.** Comparisons
  must be between duty cycles, not between single readings.
- It converts the movement question from eyeballed labels into a time series that
  can be scored against behaviour afterwards.

### 2. Direct connection, bypassing the slip ring

Custom long tether from the animal straight to the adapter board and headstage.
Removes the largest untested mechanical element.

> [!warning] Two traps in this test
> **You would change two variables at once.** A new custom tether removes the slip
> ring *and* replaces the tether and its joints. If the problem disappears you will
> not know which change did it. If possible, bypass the slip ring using the
> existing tether, or run the new tether through the existing slip ring first.
>
> **One clean sweep proves nothing**, for the reason in §7.1. Compare flip rates
> over 20 minutes, not single readings.

### 3. Tether rebuild, soldered joints and resin

Replaces the thin heatshrink joints.

> [!note] Leave a flexible section
> Soldered joints potted in resin are stiff, and stiff joints concentrate strain at
> the edge of the resin. Keep a deliberate flexible length between the resin and
> the headcap, or the break point may move rather than disappear.

### 4. Housekeeping

- Re-frame [[2026-08-03-data-quality-report-for-professor]]. The copy already sent
  to the PI does not carry today's findings.
- Keep the Kontex polarity question (Q12) in the batch but **demote it**. A channel
  reading 0.052 MΩ cannot have a permanently open negative electrode.

## 8. Recording room stripped, 2026-08-04

To rule out electrical interference, the room was reduced to essentials. Remaining
on the rack: the **wifi router** with the wall ethernet, the **ASUS PC**, the
**XDAQ**, and the **white noise generator** with its two small jack speakers.

⚠️ **The Raspberry Pis and all cameras were removed, so NO VIDEO IS BEING
RECORDED** until they go back. This blocks any behaviour scoring against the sweep
loop, so the two need sequencing: either accept eyeball labels tomorrow, or put one
camera back first.

## 9. Honest limits on everything above

1. **The still versus moving pair is n=1 and was not replicated**; the one attempt
   to reproduce it failed, and the same animal contradicted it.
2. **"Still" and "moving" were judged by eye**, not scored from video. The labels in
   the file names are the experimenter's note, not an instrument reading.
3. **No photographs** of the boards under magnification were taken, by choice. There
   is no image record of the pre intervention pad state.
4. Only the **positive** input of each bipolar pair is ever measured. See
   [[impedance-sweep-register]].
5. The 8 mouse sweeps run through **splitters**; the single animal sweeps do not.
   Cross configuration comparisons carry that difference.

> [!quote] Paper-ready
> Electrode impedance in this preparation is dominated by an intermittent
> mechanical contact rather than by the electrode tissue interface: the same
> channel measured 0.052 MΩ and 8.649 MΩ within a single afternoon, and fully open
> channels recovered spontaneously, so individual impedance sweeps were treated as
> instantaneous contact state rather than as a measure of electrode condition.

## Related
- [[impedance-sweep-register]] — every sweep, the file names, and the session timeline
- [[dmm-eeg-path-continuity-test]] — the static bench test, **CLOSED, passed fleet wide**
- [[2026-08-03-two-8-mouse-runs]] — its "8 of 8 got worse" conclusion is overturned here
- [[2026-07-31-contact-intermittency-no-wire-control]] — the 522 flips, now in context
- [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]] — duty cycle framing
- [[electrode-failure-and-impedance-literature]] — real, but not our failure mode
- [[2026-08-03-data-quality-report-for-professor]] — needs re-framing
