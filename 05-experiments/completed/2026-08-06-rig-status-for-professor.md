---
tags: [status, eeg, impedance, duty-cycle, report, professor]
created: 2026-08-06
status: complete
---

# Rig status, 6 August 2026, morning: what the rig can do and what it is actually doing

> [!abstract] TL;DR
> The rig can physically carry 8 mice and that part is finished and working. What it cannot
> do is keep them electrically connected. This morning I measured every animal 20 times in a
> row and only **1 animal of 8 has a genuinely working EEG and EMG pair**.
>
> Two things happened today that change how we should read all of our impedance numbers.
> First, one slot on the rig turned out to hold **no mouse at all**, just a cut cable, and it
> reported "connected" impedances 22% of the time. That gave us our first ever negative
> control and it tells us our old pass mark was too generous. Second, a mouse that recovered
> for **16 days before being tethered** is the only animal on the rig with a perfectly stable
> signal: 40 out of 40 measurements connected, zero dropouts.
>
> Still open: we cannot yet say whether that mouse is good because of the longer recovery or
> because of its new tether, because it got both at once.

Detail and statistics: [[2026-08-06-fleet-duty-cycle-census]]
Yesterday's tether experiment: [[2026-08-05-tether-comparison]]
Root cause work: [[2026-08-04-movement-dependent-contact]]
Planned next test: [[2026-08-06-unloaded-chain-interference]]

## 1. Can the rig record 8 mice at the same time?

**Yes on capacity, and capacity is not our problem.**

Four ports, each with a C3442 splitter carrying two animals, gives 8 mice and **256 amplifier
channels**. I enumerated all 256 this morning and every one returned a measurement. That is
exactly the hard ceiling of the XDAQ Core, which supports 8 headstages and no more, so the
rig is sitting precisely at its design limit with nothing wasted.

**No on yield.** The limiting factor is electrical contact between the implanted electrode and
the amplifier, which is the same bottleneck we identified on 4 August. Averaged over 20
measurements, **1.8 of 8 animals** had both channels connected at any given moment, and once
the numbers are corrected against the negative control described below, the honest figure is
**1 animal of 8**.

## 2. How we measure this now, and why it changed

An impedance reading tells us whether an electrode is electrically connected. On 4 August we
found that this connection **switches on and off within minutes** in the same animal without
anything being touched, so a single reading is close to a coin toss and cannot be used to
judge a channel.

Since then we measure a **duty cycle** instead: fire the same measurement 20 or 40 times in a
row and count the fraction that come back connected. One measurement of all 256 channels
takes **31.4 seconds**, and the whole process is now automated, so a 20-measurement block
costs 10 minutes of unattended time.

> [!success] The method proved itself today
> Mouse D2 was measured yesterday and again today, 24 hours apart, through a hardware change
> in between. Its EEG duty cycle was **27.5% yesterday and 30% today**, and its EMG was
> **97.5% and 100%**. So a duty cycle is a **stable, repeatable property of a channel**, not
> noise. This is what makes the comparisons below meaningful.

## 3. 🔴 The most important finding: our pass mark was too generous

The A2 position on the rig holds **a cut cable attached to nothing**. There is no mouse. The
cable is still wired through its rotating connector (slip ring), its amplifier board
(headstage) and the shared splitter into the recording system, so it was measured 20 times
this morning alongside the real animals, entirely by accident.

**It should have read disconnected every single time. It did not.**

```
22% of the readings from a cable attached to NOTHING came back below our
2 MOhm "connected" threshold, with a best reading of 0.248 MOhm.
```

This is the first negative control this project has ever had, and it is bad news that we
badly needed. It means **any channel scoring between 15% and 35% is statistically
indistinguishable from a cable attached to nothing.**

> [!important] The fix, which costs nothing
> Tightening the pass mark from **2 MOhm to 0.5 MOhm** drops the false-positive rate from
> **22% to 2.5%**, one reading in forty, while genuinely connected channels still score 30 to
> 70 percent. We have adopted 0.5 MOhm going forward, and the empty cable now stays plugged
> in permanently as a free control, because every measurement reads all ports at once.

⚠️ **This does not overturn yesterday's tether result.** Yesterday's improved channel scored
20 out of 20 against this 22% background, which is still overwhelming. What it does mean is
that the *before* condition was partly false positives, so **the improvement we measured
yesterday is larger than we reported, not smaller.**

## 4. Where every animal actually stands

Scored at the corrected 0.5 MOhm pass mark, against the empty-cable control. "Significant"
means the channel is statistically distinguishable from a cable attached to nothing.

