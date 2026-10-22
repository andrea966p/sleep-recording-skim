---
type: reference
area: eeg-rig
status: active
created: 2026-10-22
summary: "Epoch-to-epoch flicker of an open channel tells a bending tether from a severed one, on a file of about 20 epochs"
tags: [eeg, emg, tether, diagnosis, qc]
promoted-from: "Claude memory flicker-discriminates-bend-from-break"
---

# Flicker tells a bending tether from a severed one

> [!abstract] TL;DR
> An open EEG or EMG channel says nothing about WHY it is open. The epoch-to-epoch variability of the
> open level does, and it needs only about 20 four-second epochs: a file far too short for any usable
> percentage. **A conductor that bends in and out of contact must flicker. A severed one sits still.**
> Found on 2026-09-01 during a pre-flight screen ([[2026-09-01]], [[pre-flight-connection-screen]]).

## The numbers (2026-09-01, `allego_1__uid0901-12-38-53`, 84 s, every chip floor stable)

| | EEG rms variability | rms max/min | read |
|---|---|---|---|
| bending conductor | **80-150 %** | **7-55x** | torsion, recoverable by handling |
| severed conductor | **4-14 %** | **1.1-1.8x** | continuous break, handling will not fix it |
| working channel | 11-18 % | 1.6-2.1x | working; tell it apart by lf/hf above its own floor p99 |

Per position on that file (21 epochs): A1 150 % / 49x, C1 101 % / 7.3x, C2 80 % / 55x = flicker;
D1 13.6 % / 1.8x, B2 4.3 % / 1.1x, B1 4.0 % / 1.2x = static open; A2 11.1 % / 1.6x and D2 17.7 % / 2.1x =
working ([[2026-09-01]]).

Three positions holding a fixed open level for 84 s on properly grounded chips are breaks, not bends.

## Two corroborating tells, both stronger than the channel on its own

- **Both roles switching in lockstep** = one cable bundle making and breaking. C2: EEG open → closed for
  40 s → open, with the EMG tracking 1375 → 880 → 1363 µV while the chip floor did not move.
- **The other role AND the chip floor jumping in the same epoch** = the tether body moved, never an
  electrode. C1: EEG 29 → 189 µV, EMG 99 → 567 µV, floor 2917 → 4476 µV, in one epoch. The same rule says
  an animal was unplugged rather than a channel failing ([[2026-08-27-W-SD-recovery-sleep]]).

## Limits

- ⚠️ A short file cannot rule out a SLOW intermittent. A channel with a period of minutes looks static in
  84 s. Take 10 min before calling a break final.
- 🛑 The definitive test is mechanical, not statistical: record continuously while rotating and
  straightening ONE tether at a time. Closes when straight, opens when twisted ⇒ torsion proven, and
  the fix is a swivel or a shorter tether.

## Related
[[per-animal-failure-signatures]] (the four open-channel signatures) ·
[[weak-chip-ground-vs-open-electrode]] (check the chip floor first) ·
[[2026-08-04-movement-dependent-contact]] (contact flips within minutes)
