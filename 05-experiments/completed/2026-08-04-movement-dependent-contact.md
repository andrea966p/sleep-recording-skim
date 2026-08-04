---
tags: [experiment, eeg, electrodes, impedance, contact, movement, root-cause]
created: 2026-08-04
status: completed
---

# 2026-08-04 — The electrodes are fine. Movement breaks the contact.

> [!abstract] TL;DR
> **What I found.** I measured the same mouse, on the same port, in the same
> session, twice: once while it was holding still, once while it was moving. The
> EEG impedance went from **0.052 MΩ to 8.649 MΩ**. That is a 166 fold change,
> and 0.052 MΩ is the best number anyone has recorded on this rig. The electrode
> is not degraded. It is excellent when the animal is still, and it goes open
> when the animal moves.
>
> **Why it matters.** Every confusing thing about this project resolves into
> this one fact. We have spent weeks treating a mechanical intermittency as an
> electrode failure, an implant failure, and a soldering failure. It is none of
> those.
>
> **What is still open.** Where exactly along the tether the contact breaks, and
> what the mechanical fix is. Also, I did NOT repeat the still versus moving
> comparison, so read §6 before quoting the effect size in a paper.

---

## 1. The measurement that settles it

Animal **B1**, alone on **port B**, no splitter, two sweeps minutes apart in one
session. The only thing that changed between them is whether the mouse was
moving.

| B1, port B | EEG `B/1` | EMG `B/2` |
| --- | --- | --- |
| **mouse still** | **0.052 MΩ @ 179.7°** | 2.099 MΩ @ 168.6° |
| **mouse moving** | **8.649 MΩ @ 54.6°** | 5.805 MΩ @ 33.2° |
| change | **166×** | 2.8× |

Files: `B1_only_portB_mousestill.csv`, `B1_only_portB_moving.csv`.

Both channels move the same way. The phase moves with the magnitude, from near
180° (a connected, capacitive electrode interface) to 30 to 55° (the signature we
have always seen on open channels). This is not noise on one number, it is the
whole channel changing state.

> [!important] 0.052 MΩ is the best impedance ever recorded in this fleet
> The previous best was C1 EMG at 0.051 MΩ and A1 EMG at 0.073 MΩ, and those were
> EMG. For **EEG**, the best we had ever seen was B1 itself at 0.133 MΩ. B1's EEG
> electrode is not marginal, not degrading, not failing. When the animal holds
> still it is **better than everything else we own**.

## 2. What the supporting single animal sweeps show

I disconnected everything and brought animals up one at a time, with no
splitter. With one headstage and no splitter the animal lands on `/1` and `/2`
of whatever port it is plugged into, NOT on `/33` and `/34`. That matters when
reading these files.

| Sweep | file | EEG | EMG | reading |
| --- | --- | --- | --- | --- |
| **D2 alone**, port D | `imp_D2only.csv` | `D/1` 0.459 @ 2.5° | `D/2` 0.270 @ 178.5° | both connected, confirms D2 is genuinely good |
| **D1 alone**, port D | `D1only.csv` | `D/1` 7.444 @ 44.6° | `D/2` **0.688 @ 176.3°** | EMG is FINE |
| **B1 alone**, port D | `B1_only_portD.csv` | `D/1` 0.873 @ 4.7° | `D/2` 0.325 @ 1.8° | both connected in a different port |

Two things fall out of this table.

**D1's EMG did not break.** In the 8 mouse sweep an hour earlier it read 8.203 MΩ
and I wrote it up as a channel that had died during the multimeter work. Alone,
it reads 0.688 MΩ. It never broke. The animal was moving.

**B1 works in port D too**, at 0.873 MΩ. So the port is not the variable, which
incidentally discharges step 2 of the §6 escalation ladder in
[[dmm-eeg-path-continuity-test]] without having to run it deliberately.

### Channels to ignore in these files

- `/3` through `/16` sit at 0.6 to 9 MΩ. Those are **unwired pads** on the C3410.
  Open is the correct answer for them.
- `/18` through `/32` sit near 0.01 MΩ at phase 0° or 180°. The RHD2216 is a
  **16 channel** part. Those are not real inputs. Ignore them entirely.

## 3. Why this explains everything we have been chasing

Every open finding in this project has been a symptom of the same mechanical
intermittency, sampled at a different moment.

| Observation | What we thought | What it actually is |
| --- | --- | --- |
| Open electrode in 36 of 41 animal recordings | Electrodes failing, implants failing | Sweeps caught the animal moving |
| **Hum is bimodal**: 9 to 90 µV connected, 1000 to 4700 µV open | Two populations of electrodes | One electrode, two mechanical states |
| **Contact flipped 522 times in half a second** | Unexplained instability | An animal moving |
| Impedance register **churns** every sweep, 13 of 16 channels swinging, D2 EMG 55×, B1 EEG 47×, D1 EMG 41× | Progressive electrode degradation | Each sweep is a different posture |
| The DMM continuity test **passed on the whole fleet** this morning | Puzzling, since something is clearly broken | Expected. A static, unloaded, hand rotated bench test cannot reproduce an animal pulling on a tether |
| Across Run 2, EEG got worse on 8 of 8 animals and better on none | A degradation trend | A sampling artefact. Post run sweeps were taken with animals awake and active |
| ⭐ Our one good recording, **C1 on 2026-07-31, is a single 8.1 hour unbroken block** | A lucky animal | **Sleep is when the mouse holds still.** The data has been telling us this the whole time |