| animal | EEG | EMG | verdict |
| --- | --- | --- | --- |
| **B1, the new mouse** | 30%, **p = 0.004** | 65%, **p = 1.8e-07** | **the only animal with a working pair** |
| A1 | 5%, not significant | 70%, **p = 2.9e-08** | EMG excellent, EEG absent |
| D2 | 5%, not significant | 70%, **p = 2.9e-08** | EMG excellent, EEG absent |
| B2 | 0% | 0% | nothing |
| C1 | 0% | 0% | nothing |
| C2 | 5%, not significant | 10%, not significant | nothing |
| D1 | 5%, not significant | 0% | nothing |
| A2 | no mouse | no mouse | negative control |

**Four channels out of fourteen beat an empty cable.** One animal has both.

> [!warning] Single measurements are actively misleading, and this is the proof
> Mouse C1 looked healthy in a one-off measurement this morning, 0.155 MOhm on its EMG. Over
> 20 consecutive measurements it scored **0 out of 20** on both channels and changed state 9
> and 6 times. If we had judged it on one reading we would have called it a good animal.

## 5. ⭐ The new mouse, and the one number that might matter most

A mouse implanted on 21 July with the rest of the group was left in its home cage and
**never tethered until this morning, 16 days after surgery**. It was then connected to the
new soldered and resin-sealed 19.5 cm tether we built yesterday.

It scored **40 out of 40 measurements connected, on both channels, with zero dropouts.** It
is the only animal on the rig with a stable EEG. Its worst reading in the entire block was
1.531 MOhm, where every other animal swings up to 8 or 9 MOhm.

For comparison, the other seven animals were tethered on 30 July, which is **8 to 10 days
after surgery**. Our own written protocol requires **at least 14 days**. So this is the first
animal in the project ever tethered according to our own protocol, and it is the best animal
we have ever had.

> [!danger] Two things changed at once, so we cannot claim either yet
> The new mouse differs from the others in **recovery time (16 days versus 8 to 10)** and in
> **tether construction (soldered and resin-sealed versus thin heat-shrink)**. With one animal
> and two variables, neither explanation can be claimed. I want to be explicit about this
> because the temptation to declare "longer recovery fixes it" is strong and the data does not
> support it yet.

**How we separate them, this afternoon, for free:** mouse D2 was tethered at day 8 and has a
twice-measured baseline of 27.5 to 30 percent. It is scheduled to receive a new soldered
tether today.

- If D2 jumps to near 100%, **tether construction alone is sufficient** and recovery time is
  not the driver.
- If D2 improves only partly, **recovery time is carrying real weight**, and the fix for the
  next cohort is simply to follow the 14-day protocol we already have.

## 6. The professor's question: does a dangling cable interfere with other animals?

Now formally designed and partly underway: [[2026-08-06-unloaded-chain-interference]].

**Part A, what the empty cable itself does.** We strip it one element at a time and measure
after each removal: full cable, then without the tether, then without the slip ring, then
with nothing plugged in at all. Whichever removal drops the false-positive rate names the
leaking element. **First result is already in: removing the tether changed nothing** (22.5%
before, 26.7% after), so the tether is not the source. Slip ring is being tested now.

**Part B, whether it disturbs its neighbours.** We move the empty cable onto the new mouse's
splitter and alternate it in and out, four blocks, measuring both impedance and raw signal,
including a direct correlation between the empty cable's channels and the mouse's channels,
which measures crosstalk rather than inferring it. The new mouse is used because at 100% it
can only get worse, and getting worse is exactly what we are testing for. No anaesthesia and
no animal handling anywhere in this.

> [!note] The splitter is already partly cleared, for free
> Two observations from this morning argue against the splitter causing harm: the new mouse
> scored 20 out of 20 **while sharing its splitter with B2, which is completely dead**, and
> A1's EMG scored 70% **while sharing its splitter with this very empty cable**. Neither a
> dead partner nor an empty cable hurt its neighbour. The splitter was also excluded
> independently on 4 August.

## 7. Still open

- **We cannot separate recovery time from tether construction.** One animal, two variables.
  The D2 swap this afternoon addresses it.
- **We cannot test whether the slip ring is the culprit any more.** That test needed the same
  animal measured with two tethers that differ only in the slip ring, and the animal it was
  planned on died on 5 August. Any replacement costs an anaesthesia episode per animal.
- **We still only measure one half of each electrode pair.** The recording chip can test the
  other half but neither the manufacturer's software nor the open-source alternative exposes
  the control. This is with the vendor.
- **No video.** All cameras were removed from the room on 4 August, so we cannot yet relate
  contact dropouts to what the animal is physically doing.
- **The impedance duty cycle predicts channel class, not sleep-scoring yield.** In our
  our 2 August recording the pre-registered predictions came out 4 correct, 3 wrong, 1 void.
  A good duty cycle is necessary, not sufficient.

## 8. What I would say in one sentence

We have gone from "the electrodes are failing" to "the electrodes are fine and the connection
is intermittent" to, today, **"we now have a negative control, a corrected pass mark, and one
animal that works perfectly"** — and the single most valuable thing we can do next is find out
whether that animal works because we waited 16 days or because of its new cable.
