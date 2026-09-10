---
name: flicker-discriminates-bend-from-break
description: Epoch-to-epoch variability of an open channel separates a bending/torsioned tether from a severed one, and it works on a file far too short to give a usable fraction.
metadata:
  type: reference
---

An open EEG/EMG channel says nothing about WHY it is open. **Epoch-to-epoch variability of the open
level does**, and it needs only ~20 four-second epochs — a file far too short for any usable
percentage (see [[weak-chip-ground-hides-as-electrode-failure]] for the other short-file rule).

Measured on `allego_1__uid0901-12-38-53`, 84 s, with every chip floor stable:

| | EEG rms variability | rms max/min | read |
|---|---|---|---|
| bending conductor | **80-150%** | **7-55×** | 🔧 torsion, recoverable by handling |
| severed conductor | **4-14%** | **1.1-1.8×** | ❌ continuous break, handling will NOT fix it |
| working channel | 11-18% | 1.6-2.1× | ✅ (distinguish by lf/hf above its own floor p99) |

🔑 **A conductor that bends in and out of contact MUST flicker. A severed one sits still.** Three
positions holding a fixed open level for 84 s on properly grounded chips are breaks, not bends.

⭐ **Two corroborating tells, both stronger than the channel on its own:**
- **Both roles switching in lockstep** = one cable bundle making and breaking (C2: EEG open → closed
  40 s → open, EMG tracking 1375 → 880 → 1363 µV).
- **The other role AND the chip floor jumping in the SAME epoch** = the tether BODY moved, never an
  electrode (C1: EEG 29→189 µV, EMG 99→567 µV, floor 2917→4476 µV, one epoch). Same rule that says
  an animal was unplugged rather than a channel failing — see [[w-sd-recovery-sleep-run-2026-08-27]].

⚠️ **A short file cannot rule out a SLOW intermittent.** A channel with a period of minutes looks
static in 84 s. Take 10 min before calling a break final.

🛑 The definitive test is mechanical, not statistical: record continuously while rotating and
straightening ONE tether at a time. Closes when straight, opens when twisted ⇒ torsion proven, and
the fix is a swivel or a shorter tether. Related: [[movement-dependent-contact-root-cause]].
