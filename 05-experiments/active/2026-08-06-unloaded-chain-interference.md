---
tags: [experiment, eeg, impedance, splitter, slip-ring, tether, interference, crosstalk, pre-registration]
created: 2026-08-06
status: active
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
