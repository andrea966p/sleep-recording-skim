---
type: experiment
area: rig-bringup
status: done
status-note: "active"
tags: [experiment, eeg, impedance, splitter, slip-ring, tether, interference, crosstalk, pre-registration]
created: 2026-08-06
---

# Does an unloaded tether + slip ring + headstage interfere with other animals?

> [!abstract] TL;DR
> When a mouse is removed but its tether, slip ring and headstage stay plugged into the rig,
> that dangling chain is still electrically live. Two questions follow. First, **what does the
> empty chain itself read**, because today it reported "connected" impedances 22% of the time
> with no animal on the end of it. Second, **does it disturb the animals sharing its splitter
> and port**, in impedance and in raw signal.
>
> This is the professor's question, written as a protocol before any data exists. It needs no
> anaesthesia and no surgery. Everything here is done at the rig end of the tether.

Origin: [[2026-08-06-fleet-duty-cycle-census]] §2b. Root cause context: [[2026-08-04-movement-dependent-contact]].
Files: `~/Downloads/impedance measurments/2026-08-06/`.

## 1. Why this is worth doing

The A2 position currently holds a **cut tether attached to nothing**, still wired through its
slip ring, headstage and the port A splitter. It was measured 20 times this morning by
accident and produced:

```
A/33   min 0.248 MOhm @ 1.3 deg     5/20 below 2 MOhm     1/20 below 0.5 MOhm
A/34   min 0.654 MOhm @ 3.5 deg     4/20 below 2 MOhm     0/20 below 0.5 MOhm
```

**Below 2 MOhm the empty chain is electrically indistinguishable from a real electrode**, in
magnitude and in phase: across the census, every reading below 2 MOhm sits at 0 or 180
degrees, which are the same resistive state, whether it came from an animal or from the empty
chain. The 30 to 150 degree band appears only above 5 MOhm.

Two mechanisms could produce this and they have opposite implications:

| mechanism | implication |
| --- | --- |
| **(a) leakage inside the chain** — slip-ring brushes, cut wire ends, flux residue, moisture | fixable, **and it contaminates every animal's readings too** |
| **(b) the amplifier's own floating-input behaviour** | not fixable, a permanent property of the instrument that we threshold around |

Nothing in the census separates them. Part A separates them.

## 2. Part A — what does the chain itself read? A teardown ladder

No animals involved. The A2 slot is dismantled one element at a time, and each configuration
is swept **15 times back to back**, about 8 minutes per rung at 31.4 s per 256-channel sweep.