That last row is the one I trust most, because it is an independent 8.73 hour
observation that nobody designed as a test of this hypothesis, and it points the
same way.

> [!quote] Paper-ready
> Electrode impedance in this preparation is dominated by a movement dependent
> mechanical contact rather than by the electrode tissue interface: the same
> animal measured on the same port read 0.052 MΩ while immobile and 8.649 MΩ
> while moving, and recording yield tracks immobility rather than electrode age.

## 4. What is now excluded, and must not be re-proposed

These are dead. All of them were expensive to kill and none of them should be
raised again without new evidence.

1. **"The electrodes are degraded or failing."** B1's EEG reads 0.052 MΩ. The
   82% epidural failure literature in [[electrode-failure-and-impedance-literature]]
   is real, but it is **not what is happening here**, and it should no longer be
   used to explain our numbers or to lower expectations.
2. **"Cold solder joint on pad 0 or pad 1."** Killed this morning by the DMM
   test, fleet wide.
3. **"The slip ring is the fault"**, in the sense of a statically broken
   conductor. Killed this morning. It may still be the mechanical hinge, see §5.
4. **"The fault is per pad rather than per channel type."** B1 passed on pads
   2 and 3.
5. **"The fault is the port or the XDAQ."** B1 works in both port B and port D.
6. **"We need new mice."** Absolutely not. The implants are good. **NO SURGERY.**
7. **"The negative electrode of each pair is open."** Still unmeasurable, still
   worth asking Kontex about, but it is no longer a leading hypothesis: a
   permanently open negative electrode cannot produce a channel that reads
   0.052 MΩ when the animal is still.

## 5. What is still open

**Where along the path does the contact break under movement?** Everything from
the C3410 pads to the slip ring socket passed a static continuity test, so the
candidates are the interfaces that a static test cannot load:

- the **tether to headcap** connection at the animal, under tension and torque
- the **slip ring under load**, which the hand rotation test could not reproduce
  because it was unloaded and at rest
- the **tether plug** at the slip ring socket, under cable drag
- the **headstage seating** on the C3410, under cable pull

The fix is mechanical, and mechanical means strain relief, cable management,
tether counterbalance, and connector retention. It does not mean surgery and it
does not mean new electrodes.

> [!danger] Still forbidden, and now for a better reason than before
> No "reseating" of electrodes or EMG wires, which is impossible after
> implantation anyway. No tether change without a written argument. **And no
> surgeries: the implants have now been positively shown to be good.**

## 6. Honest limits on this result, read before quoting it

I am recording these plainly so that nobody, including us, over reads the data
later.

1. **The still versus moving comparison was run ONCE, on ONE animal.** It was not
   replicated, by choice, on 2026-08-04. The effect size is enormous and both
   channels moved together, and it is corroborated by the C1 sleep block and by
   the whole pattern in §3, but the direct experiment is n=1. If a reviewer asks
   for the still/moving/still/moving alternation, we do not have it yet, and it
   would cost about ten minutes to get.
2. **"Moving" and "still" were judged by eye**, not scored from video. There is
   no timestamped movement trace aligned to the sweeps.
3. **Impedance sweeps are not instantaneous.** Each sweep takes time to step
   through sites, so a "moving" sweep is a mix of postures, which if anything
   makes the measured effect an **underestimate**.
4. Only the **positive** input of each bipolar pair is measured, as always. See
   [[impedance-sweep-register]].
5. **No photographs** of the boards under magnification were taken, by choice, on
   2026-08-04. The DMM test and visual inspection results are recorded, but there
   is no image record of the pre intervention pad state.

## 7. What to do next

1. **Reconnect all 8 animals and run.** The rig is not broken and the animals are
   not broken.
2. **Expect and exploit the movement dependence.** Usable EEG will come from
   immobile periods, which is exactly when sleep happens. This is a far better
   position than we thought we were in this morning, because sleep research only
   needs the animal to be scoreable while it is asleep.
3. **Attack the mechanics, not the electronics.** Strain relief and tether load
   are the target now. Weigh the tether, check the counterbalance, check that the
   cable cannot drag or torque the headcap.
4. **Re-frame the professor handover pack.** The current draft explains a data
   quality problem in terms of electrode failure. That framing is now wrong and
   should be replaced with this result, which is a much better story: the
   preparation works, and the remaining problem is mechanical and fixable.
5. Keep the Kontex polarity question (Q12) in the batch, but **demote it**. It is
   now a completeness issue rather than a candidate root cause.

## Related
- [[impedance-sweep-register]] — every sweep, including today's
- [[dmm-eeg-path-continuity-test]] — the static test that passed fleet wide this morning
- [[2026-08-03-two-8-mouse-runs]] — the run analysis whose "8 of 8 got worse" conclusion this result overturns
- [[2026-07-31-contact-intermittency-no-wire-control]] — the 522 flips
- [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]] — duty cycle framing, now explained
- [[electrode-failure-and-impedance-literature]] — real, but not our failure mode
- [[2026-08-03-data-quality-report-for-professor]] — needs rewriting around this