| rung | configuration in the A2 splitter slot | isolates |
| --- | --- | --- |
| **A0** | **nothing plugged**, splitter slot empty | the instrument alone, mechanism (b) |
| **A1** | headstage only | the headstage |
| **A2** | headstage + slip ring | **the slip ring** |
| **A3** | headstage + slip ring + cut tether (**today's state**) | **the tether**, full chain |

> [!important] Read the ladder as differences, not as levels
> A0 is the floor. Any rung that lifts the fraction below 2 MOhm above A0 names the element
> that leaks. If A0 already reads 22%, the chain is innocent and the effect is the amplifier.

**Outcome per rung:** fraction of readings below 2 MOhm, fraction below 0.5 MOhm, median,
min and max |Z|, and the phase distribution.

### ✅ Part A RESULT, 2026-08-06. The ladder is flat and the chain is innocent.

| rung | configuration | \|Z\| < 2 MOhm | \|Z\| < 0.5 MOhm | best reading |
| --- | --- | --- | --- | --- |
| **A3** | tether + slip ring + headstage | 9/40 = **22.5%** | 1/40 | 0.248 MOhm |
| **A2** | slip ring + headstage, no tether | 8/30 = **26.7%** | 1/30 | 0.266 MOhm |
| **A1** | **headstage only** | 7/30 = **23.3%** | 1/30 | **0.107 MOhm** |
| **A0** | nothing plugged | **not measurable, see below** | | |

**Removing the tether changed nothing. Removing the slip ring changed nothing.** A bare
headstage with nothing attached to it still produced 0.107 MOhm, a value we would have read
as an outstanding electrode.

> [!warning] A0 as designed is degenerate
> Unplugging the headstage from the splitter does not leave an empty channel to measure, it
> **removes the channels**. Port A dropped from 64 to 32 amplifier channels and the total from
> 256 to 224; `A/33` and `A/34` ceased to exist. The instrument floor cannot be measured this
> way.

### ⭐⭐⭐ The real A0: unwired amplifier inputs, already in every sweep we own

Each mouse is wired to only **2 of its chip's 16 amplifier inputs** (pads 0-3 → `/1` and `/2`).
That leaves `/3` to `/16` and `/35` to `/48` as **real amplifier inputs with no wire attached**,
on every port, in every sweep ever taken. They are the instrument floor, free, with enormous n.

⚠️ `/17`-`/32` and `/49`-`/64` must be **excluded**: those are inactive slots, internally tied,
and they read ~0.051 MOhm essentially always (96.2% below 0.5 MOhm here). Including them would
destroy the control.

| control | n | < 2 MOhm | < 0.5 MOhm | min |
| --- | --- | --- | --- | --- |
| A2 cut tether, teardown ladder | 100 | **22.5%** | **3.0%** | 0.107 |
| **unwired amplifier inputs, all 4 ports, 20 sweeps** | **2240** | **21.4%** | **3.1%** | **0.051** |

> [!success] Two independent controls agree to within one percent
> A cut tether through a slip ring and a splitter, and a bare amplifier input with no cable
> at all, produce the **same false-positive rate**. The false positives are the **amplifier's
> own floating-input behaviour**, mechanism (b) of §1. **Mechanism (a) is excluded: our
> tethers, slip rings and splitters are not leaking.**

> [!danger] The unwired floor reached 0.051 MOhm
> That is the same value as the best electrode reading ever recorded on this rig. **A single
> low impedance reading, on its own, is not evidence of contact.** Only a duty cycle compared
> against this floor is.

### Recordable animals, scored against the 2240-sample floor at 0.5 MOhm

| animal | EEG | EMG | verdict |
| --- | --- | --- | --- |
| **B1, new mouse** | 6/20, **p = 3e-05** | 13/20, **p = 5e-15** | ✅ **RECORDABLE, both channels** |
| A1 | 1/20 n.s. | 14/20, **p = 1e-16** | EMG only, **cannot stage sleep** |
| D2 | 1/20 n.s. | 14/20, **p = 1e-16** | EMG only, **cannot stage sleep** |
| B2 | 0/20 n.s. | 0/20 n.s. | ❌ not recordable |
| C1 | 0/20 n.s. | 0/20 n.s. | ❌ not recordable |
| C2 | 1/20 n.s. | 2/20 n.s. | ❌ not recordable |
| D1 | 1/20 n.s. | 0/20 n.s. | ❌ not recordable |
| A2 | no mouse | no mouse | negative control |

**1 animal of 8 would yield scoreable sleep. 3 of 8 yield any signal at all.**

⚠️ Impedance predicts **class, not yield** — the 2 August run's pre-registered predictions came
out 4 correct, 3 wrong, 1 void. B1 being recordable is necessary, not sufficient.

> [!warning] Re-run `remap.py` after every rung
> `ntvChanIdx` is global. Unplugging a headstage can change how many channels a port
> enumerates, which silently shifts every downstream label. **Confirm the channel count and
> the map before each block**, or the files carry the wrong animal.

## 3. Part B — does the chain disturb its neighbours?

### 3.1 Reference animal

**B1, the new mouse.** It is the only animal on the rig with a stable channel pair: 20/20 and
20/20 with **zero flips** this morning. Every other animal flips too much to detect a change
against.

> [!note] B1 is at the ceiling, so this is a harm detector
> A ceiling channel cannot show improvement, only damage. **Damage is exactly the question
> the professor asked**, so the ceiling is the right property here, the same logic that makes
> D2's EMG the harm detector in [[2026-08-05-tether-comparison]].

### 3.2 Manipulation

Move the **unloaded chain onto B1's splitter**, on port B, and alternate it in and out.
B2's headstage is unplugged at the **splitter end** for the duration, so that the slot is free
and B2 contributes nothing. The tether stays on B2's head. **No anaesthesia, no handling of
any animal.**

| block | port B splitter slot 2 | sweeps |
| --- | --- | --- |
| **OFF-1** | empty | 15 |
| **ON-1** | unloaded chain plugged in | 15 |
| **OFF-2** | empty | 15 |
| **ON-2** | unloaded chain plugged in | 15 |

ABAB, because a single AB cannot separate the manipulation from drift across the session.
About 45 minutes total including the plug changes.

### 3.3 Outcomes, fixed before any data

**Impedance**, on `B/1` and `B/2`:

| metric | definition |
| --- | --- |
| **duty cycle** | fraction of the 15 sweeps below **0.5 MOhm**. Primary outcome. |
| duty cycle at 2 MOhm | reported alongside, for comparability with earlier blocks |
| median, min, max \|Z\| | the distribution, not just the threshold crossings |
| flip count | transitions across consecutive sweeps |

**Signal**, one 60 s raw capture per block via `AllegoClient.get_signals()`:

| metric | why |
| --- | --- |
| **rms µV** | the connected / floating / inactive signature table in [[eeg-rig-current-state]] |
| **60 Hz amplitude** | hum is a direct readout of contact quality on this rig |
| band powers 0.5-4, 4-9, 9-20, 20-50, 50-300 Hz | spectrum shape, catches a change that rms hides |
| **cross-correlation between the chain's channels and `B/1`, `B/2`** | **this is crosstalk, measured directly rather than inferred** |

Comparison: pooled ON against pooled OFF, Fisher exact on connected counts for impedance,
and a paired comparison of the signal metrics across the four blocks.

## 4. Pre-registered predictions

| if | then |
| --- | --- |
| the chain is **inert** | B1 stays 15/15 in all four blocks, no rms or 60 Hz change, no cross-correlation above the OFF-block floor. **The professor's question is answered "no interference" with data.** |
| the chain **injects noise** | 60 Hz and rms rise in the ON blocks on `B/1` and `B/2`, and the chain's channels correlate with B1's |
| the chain **loads the shared bus** | B1's duty cycle falls in the ON blocks, with or without a signal change |
| **nothing is separable** | B1 has left the ceiling and drifted. Abort and re-baseline; the test needs a stable reference. |

## 5. What this does and does not settle

- ✅ Settles whether a dangling chain harms its neighbours, in impedance and in signal.
- ✅ Settles where the empty chain's own false-positive readings come from.
- ❌ Does **not** re-open the splitter question in general. The splitter was excluded on
  2026-08-04, and the census adds two more free observations against it: **B1 is 20/20 while
  sharing its splitter with B2, which is completely open**, and **A1's EMG is 70% below
  0.5 MOhm while sharing its splitter with this very chain.**
- ❌ n = 1 reference animal. A null here is a null for B1, on one morning.

> [!danger] Rejected design: moving A1 and B1 onto the same splitter
> It changes **port and splitter partner simultaneously**, provides no repeat measure, and
> puts a ceiling channel where it can only lose. It cannot attribute any change to the
> splitter. The within-animal ABAB above answers the same question with a reversible,
> free manipulation.

## 6. Scheduling against the D2 tether swap

Part A costs 35 minutes and no animal contact, so it can run at any time.

⚠️ **Part B and the D2 long-tether swap both change what is plugged into the rig.** Do not
interleave them. Run one to completion, re-run `remap.py`, then start the other. The D2 swap
is the pre-registered priority for this afternoon; Part B is a good use of the time while D2
settles, provided port B is left alone by the swap.
