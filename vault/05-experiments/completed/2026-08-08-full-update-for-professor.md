---
tags: [status, eeg, report, professor, troubleshooting, analysis, claims]
created: 2026-08-08
status: complete
---

# The test mice, start to finish: the rig, the troubleshooting, and what the data can and cannot say

> [!info] 📄 **THIS IS THE LONG WORKING RECORD, NOT THE HANDOUT.**
> **The document to actually send is [[2026-08-08-professor-update-short]]** — two pages, eight figures, crucial points only.
> This page keeps the complete narrative, every number, every retraction and every raw file reference behind it.
> Figures live in `05-experiments/attachments/2026-08-09-fig01..fig09-*.png`, rebuilt on 2026-08-09 after an audit;
> the previous set is kept under `attachments/superseded/2026-08-08-figures/`. **Read
> [[figure-and-analysis-audit-2026-08-08]] before citing any figure**: it records a fabricated reference band, an
> invalid confidence interval, three figures that held typed-in values, and a threshold-dependent tether result
> that all had to be corrected.

Covers the ORIGINAL EEG plus EMG cohort (surgeries 21 to 23 July 2026, tethered 30 July, recorded through 7 August). It does NOT cover the seven new EEG plus EMG plus ECG mice implanted on the evening of 7 August, which are a separate story and are currently blocked on a wiring fault.

---

# PART 0 — The very short version

> [!quote] Paste ready. No dashes, plain wording, nothing below is needed to follow it.
>
> **Where we ended up.** Out of eight animals in this cohort, **two produced continuous, scoreable EEG and EMG across a full 24 hour light and dark cycle**. One of them, B1, gave **23.66 hours in a single unbroken block**, which is the best recording this project has ever produced. The second, D2, gave 23.28 hours with a longest block of 9.6 hours. The other six gave nothing usable.
>
> **How long it took and why.** These animals were operated on 21 to 23 July and first connected to the rig on 30 July. The first impedance readings were taken by hand on 31 July, one sweep at a time, and two test recordings ran across that weekend, about 50 hours in total. Those first readings misled us badly, and it is worth saying exactly how: the same animal read 0.623, then 1.717, then 0.027 megaohms across 98 minutes with nothing done to it, a swing of 64 times, and we were reading each of those numbers as a fact about the animal. It took another five days to work out that we were sampling a switch that flips on its own, and to replace single readings with repeated ones, negative controls, and a threshold derived from amplifier inputs that have no wire on them.
>
> **One naming warning.** A1, B1, D2 and so on are rig positions, not animal names. The B1 in the overnight result is **not** the B1 in the July results, because the original animal in that position was sacrificed on 5 August after its skull electrode detached, and a replacement was moved in.
>
> **What was actually wrong.** Not the surgeries, not the amplifier, not the recording computer, not the room, not the mains hum, and not the electrodes. It was **electrical contact in the tether chain**, and it was intermittent. The same electrode on the same animal in the same session measured 0.052 megaohms one minute and 8.649 megaohms the next, a factor of 166. That single fact explains almost every confusing result we had for six weeks.
>
> **What fixed it.** Tethers rebuilt with **soldered joints sealed in resin**, replacing the thin heat shrink joints the original ones had. D2 went from 0.0 percent usable EEG to 87.9 percent within 24 hours of the swap, and it had been tethered only 8 days after surgery. So the long recovery time we suspected was not the deciding factor. The tether was. That matters because it means the fix is an engineering change we can apply to every animal, without new surgery.
>
> **Animals that started well and then failed.** Several, and the most painful is C1. It had the best electrode in the fleet on 31 July, it survived us deliberately wiggling every joint in its cable, and it produced 8.73 hours of real sleep in one unbroken block, which was the only real sleep data this project had until August. By Sunday morning its EEG was electrically open and it never recorded again, even though the impedance came back to a good value four days later. **That is the fact that made us stop trusting impedance as a result: a channel can read connected and still record nothing.** A second animal, A1, has had a textbook perfect muscle electrode for a week and still gives about 5 percent usable data, because its reading is 331 microvolts of which 296 is mains hum. Impedance can see that a wire is connected. It cannot see what is riding on it.
>
> **What the data shows.** Both animals show real temporal structure in sleep and wake, they are much more awake in the dark phase than in the light phase, and the order of state transitions is correct. The light phase sleep numbers, 70 percent for D2 and 81 percent for B1, sit near the published value for this mouse strain.
>
> **What I will NOT claim.** We have **no human scored ground truth yet**, so the accuracy of the automatic scoring is unmeasured. We also found that the single most important threshold in the analysis, the one that separates wake from sleep, moves the headline circadian number by up to 66 percentage points when nudged by 25 percent. So the agreement with the literature is real but it is **not** the independent confirmation I described it as last week. And we cannot separate REM sleep reliably at all, so I report wake versus non REM sleep only.
>
> **The one thing that unblocks everything.** A human needs to blind score 300 short clips per animal so we can compute a Cohen kappa. The packs are built and waiting, the decision rules were written down before any scoring started, and it is a few hours of work. Until then every architecture number should be treated as provisional.

---

# PART 1 — The history, in the order we learned it

I am writing this as a narrative because the individual results only make sense against what we believed at the time. Several things I told you earlier turned out to be wrong, and I flag every one of them.

## 1.1 The first wall: mains hum (July)

The rig is in Korea, so mains is **60 hertz**, not 50. Getting that wrong cost us weeks early on.

Every channel was swamped by 60 hertz pickup. Five advisors re-ran the raw files and produced the equation that has held up ever since:

```
differential 60 Hz  ~=  common mode mains  x  electrode impedance imbalance
```

There is one mains source driving everything (phase locking value of 1.00 across all recording slots). A bipolar montage is supposed to reject that, and ours did not, because the two legs of each pair had badly mismatched impedances. So **the hum was never really an electrical noise problem. It was a contact problem wearing a noise costume.** That reframing is the single most useful thing that came out of July.

**What worked:** aluminium foil over the headstages. Single ended 60 hertz collapsed by up to two orders of magnitude (one channel went 3604 to 8 microvolts). This is Intan's own published advice. **WARNING: our foil is still floating.** It should be tied to a ground point outside itself, and it is not, so we are leaving a large part of the available improvement on the table.

**What did NOT work, and should never be re-tested:** grounding the power brick, earthing work by the electricians, the SPI splitter, and slip ring rotation. All tested directly, all negative, all closed.

## 1.2 The first false alarm: "first sleep biology" (15 July, RETRACTED)

I reported the first apparent sleep signal on 15 July. It was **an artefact of amplifier saturation**, and I retracted it the next day.

The channel was hard railed: raw maximum sitting exactly on the rail at 6389.6 microvolts, standard deviation around 4050 microvolts where real mouse bipolar EEG is under 300. **Only 1 epoch out of 493 had zero clipped samples.** When I excluded the railed epochs the effect **flipped sign**, from minus 0.65 to plus 0.63. A railed amplifier is non linear, so its spectrum means nothing.

**The lesson, which is now enforced in code:** never judge a channel before rejecting clipped epochs, and always report the fraction of CLEAN epochs, not just the median clip percentage. The scoring script now hard refuses to produce a verdict when fewer than 60 clean epochs survive.

There is a second, subtler point here that took us until August to appreciate. **On this rig, railing is the signature of an OPEN electrode, not of a moving animal.** The slot with no mouse attached at all rails 100 percent of the time. So discarding railed epochs does not rescue a bad channel, it just leaves you with fewer bad epochs.

## 1.3 The cohort arrives and is connected for the first time (21 to 30 July)

⚠️ **A naming point that has confused every reader of our older files, including me.** A1, B1, C1, D2 and so on are **rig POSITIONS, not animal identities**. Port A slot 1, port B slot 1, and so on. Those same eight labels were in use before this cohort existed, so **the July recordings before 30 July describe DIFFERENT animals in the same eight positions.** Everything in sections 1.1 and 1.2 above happened to earlier animals. **Please confirm the individual identities against your own surgery log before any of this reaches a paper**, because our files record positions and dates, not animal IDs.

**This cohort: surgeries 21 to 23 July. First tethered 30 July.** That is **day 8 to 10 after surgery**, against our own written standard operating procedure of at least 14 days of recovery, and roughly 1 day of habituation on the tether against the reference lab's 9 days. We knew that at the time and did it anyway because the whole point was to commission the rig. 🛑 **That is why "about 6 percent yield" from those first runs must never be quoted as our yield.** Both of those runs were commissioning tests run against our own protocol.

Before 30 July nothing about this cohort had been measured at all. The first electrical contact any of these animals had with the rig was on 30 July, and the first measurement was the following afternoon.

## 1.4 The first impedance readings, done by hand, one sweep at a time (31 July)

This is the part of the history I want to set out carefully, because almost everything we did for the next week was a reaction to how badly this first day misled us.

**How we worked then.** One impedance sweep at a time, exported to a CSV file, opened and read by eye. No repetition, no controls, no automation. A sweep takes about 20 seconds and we treated each one as a fact about the animal. **The whole conceptual apparatus we use now, duty cycle over 20 to 40 sweeps, an unwired floor control, a threshold derived from that floor, did not exist on 31 July. None of it.**

Here is what the raw files from that afternoon actually contain for B1, and this is the single most instructive table in the whole project:

| time | configuration | B1 EEG | B1 EMG |
| --- | --- | --- | --- |
| 16:13 | B1 alone on port B, no splitter | **0.623 MΩ** | **0.026 MΩ** |
| 17:34 | 8 mice, splitters in, the sweep before run 1 | **1.717 MΩ** | **5.465 MΩ** |
| 17:51 | 4 mice, splitters removed | **0.027 MΩ** | 6.695 MΩ |

**Nothing was done to that animal between those three readings.** Its EEG moved 0.623, then 1.717, then 0.027, a range of **64 times** across 98 minutes. Its EMG went from an excellent 0.026 to fully open and stayed there.

At the time I read those three numbers as three different measurements of three different configurations, and I drew conclusions about the splitter from them. **They were three samples of a switch that flips on its own.** We did not understand that for another four days.

The pre run 1 sweep, which is the one we actually acted on, read like this for the two animals that end up mattering:

| animal | position | EEG | EMG |
| --- | --- | --- | --- |
| **B1** | `B/1`, `B/2` | 1.717 | 5.465 |
| **D2** | `D/33`, `D/34` | **0.660** | **0.286** |

By the standard we were using that day, **D2 looked like one of the best animals on the rig and B1 looked mediocre**. That was almost exactly backwards over the following week.

Three things happened the same day that started to dismantle this way of working:

- **The electricians' earth wiring was measured and did nothing.** I also got the hum measurement itself wrong first time, by reading 60 hertz on a single spectral bin, which understated it by four to five times because mains drifts and does not sit exactly on 60.00 hertz. I corrected it within the hour, and we now always measure the 55 to 65 hertz BAND.
- **The splitter was put on trial and acquitted by direct physical test**, not by argument. With every splitter pulled, the legs still matched a no wire control.
- **We watched a channel break live**, mid recording, with nobody touching anything: 4346 microvolts down to 7 microvolts, a factor of 522, inside half a second. ⚠️ **Tissue does not do that in half a second. That is metal losing contact with metal.**

I also made and retracted a claim the same evening: I said the fault was localised to a slip ring because one animal started chattering while a different animal was being provoked. **You pointed out that those two animals share nothing, so it was coincidence, and I withdrew it.** The cost of that retraction was real: it left us with **no positive evidence pointing at any specific joint**, which is why the next week was spent building controls rather than chasing parts.

## 1.5 The measurement that changed everything: the no wire control (31 July)

Every amplifier chip has 16 inputs and each mouse uses only 2 of them. That means **112 real amplifier inputs with no electrode attached are being recorded simultaneously, in the same file, on the same board**. We had been throwing them away.

Once we scored them, the picture inverted:

- Unwired inputs read a median impedance of 5.233 megaohms. The 32 mouse electrode legs read 5.329 megaohms. **Statistically identical.** So 5 to 8 megaohms does not mean "a high impedance electrode", it means **not connected at all**. 22 of 32 legs were open.
- Contact **flips on its own**. One channel went from 5869 to 11 microvolts, a factor of 522, in half a second, with nobody touching anything.

**Consequence: an impedance snapshot is not a go or no go gate.** Every ranking and comparison we had built on single sweeps was comparing two moments, not two conditions.

## 1.6 The two weekend test recordings (31 July to 2 August)

Both of the first real recordings on this cohort ran over that weekend, and between them they are the reason we stopped trusting single measurements of any kind.

**Run 1. Friday 31 July, 18:06, for 27.9 hours, 105 gigabytes, all 8 mice.** Started about half an hour after the pre run 1 sweep above.

- ✅ **Environmental causes closed for good.** Sixteen internally tied control pins across 27.9 hours: median 2.8 microvolts, maximum 5.3, **zero drift** across a full light and dark cycle, and all eight headstages identical. **Do not revisit earth, room, splitter or grounding.** That question is answered.
- 🔴 **78.7 percent of all electrode leg time was OPEN**, later corrected to 61.6 percent once the channel map was fixed.
- 🔴 **Two distinct failure modes, and they are different problems.** One is **one way irreversible loss**: a channel is connected for hours and then goes open and never comes back. The other is **chattering**: hundreds of flips, back and forth. B1 was the worst chatterer in the fleet, at 372 flips or more.
- ⚠️ **The flip counts are LOWER BOUNDS.** To survey a 105 gigabyte file we sampled 10 seconds out of every 60, so any flip inside the unobserved 50 seconds is invisible.
- ⭐ This run contains **C1's 8.7 hour window, which was the cleanest data the project had ever produced**, 99.9 percent of epochs with zero clipping. On the wrong channel map I scored it as showing NO sleep structure and logged it as a negative result. **After the map was corrected two days later, the same window turned out to be textbook sleep architecture.** That is the single clearest example of how much damage the map did.

**Run 2. Sunday 2 August, 01:46, for 21.74 hours, all 8 mice.** This was the first run using the corrected channel selection, and the first run where I wrote the predictions down BEFORE looking at the data, in a pre registration document, precisely because we had already retracted one result and corrected another.

The pre flight sweep predicted, per animal, which would be scoreable. Scored afterwards: **4 hits, 3 misses, 1 void.**

- ✅ **HIT: B1 will have good EEG and no EMG.** It had the best EEG in the fleet and 0.0 percent EMG.
- ✅ **HIT: A1, C1 and D1 will have good EMG and no EEG.** Muscle channels at 99.9, 97.1 and 100 percent, EEG at 0.0 percent on all three.
- ✅ **HIT: the two worst animals will yield nothing.** They yielded nothing.
- ✅ **HIT: at least one channel will change state during the run.** One did, degrading from 11.2 percent to 0.4 percent across thirds of the recording.
- ❌ **MISS: one to two mice will be fully scoreable.** **Zero were.** The animal predicted to be the best gave 0.06 hours inside testable blocks, in 250 fragments with a median length of 4 seconds.

🔑 **The lesson from that scorecard is the most useful single sentence about impedance we have: it predicts CLASS, not YIELD.** It tells you fairly reliably whether a channel is connected at the moment you measure it. It tells you almost nothing about how many hours that channel will give you, because it cannot see that the channel will spend the night flipping.

**And between the two runs, with nothing done to any animal, contact moved in BOTH directions:**

| animal | channel | 31 July | 2 August | change |
| --- | --- | --- | --- | --- |
| B1 | EEG | 1.717 | **0.133** | **13 times BETTER**, best on the rig |
| C2 | EEG | 4.418 | 1.146 | open to connected |
| C1 | EEG | 0.465 | 5.720 | **connected to OPEN**, our best animal lost it |
| D2 | EEG | 0.660 | 2.114 | drifted into the grey zone |

⭐ **Channels recover as readily as they fail. Damage is not cumulative.** That fact is what kept us from concluding the implants were dying, and it is the reason nobody has scheduled a new surgery since.

**So the honest summary of the weekend: two recordings, about 50 hours, eight animals, and after the channel map correction about 21 scoreable mouse hours, all of it from run 1, and zero from run 2.**

## 1.7 The biggest mistake: the channel map was wrong all along (1 August)

For weeks I reported that the EMG (electromyography, the neck muscle channel) had failed on 23 of 24 legs, and that we should consider new surgeries.

**You refused that result.** Your argument was that you did the surgeries yourself and it was not plausible that every single EMG had failed, so we must be reading the data wrong. That was correct.

The chip is an **Intan RHD2216, which is bipolar**. Each channel already reports the difference between its own plus and minus pins. The four solder pads on the headstage board are therefore **two channels, not four**: pads 0 and 1 together are the EEG channel, pads 2 and 3 together are the EMG channel. Our old analysis computed "EEG = pad0 minus pad1", which actually computed **EEG minus EMG**, and it computed "EMG" from **two empty pads that never had a wire on them**.

So the 24 "failed EMG surgeries" were empty pads. **The EMG mostly worked the whole time.** The real failure was always the EEG channel.

I confirmed this four independent ways (cross correlation between the two channels, high frequency burstiness, muscle power versus delta power, and the fact that the supposedly failed pads matched the no wire controls exactly).

**The lesson I want to keep: an implausible result is a bug report about your own method.** Audit the channel map first.

Fixing the map immediately produced the project's first real sleep architecture, from animal C1 on 31 July: 8.7 hours, wake 66.8 percent, non REM 29.3 percent, with correct physiology and strong persistence. That was the first evidence the rig could ever work.

## 1.8 The second bug, and the second retraction (3 August)

Then I found a bug in the persistence statistic itself. Persistence is our main check that a hypnogram is real and not noise: it asks whether the state one minute from now resembles the state now.

The code computed it as a fixed lag on the array of surviving epochs. **That is only a one minute lag if the epochs are contiguous in time.** Ours were not, because bad epochs had been removed. So the statistic silently measured a lag across arbitrary time gaps.

**It failed in BOTH directions**, which is why it was hard to catch: it gave an impossibly low value to a good recording, and an impossibly high value (0.854) to a recording whose longest block was 39 minutes of continuous wakefulness. Fixed by computing autocorrelation strictly within unbroken blocks.

I then rescored **every recording we have ever made**: 8 recordings, 41 animal recordings, about 174 animal hours. The result was **about 10.4 scoreable mouse hours, all of it from a single day, 31 July**. The 72 hour run and the 20 hour run contained zero. Six apparent recoveries found with the buggy metric were all false and were discarded.

## 1.9 The root cause: contact is intermittent and mechanical (4 August)

Seven impedance sweeps in 23 minutes settled it.

- **The electrodes and the implants are GOOD.** Animal B1's EEG measured **0.052 megaohms**, the best number ever recorded on this rig, and inside the published 10 to 50 kiloohm band for this kind of electrode. A degraded or badly implanted electrode cannot produce that. D2 recovered completely from a fully open state. **Damage is not cumulative.**
- **The problem is fast, reversible intermittency.** B1's EEG across 23 minutes: 6.236, then 0.052, then 8.649, then 0.177 megaohms.

⚠️ **WARNING, and this is a correction to something I said out loud that day:** I proposed that movement causes the contact loss, and I **disproved it the same day**. The pre-registered eight mouse test gave 50 percent connected among moving animals versus 50 percent among still animals. B1 contradicted itself directly, reading 8.649 while moving and then 0.177, connected, also while moving. **Do not repeat the movement explanation.**

Also settled and closed permanently: it is not the port, not the splitter, not the XDAQ recording box (B1 works in two different ports), not a cold solder joint, not board leakage, and not a statically broken slip ring. We put a multimeter across the whole fleet on 4 August, including a 360 degree rotation test, and everything passed.

## 1.10 Duty cycle, and the control that embarrassed our threshold (6 August)

Because a single sweep proves nothing, we automated the sweeps and started measuring the **fraction of sweeps in which a channel is connected**, over 20 to 40 repeats. That number reproduces across days, which is what makes it a real measurement.

Then we discovered that **one rig position, A2, held a cut cable with no mouse on it at all**. It had been sitting there as an accidental negative control.

🔴 **That empty cable passed our "connected" test 22 percent of the time.** Our threshold of 2 megaohms had a 22 percent false positive rate. Tightened to 0.5 megaohms, the empty cable drops to 2.5 percent.

Rescoring against that control: **only 4 of 14 channels across 7 animals beat a cable attached to nothing.** The rig was recording one animal out of eight, not the 1.8 we had counted.

We also tore the chain down rung by rung on the empty slot, and the false positive rate stayed flat (22.5 percent with the full chain, 26.7 percent without the tether, 23.3 percent with the headstage alone). **The false positives come from the amplifier's own floating input, not from our cabling.** Tether, slip ring and splitter are all innocent of that particular effect.

⚠️ **WARNING, and it is the most counterintuitive result of the whole project: the unwired floor reached 0.051 megaohms**, which is better than our best ever real electrode. **A single low impedance reading is NEVER evidence of contact.**

## 1.11 The filtering trap (6 August)

We took the standard textbook cleanup, a notch at 60, 120 and 180 hertz plus a bandpass from 0.5 to 30 hertz, and applied it to the animals **and to the 112 unwired inputs**.

🔴 **After filtering, a channel with no wire on it produces a median of 69 microvolts of plausible, EEG looking signal**, with a 95th percentile of 423 microvolts. **Filtering manufactures a convincing trace out of nothing.** So "the filtered trace looks good" is never evidence.

What does survive filtering is **the shape of the spectrum**. Real brain activity falls steeply with frequency; a bare wire is flat. The unwired floor sits at a spectral slope between minus 1.10 and minus 0.04. Our two working animals sit at minus 1.81 and minus 2.05, far outside it. That is the discriminator we now use, and it agrees with the impedance based test while being completely independent of it.

⚠️ Plot every trace on a **fixed** vertical scale. Auto scaling makes every channel look like signal.

## 1.12 The retraction I am least comfortable about (6 to 7 August)

On 6 August I reported, with a p value of 1.0 times 10 to the minus 7, that the new long tether had **harmed** animal D2, taking its EMG from 67 percent to 0 percent.

> [!note] ⚠️ Small numerical correction made on 26 August, and it changes nothing about the story
> When this update was first written the p value here read 8.4 times 10 to the minus 8. That number had been computed over 41 impedance sweeps rather than 40. The extra one was a single manual sweep taken by hand about 80 seconds before the automated block began, which had been sitting in the same folder and was getting picked up by a file glob. Recomputed over the real 40 sweeps the value is **1.0 times 10 to the minus 7**. The counts, the medians, the direction and the retraction below are all unchanged. The full audit is in the tether comparison page, section 13.

**That was exactly backwards.** The overnight recording showed the swap had **fixed** D2: usable EEG went from 0.0 percent to 87.9 percent, railed epochs from 29.7 percent to 0.0 percent, median hum from 916.9 to 133.2 microvolts.

The reason the statistic lied is that the 40 sweep block spanned only **21 minutes**, and it happened to sit inside one long open state. Contact on this rig stays in one state for longer than 21 minutes, so a short block can sample a single state and then report it with enormous, entirely spurious confidence.

🔑 **The rule that came out of this, and it now governs how we report everything: an impedance block SCREENS, only a multi hour recording is an OUTCOME.** Always state the block duration next to any duty cycle. Never conclude harm or benefit from a block alone.

## 1.13 The overnight recording that worked (6 to 7 August)

`allego_1__uid0806-16-57-38`, 23.66 hours, 89.3 gigabytes, a full light and dark cycle.

- **B1: EEG usable 100 percent, EMG 99.6 percent, longest unbroken block 3.6 hours by the strict combined criterion**, and the whole 23.66 hours as a single block by the analysis pipeline's own criterion. Both numbers are correct; they use different epoch lengths and different gates. **Quote the pipeline numbers for scoreability.**
- **D2: EEG 87.9 percent, EMG 98.6 percent, longest block 87.3 minutes strict, 9.6 hours by the pipeline.**
- **Everything else 0.0 percent.**
- Neither working animal railed at all.
- Falsification passed: the unwired floor scored 0.00 percent usable and the no mouse slot scored 0.0 percent.

**Why the tether is the answer and recovery time is not.** D2 was tethered on 30 July, day 8 after surgery, which is short of our own 14 day standard operating procedure. It had 0.0 percent usable EEG. A new tether chain took it to 87.9 percent without touching the animal's implant. That was the pre-registered disambiguation and it came out cleanly.

⚠️ **HONEST LIMIT: four things changed together in that swap.** Tether construction, slip ring removed, connector reseated, and one isoflurane episode. So "does the new chain help" is answered YES. "Is it specifically the slip ring" is NOT answered, and answering it would cost one anaesthesia per animal. The best circumstantial argument is that one successful chain kept its slip ring and the other did not, so what the two share is **soldered and resin encapsulated construction**.

⚠️ Also: a per animal forensic pass on the six failures showed that **five of the six point at the tether chain rather than the implant.** One animal's tether is confirmed chewed. Two animals show a correlation of 0.74 and 0.50 between their own two independent channels, where working animals sit at 0.07, which is the signature of one shared fault path rather than two independent electrode failures.

## 1.14 The animal we lost

B1, the original, was sacrificed on 5 August because its skull electrode had detached. The replacement animal in that slot is the one referred to as B1 throughout the recording results above. That loss also permanently ended the slip ring isolation experiment.

⚠️ **CORRECTION LOGGED 2026-08-09.** This was written up at the time as a death under isoflurane on induction, and a welfare action was raised off the back of it. **That was wrong and both have been withdrawn across the vault.** Anaesthesia is not implicated and no check of the vaporiser, flow or warming is owed.

⭐ **The corrected cause carries a finding, and it cuts slightly against the tether story, so it is stated here rather than buried.** A **skull electrode physically came away** on this animal. That is a genuine head side, mechanical failure mode, and it is the one piece of direct physical evidence of an implant level problem in the whole cohort. It does not overturn the tether conclusion, because that conclusion rests on a different animal recovering from zero to 87.9 percent usable EEG **with its implant untouched**, and on five of six failures showing shared path or cable signatures. What it does mean is that **head side attachment is not automatically safe**, and it belongs on the list of things to watch in the next cohort alongside the tether construction.

---

# PART 1b — The two animals that matter, followed individually

Everything in Part 1 is the fleet view. Because the entire result rests on two positions, here is each one on its own, in order, with every number we have. **These two timelines are the argument.** Read them and the conclusion about the tether follows on its own.

## B1, and the fact that B1 is two different animals

🔴 **IMPORTANT AND EASY TO MISS. The B1 in our overnight result is NOT the B1 in our July results.** The original animal in that position died on 5 August. A replacement was moved into the same position on 6 August. Both are called B1 in the files, because the file names record the rig position. **Any figure or sentence that puts a July B1 number next to an August B1 number is comparing two animals.**

### B1, the original, 30 July to 5 August

| when                 | what happened                                         | numbers                                                                        |
| -------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| 31 Jul 16:13         | first ever reading, alone on port B                   | EEG **0.623**, EMG **0.026 MΩ**, both excellent                                |
| 31 Jul 17:34         | 8 mouse sweep, 81 minutes later, nothing done         | EEG **1.717**, EMG **5.465**, the muscle channel has gone open                 |
| 31 Jul 17:51         | splitters removed, 17 minutes later                   | EEG **0.027**, a **64 times** swing from the reading before                    |
| 31 Jul evening       | chattered during another animal's provocation test    | bounced between 10 and 4400 microvolts for 55 seconds                          |
| 31 Jul to 1 Aug      | **run 1**, 27.9 hours                                 | **the worst chatterer in the fleet, 372 flips or more**                        |
| after run 1          | scored on the corrected map                           | **11.8 hours of good EEG, 0.2 hours of EMG**                                   |
| 2 Aug 01:44          | pre run 2 sweep                                       | EEG **0.133, the best number on the rig**, EMG **7.099, open**                 |
| 2 Aug                | **run 2**, 21.74 hours                                | best EEG in the fleet and still only 14 percent of epochs; EMG **0.0 percent** |
| 4 Aug 16:44          | moved to **port D** as a control                      | still works there, so **the port, splitter and recording box are cleared**     |
| 4 Aug 16:47 to 16:56 | four sweeps in nine minutes                           | EEG **6.236 then 0.052 then 8.649 then 0.177 MΩ**                              |
| 5 Aug 16:36          | **arm A**, original tether, 20 sweeps                 | EEG connected **45 percent**, EMG **20 percent**                               |
| 5 Aug 17:46          | **arm B**, short soldered and resin tether, 20 sweeps | EEG **100 percent**, EMG **75 percent**, p = 0.0001 and 0.0006                 |
| 5 Aug                | **sacrificed, skull electrode detached**      | colony down to seven                                                           |

⭐ **The single most important number in the whole project is in that table: 0.052 megaohms.** That is inside the published range for this type of electrode, it is the best value ever recorded on this rig, and **a degraded or badly implanted electrode cannot produce it.** It is the positive evidence that the implants were fine.

⭐ **The second most important thing in that table is the shape of it.** This animal had **11.8 hours of good EEG in run 1 and was still completely unscoreable**, because scoring needs the muscle channel too and the muscle channel was dead. **One channel blocked half a day of good brain data.** That pattern, one good channel and one dead one on the same animal through the same cable, is what eventually pointed at the cable rather than the animal.

⚠️ **What was lost with this animal:** it was the only animal with a measured before and after on the same tether comparison, and the arm C test that would have isolated the slip ring specifically is **permanently impossible**. The arm A and arm B blocks stand and are still the strongest tether evidence we have.

### B1, the replacement, from 6 August

| when | what | numbers |
| --- | --- | --- |
| implanted | 21 July, with the rest of the cohort | |
| kept | **untethered in its home cage until 6 August** | **16 days of recovery**, the first animal ever tethered inside our own protocol |
| tethered with | the 19.5 cm short soldered and resin tether from arm B | |
| 6 Aug 11:30 | 20 sweep census | EEG **100 percent**, EMG **100 percent**, **zero flips**, EEG median 0.813 MΩ |
| 6 Aug 12:45 | 3.18 hour afternoon recording | **SCOREABLE**, persistence 0.481, 73.3 percent asleep in the light phase |
| 6 to 7 Aug | 23.66 hour overnight recording | **EEG usable 100 percent, EMG 99.6 percent, the whole recording is ONE unbroken block** |
| | spectral check | slope **minus 1.81**, delta fraction 0.32, against a bare wire floor of minus 1.29 to minus 0.07 |
| | railing | **zero railed epochs out of 782** |
| | scoring | persistence **0.603**, REM entered from non REM 72.4 percent at about 10 standard deviations above its null |

⚠️ **This animal changed TWO things at once: 16 days of recovery AND a soldered tether. It is n equals 1. It cannot tell us which of the two mattered.** What resolved that was D2, below, which got the tether without the recovery time.

## D2, the animal that answers the question

D2 is the more valuable of the two, scientifically, because it is the only animal we have that went **from failing to working with nothing changed on the animal side**.

| when | what happened | numbers |
| --- | --- | --- |
| 21 to 23 Jul | surgery | |
| 30 Jul | first tethered, **day 8 after surgery**, 6 days short of our own protocol | |
| 31 Jul 17:34 | first ever reading, pre run 1 | EEG **0.660**, EMG **0.286 MΩ**, one of the best looking animals on the rig |
| 31 Jul to 1 Aug | **run 1**, 27.9 hours | **4.2 hours of good EEG, 27.8 hours of EMG** |
| 2 Aug 01:44 | pre run 2 | EEG **2.114, drifted into the grey zone**, EMG 0.023 |
| 2 Aug | **run 2** | nothing usable |
| 2 Aug 23:34 | post run 2 | EEG **9.200 MΩ, fully open** |
| 3 Aug | full rescore of everything | D2 **correctly REJECTED**, persistence 0.250 and physiology FAIL. ⚠️ It had "passed" two days earlier only because it had been scored on a hand picked window using **another animal's** threshold. **Never reuse a threshold derived from one animal on another.** |
| 4 Aug | three sweeps | **connected on BOTH channels in EVERY sweep**: 0.352 and 0.233, then 0.459 and 0.270, then 0.400 and 0.088. **The only animal to manage that all day.** ⭐ It had recovered completely from fully open, with nothing done to it. |
| 5 Aug | served as the control animal for B1's tether comparison | EEG 40 percent then 15 percent, EMG 100 percent then 95 percent. **The control did not improve while B1 did**, which is what excludes a session wide drift explanation for B1's result |
| 6 Aug 11:30 | fleet census, 20 sweeps | EEG **30 percent**, EMG **100 percent** |
| 6 Aug, rescored against the empty cable | at the corrected 0.5 megaohm pass mark | 🔴 **D2's EEG is NOT statistically distinguishable from a cable attached to nothing.** EMG only. **Cannot stage sleep.** |
| 6 Aug 15:57 | 15 sweep baseline, 20 minutes before the swap | |
| 6 Aug 16:27 | **new long soldered tether fitted, slip ring removed**, 40 sweeps over 20 minutes | 🔴 read as **harm, p = 1.0 times 10 to the minus 7** |
| 6 to 7 Aug | the 23.66 hour overnight recording | ✅ **EEG usable 0.0 percent to 87.9 percent. Hum median 916.9 to 133.2 microvolts. Spectral slope minus 0.38 to minus 2.05. Railed epochs 29.7 percent to 0.0 percent. EMG 86.1 to 98.6 percent.** |
| 7 Aug, scored | | **SCOREABLE.** 23.28 hours in 9 blocks, longest 9.6 hours, persistence 0.499, REM order 78.4 percent at about 12 standard deviations, **70.4 percent asleep in the light phase** |

**Why this animal settles the argument.** D2 was tethered at day 8, which is exactly the condition we suspected was ruining the cohort. It was scored as having no usable EEG at all, twice, by two independent methods, and against a negative control. **A tether swap, with the implant untouched, took it to 87.9 percent usable and to the steepest, most biological spectrum on the rig.**

⇒ **Recovery time is not the deciding variable. The tether chain is.** ⇒ **The remaining animals are recoverable by an engineering change, without surgery.**

⚠️ **Two honest limits on that.** First, the swap changed **four things together**: tether construction, slip ring removed, connector reseated, and one isoflurane episode. So "does the new chain help" is answered yes, and "is it the slip ring specifically" is not answered and now cannot be, cheaply. The best argument is that B1's successful chain KEPT its slip ring and D2's successful chain did not, so what the two share is **soldered and resin encapsulated construction**. Second, **D2 is the most threshold fragile of our three recordings**, with a 66 point swing on the circadian number, so its 70.4 percent should never be quoted bare.

## What the two timelines have in common

1. **Both animals looked fine, then bad, then fine again, with nothing done to them.** Neither shows the monotonic decline you would expect from a failing implant.
2. **Both were scored as failures by our own methods at some point, and both were right to be scored that way at the time.**
3. **Both recovered on a cable change.**
4. **Neither ever railed once it was working.** Railing is an open circuit signature on this rig, and both animals stopped doing it entirely.
5. **In both cases the impedance sweep taken just before or just after was a poor predictor of the recording**, in one case confidently and wrongly predicting harm.

---

# PART 1c — The other six positions, including the ones that started well and then degraded

You asked specifically about animals that looked fine at the start and got worse. **There are several, and one of them is the animal that gave us the only real sleep data this project had before August.** This section is the whole fleet, measured, not remembered. Every number below comes out of the raw sweep files.

## The full impedance history, all eight positions, in megaohms as EEG / EMG

| position | 31 Jul 17:34 | 2 Aug 01:44 | 2 Aug 23:34 | 4 Aug 16:33 | 4 Aug 16:56 |
| --- | --- | --- | --- | --- | --- |
| **A1** | 6.757 / **0.087** | 4.446 / **0.087** | 8.284 / **0.073** | 6.078 / **0.252** | 5.989 / **0.327** |
| **A2** | 7.644 / 5.849 | 5.962 / 4.851 | 6.917 / 1.746 | **1.966** / 8.195 | 6.221 / 3.639 |
| **B1** | 1.717 / 5.465 | **0.133** / 7.099 | **0.732** / 6.375 | 6.236 / 6.660 | **0.177** / 8.693 |
| **B2** | 7.110 / 5.663 | 5.771 / 6.287 | 7.336 / 2.695 | **0.879** / 7.765 | 5.406 / 7.765 |
| **C1** | **0.465** / **0.190** | 5.720 / **0.051** | 7.929 / **0.270** | 4.323 / **0.323** | **0.584** / **0.644** |
| **C2** | 4.418 / **0.139** | **1.146** / **0.168** | 2.507 / **0.111** | 5.137 / **0.318** | **0.411** / **0.122** |
| **D1** | 6.300 / **0.335** | 3.980 / **0.202** | 7.504 / **0.279** | **1.172** / 8.203 | 4.926 / 5.557 |
| **D2** | **0.660** / **0.286** | 2.114 / **0.023** | 9.200 / 1.273 | **0.352** / **0.233** | **0.400** / **0.088** |

Bold is below 0.5 megaohms, which is the pass mark we arrived at later, after the empty cable told us the old one was far too generous. **Nothing was done to any animal between any two columns.**

⚠️ **Read that table across the rows, not down the columns.** Almost every row goes up and down. **There is no row that shows a clean monotonic decline**, which is what a dying implant would look like. What there is instead is a lot of movement in both directions, on a timescale of hours to days.

## C1: the animal that gave us everything, then stopped

This is the clearest case of the pattern you asked about, and it is worth stating in full because for two days C1 WAS the project.

| when | impedance EEG | what the recording gave |
| --- | --- | --- |
| 31 Jul 17:34 | **0.465**, best EEG in the fleet | |
| 31 Jul evening | | ⭐ **the first clean unclipped EEG pair the project ever produced**: 0.00 percent clipping, 11.7 microvolts of hum, delta dominant, sane 1/f falloff |
| 31 Jul, provocation test | | 🔑 **survived direct provocation.** We deliberately wiggled its electrode, its tether, its slip ring wires, and twisted the slip ring, one joint at a time. The channel stayed between 2.2 and 30.3 microvolts across the whole 101 seconds. **Nothing moved it.** |
| 31 Jul to 1 Aug, run 1 | | ⭐⭐ **8.73 hours usable, in ONE unbroken 8.1 hour block, persistence 0.744.** Still the highest persistence value we have ever measured. **This was the only recording with real sleep in it until 6 August.** |
| 2 Aug 01:44 | **5.720, fully open** | |
| 2 Aug, run 2 | | **0.0 percent usable EEG** |
| 2 Aug 23:34 | 7.929 | |
| 4 Aug 16:33 | 4.323 | |
| 4 Aug 16:56 | **0.584, connected again** | |
| 6 Aug, 20 sweep census | **0 out of 20 sweeps below the pass mark, on BOTH channels** | |
| 6 to 7 Aug, overnight | | **EEG 0.0 percent usable.** Hum 5813 microvolts, 6.8 percent railed, spectral slope minus 0.34, which is inside the bare wire range |

**So: our single best animal lost its EEG between Friday night and Sunday morning and never recorded with it again**, even though the impedance came back to 0.584 megaohms on 4 August.

🔑 **That last point is the important one and it generalises.** A channel can read connected and still record nothing. Impedance is measured with a small injected current at one frequency, and it can pass through a contact that is far too unstable or too noisy to carry microvolt biology for hours. **This is why we stopped treating impedance as an outcome.**

⭐ **C1's muscle channel, by contrast, has been connected the entire time and still is**, at 0.190, 0.051, 0.270, 0.323 and 0.644 megaohms, and at 75.9 microvolts of hum in the overnight recording, which is inside the connected band. **C1 is the best salvage candidate on the rig.** ⚠️ Its muscle channel carries 544 microvolts of root mean square signal against only 75.9 microvolts of hum, so there is a lot of real non hum content, and it is **either genuine muscle activity or movement artefact. Video is the only way to separate those, and the cameras were removed from the room on 4 August.**

## C2: the second scoreable animal, and a chewed cable

C2 was the **second** animal ever to produce scoreable sleep, alongside C1, in run 1. Its impedance actually IMPROVED into run 2, from 4.418 to 1.146 megaohms, going from open to connected, which is why the pre registration predicted it as **the single most likely animal to be scoreable**.

**It then produced 0.06 hours of testable data in 250 fragments with a median length of 4 seconds.** That was the biggest miss on the run 2 scorecard, and it is where "impedance predicts class, not yield" comes from.

⭐ **We now know why, and the recording itself told us.** Both of C2's channels sit at **intermediate hum, around 1076 and 1331 microvolts, which is QUIETER than the bare wire floor at 2276 microvolts**, with almost no railing and no signal. That is the signature of a **partially conducting, damaged cable**, not an open electrode and not a failing animal. 🦷 **C2's tether is chewed, and this is the data confirming it.**

⚠️ **Note the trap in that.** A damaged cable can read **quieter** than a channel with no wire at all. **Quiet is not good.** If we had been screening on hum alone, C2 would have looked like one of the better animals.

## A1 and D1: perfect muscle channels, and what they cost us

**A1 has the most stable channel on the entire rig.** Its muscle electrode read 0.087, 0.087, 0.073, 0.252 and 0.327 megaohms across five sweeps spanning five days, and in the census it was connected in 70 to 95 percent of sweeps, which is statistically far better than an empty cable. **Its EEG has been open in every single measurement we have ever taken.**

🔴 **And yet A1's muscle channel produced only 5 to 7.6 percent usable data in the recordings.** The explanation is the single most useful sentence about impedance we have: **its root mean square is 331 microvolts, of which 296 microvolts IS the 60 hertz hum.** ⇒ **Impedance can see that the wire is connected. It CANNOT see that mains is riding on it.** A perfect impedance number and an unusable recording, on the same channel, at the same time.

**D1 shows the same shape and adds a degradation.** Its muscle channel read 0.335, 0.202 and 0.279 megaohms across the first three sweeps, then **8.203 megaohms, fully open, on 4 August**, then **0.688 megaohms nine minutes later**. Fully open to fully connected in nine minutes, with nobody touching it.

🔴 **In the overnight recording, D1's own two channels correlate at 0.74.** Working animals sit at 0.07 to 0.08. **A correlation that high means both channels are riding one common potential, so this is ONE fault upstream of both of them, in the ground, the connector or the tether body. It is not two independent electrode failures.** B2 shows the same thing more weakly, at 0.50.

That matters for what you do next: **for D1 and B2, check the ground pin mating before assuming anything at all about the implants.**

## B2: never worked, and told us something anyway

B2 never produced usable data in any run. Its value to us is diagnostic: on 31 July we watched one of its channels drop by a factor of **522 in half a second**, mid recording, untouched. That was the observation that first proved contact flips on its own, and it is the reason the rest of the investigation was built the way it was.

## A2: the position that turned out to hold no animal

A2 produced nothing throughout, and on 6 August we found out why: **that position holds a cut tether attached to nothing**, still wired through its slip ring, headstage and splitter.

⭐ **It became the most valuable object on the rig.** It is our first true negative control, and it is what revealed that our pass mark had a **22 percent false positive rate**. It also behaves exactly as a control should in the overnight recording. **It is staying in place permanently**, because every sweep reads all ports at once, so the control is free forever.

⚠️ **Please confirm from your own records what happened to the animal that was in that position.** Our files record the position as empty from 6 August and do not record the animal's fate.

# PART 1d — What the degradations actually imply

This is the part I would want you to take away from the fleet history, separately from the two working animals.

1. 🔑 **No animal shows the pattern of a failing implant.** A failing electrode gives a monotonic decline. **We see movement in both directions on every single position**, including full recovery from a fully open state, in C1, D1, D2 and B1. Combined with the best ever reading of 0.052 megaohms and a clean multimeter pass across the whole fleet, **the implants are not the problem, and this is positive evidence, not an absence of evidence.**

2. 🔴 **A connected impedance does NOT mean a usable recording.** C1 read 0.584 megaohms and recorded nothing. A1 read 0.087 megaohms for a week and gave 5 percent usable data because mains was riding on the wire. **Impedance is a screening tool. The recording is the outcome. Never report one as if it were the other.**

3. 🔴 **A quiet channel does NOT mean a good channel.** C2's damaged tether reads quieter than a bare wire. A shorted channel reads quieter than a good one. **Always confirm biology, never pass a channel on low noise alone.**

4. ⭐ **The failures are not eight independent stories, they are mostly one story.** Of the six failing positions: one is a confirmed chewed tether, two are single shared path faults upstream of both channels, two have a working electrode on one channel and a floating one on the other **through the same cable**, and one has no animal in it. **Five of six point at the tether chain.** That is the same conclusion the two working animals reach from the other direction.

5. ⚠️ **We came very close to concluding the opposite.** On 16 July the standing conclusion in this vault was "every frontal electrode is open on every mouse, this is a surgery problem, the cohort is spent, make new mice." That was written before the no wire control existed, before the channel map was corrected, and before anyone had measured what a disconnected input reads on this hardware. 🛑 **No surgeries were scheduled on it, and that turned out to be the right call.**

6. 📉 **The honest yield figure, and how to say it.** Across every recording made before 6 August, about 174 animal hours, we have roughly **10.4 scoreable mouse hours, all of it from one animal on one day**. After the tether change, a single 23.66 hour recording produced **about 47 scoreable animal hours from two animals**. ⚠️ **That is a comparison of one recording against one recording and it should be presented as such**, but the direction is not subtle.

7. 🛑 **What this does NOT license.** It does not license "the tethers are all we need to fix", because we have two working animals, not eight. It does not license quoting any yield percentage from the July runs as our yield, because those animals were tethered 4 to 6 days earlier than our own protocol with about a day of habituation instead of nine. And it does not license any statement about scoring accuracy until the blind scoring is done.

---

# PART 2 — The analysis, and what it is worth

The pipeline takes the raw file, gates out unusable epochs, scores each 4 second epoch as wake, non REM or REM, and then produces architecture, bout statistics and light versus dark breakdowns. Every threshold in it was re-derived from our own data, 1,137,955 epochs of it.

## 2.0 Where the statistics live

Point estimates alone are not the case. The tests behind each claim are in two figures.

**Hardware claims, `05-experiments/attachments/2026-08-09-fig08-hardware-statistics.png`.** Every channel's connected duty cycle against 2,240 readings from amplifier inputs with no wire, Fisher exact one sided, Jeffreys 95 percent intervals. **Four of sixteen channels beat an unconnected input after Holm correction for the sixteen tests, and three of those four are muscle channels.** Risk differences against the floor run from +26.9 to +66.9 points. The tether comparison is on the same figure, Fisher exact, at BOTH pass marks, with the concurrent control animal plotted alongside so drift can be ruled out by eye. See the correction above: the EEG half of that comparison reverses at the corrected pass mark.

**Sleep claims, `05-experiments/attachments/2026-08-09-fig09-sleep-statistics.png`.** Persistence against a within block permutation null, REM ordering against 2,000 run order permutations, and the rank correlation between impedance and actual yield with an exact permutation p.

⚠️ **Two things that figure admits rather than hides.** First, **no confidence interval is placed on the persistence magnitude.** The best recording is a single unbroken block, so there is no independent replicate to resample, and a block bootstrap interval would mostly report the chunk length chosen rather than anything about the animal. A block bootstrap was built, produced intervals that did not bracket their own point estimate, and was discarded rather than tuned until it looked right. The permutation test shown instead is exact and tests the claim actually being made. Second, the values plotted come from the stored hypnogram, whose labels have been through the 12 second minimum bout rule, so they sit **above** the raw label values quoted throughout this document. That gap is the smoothing inflation described in §2.4, drawn rather than asserted.

⭐ **The rank correlation is the useful negative result.** Across the seven positions holding an animal, impedance duty cycle against usable fraction gives Spearman rho 0.73 with an **exact permutation p of 0.094 from 10,000 relabellings, not significant**. The exact test is used because five of the seven values are tied, which makes the asymptotic p unreliable, and the position with no animal is excluded because it cannot belong in a correlation about animals. D2 was connected in one sweep out of twenty and produced 87.9 percent usable EEG; three channels tied with it produced nothing. That is the operational rule stated as a number.

## 2.1 The three scoreable recordings

| | B1 overnight | D2 overnight | B1 afternoon |
|---|---|---|---|
| usable | **23.66 h in ONE block** | 23.28 h in 9 blocks, longest 576.4 min | 3.18 h in one block |
| wake / non REM | 50.2 / 46.5 percent | 43.3 / 49.9 percent | 26.7 / 65.3 percent |
| persistence r at 1 min | **0.603** | 0.499 | 0.481 |
| REM entered from non REM | 72.4 percent, null 56.6 plus or minus 1.6, about **9.9 SD** | 78.4 percent, null 64.5 plus or minus 1.2, about **11.6 SD** | 81.1 percent, null 62.8 plus or minus 3.8, about 4.8 SD |
| asleep in light phase | 81.2 percent (swing **36.0** points) | 70.4 percent (swing **66.0** points) | 73.3 percent (swing 22.3 points) |

Persistence calibration: pure noise gives minus 0.035, synthetic 4 minute bouts give plus 0.510. All three recordings sit above the bout calibration. For comparison, C1 on 31 July, the previous best, was 0.744.

## 2.2 The council review, and what survived it

I put the whole analysis through a five advisor review with anonymous peer review on 7 August. It found six serious problems. I then went and **measured** each one, and three of them did not survive contact with the data. I am reporting both halves.

**Problems that were REAL and are now fixed or acknowledged:**

🔴 **Four of the five "physiology checks" cannot fail.** I had been reporting "physiology 5 out of 5 PASS" as validation. Three of those checks are simply the scoring rule restated back to itself, and a fourth is near forced as the residual. **Only one, that non REM has the largest EEG amplitude, can genuinely fail.** The summary files now print FORCED next to each one. **I will not quote 5 out of 5 again and neither should anyone reading our output.**

🔴 **"Threshold independent" was false.** The wake versus sleep threshold is refit per animal, so animals are not on a common scale.

🔴 **Accuracy is unmeasured.** No human has scored anything, so there is no Cohen kappa. This is the blocking item.

🔴 **We only have negative controls.** Every control we have proves we do not hallucinate signal. **None of them proves we would FIND a signal that is really there. A pipeline that returned "no signal" for every input would pass every check we currently have.** That only starts to cost us the moment a result depends on an absence, for example a genotype with less delta power or a drug that suppresses REM.

**Problems that turned out NOT to apply, once measured:**

⭐ **The selection bias is not operating.** The worry was that our quality gate rejects epochs based on contact, contact is movement driven, movement is a behavioural state, and therefore the surviving clean epochs would be enriched for quiet states and every downstream number would inherit a bias correlated with the thing we are measuring. That is a correct concern in principle. Measured: **B1 rejected 0.0 percent of epochs in both recordings, D2 rejected 1.3 percent**, and the rejected epochs in D2 have LOWER muscle activity, which is the opposite direction from the feared bias. Two of the three recordings could not have been biased at all.

⭐ **The REM ordering result is real evidence.** REM sleep should be entered from non REM sleep, not from wakefulness. The objection was that this could be forced by how many epochs of each state exist. Tested by permuting the ORDER of state runs while preserving their lengths and composition. Observed values sit at the 100th percentile of the null at **5 to 12 standard deviations** in all three recordings. **This is now our second informative validity check, and it is the stronger of the two.**

🟡 **The pseudoreplication concern is half real.** All three peer reviewers said the 112 unwired control channels are not independent because they share a board, a reference and a ground. Measured: the intraclass correlation by port is 0.000 and the effective sample size is 110.7 out of 112, so they are effectively exchangeable. However, a cluster bootstrap that resamples the four ports gives an interval 4.8 times wider. That width is mostly an artefact of having only four clusters. **Conservative position: quote the wider cluster interval anyway.**

⛔ One recommendation was **rejected**: modernising the staging algorithm (multitaper spectra, hidden Markov models, or the published automatic scorers). At two animals with zero ground truth that is busywork, and sophisticated staging on unverified channels **hides** the failure mode rather than exposing it. Validate first, modernise second.

## 2.3 The result that damaged our best claim

I had been presenting the circadian agreement as the strongest evidence we had, on the grounds that nothing in the quality gate, the scoring rule or the persistence statistic knows anything about the clock, so agreement with the published light phase sleep figure would be genuine external validation.

I then swept the wake threshold by plus or minus 25 percent, which is a shift of only 0.097 in log space.

| animal | reported asleep in light | range across the sweep | swing |
|---|---|---|---|
| B1 afternoon | 73.3 percent | 60.9 to 83.2 | 22.3 points |
| B1 overnight | 81.2 percent | 54.2 to 90.2 | 36.0 points |
| **D2 overnight** | **70.4 percent** | **23.0 to 89.0** | **66.0 points** |

🔴 **A 25 percent shift in one per animal threshold moves D2 from 23 percent to 89 percent asleep in the light phase. The published value of about 70 percent is reachable from almost anywhere in that range.** So the circadian agreement is **not** the independent confirmation I presented it as. It is still a sanity check that we are not wildly wrong, and the direction is right, but the number must always be quoted with its swing.

⚠️ **A direct correction to myself:** I previously called D2's 70.4 percent "the cleaner number" because it is closest to the literature mean. **On this axis it is the WORST of the three**, with a 66 point swing against B1's 36. Proximity to a published mean says nothing about robustness.

⭐ What the sweep really diagnoses is more useful than what it destroyed: a shift that small only moves things this much if **the muscle activity distribution has no clear valley between sleep and wake**, meaning the threshold is being cut inside a continuum rather than at a gap. And the ranking tracks signal quality exactly, with B1 at 15.2 microvolts of hum and 0.0 percent unscored versus D2 at 26.6 microvolts and 1.6 percent.

🛑 **A tempting fix I am refusing:** B1's persistence statistic actually peaks at a different threshold than the automatic one, 0.689 versus 0.603. **Tuning the threshold to maximise our own validity statistic would make that statistic circular.** The threshold must be chosen against an EXTERNAL standard, which means human agreement.

## 2.4 Aligning with the Tsukuba method

Our montage follows Iwasaki, Funato and Yanagisawa, so I checked our analysis against the current method paper from that group (Nakata and colleagues, SLEEP 2025).

**We match on:** 4 second epochs, theta defined as 6 to 9 hertz, and episode duration computed as total time divided by episode count.

**We differed, and I applied four changes on 8 August:** transition epochs are now excluded from spectra only, not from the state totals; band power is normalised against the 15 to 30 hertz band as they do; state totals are now reported against the whole recording as well as against scored epochs; and the delta band moved from 0.5 to 4 hertz up to 1 to 4 hertz.

⭐ That last one also suits our hardware. **The acquisition high pass sits at 1.10 hertz and reaches the saved file**, so it had already eaten everything below 1.1 hertz irreversibly. A 0.5 hertz band edge was integrating nothing.

🔴 **One thing we must stop attributing to them: there is NO minimum bout duration rule anywhere in the Tsukuba method.** Our 12 second rule is a house convention and it is now labelled as one in the code. That matters because it is not a small knob. Applying it changed B1's bout count from 1232 to 205 and the median bout length from 12 seconds to 84 seconds.

⚠️ **The trap that exposed:** smoothing INFLATES our validity statistics by construction. B1's persistence went from 0.603 to 0.742 and the REM ordering from 73.9 to 82.7 percent purely from merging short bouts. **Fixed:** persistence and REM ordering are now computed on the RAW labels before any merging, while architecture, bouts and the light and dark split are computed after. The output records which is which.

⚠️ **Our protocol differs from theirs in one large way that is worth saying out loud:** they allow at least 7 days of recovery and then at least 9 days of habituation on the tether. We tethered at day 8 to 10 with about 1 day of habituation. That is a real gap and it is a plausible contributor to the first tethering wakefulness we have seen before.

## 2.5 The Japanese scoring tool's source code

I obtained and read the source of the scoring application used by the collaborating group.

⭐ **They do not use a percentile rule for REM.** Both of their thresholds are **two cluster k means splits**, with the threshold set at the midpoint between cluster centres: wake from the rectified muscle integral, REM from the theta to delta ratio among sleep epochs only.

That is directly relevant, because **our percentile rule forces REM to a fixed share of sleep by construction**, which is exactly why our REM numbers are untrustworthy. Their wake rule is effectively the same as ours (k means with two clusters and Otsu's method optimise the same split on one dimensional data), which also means **the plus or minus 25 percent sensitivity we found applies to their tool too**.

Two things worth knowing: their delta and theta are **time domain rectified integrals, not spectral band powers**, so their threshold values cannot be transferred to our features without rescaling. And their interface has **manual overrides on all three thresholds with a live hypnogram**, which means that in practice a human tunes the automatic thresholds by eye. Their published method describes itself as semiautomatic with visual inspection, and that is what that means.

🛑 **I have applied NONE of it, deliberately.** Swapping the REM rule changes every REM number, and changing methods at two animals with no ground truth is unfalsifiable. **The order is: score the blind packs, get the kappa, and only then swap the REM rule and measure whether the kappa improves.**

---

# PART 3 — What I claim, and what I refuse to claim

## Claims I will defend

1. **Two animals produced continuous, scoreable EEG and EMG across a full light and dark cycle**, one of them as a single unbroken 23.66 hour block. Both are far outside the unwired control on two independent measures, and the weakest passing channel is at p equal to 0.00003.
2. **Sleep and wake show real temporal structure.** Persistence sits well above both the shuffled null and the synthetic bout calibration.
3. **The order of state transitions is real.** REM is entered from non REM far more often than a permutation of the same state runs would give, at 5 to 12 standard deviations.
4. **The bottleneck is electrical contact in the tether chain, not surgery, not the implants, and not the recording system.** Supported by a best ever 0.052 megaohm reading, by full recovery of a previously open channel, by a clean multimeter pass across the whole fleet, and by five of six failures showing a shared fault path rather than independent electrode failures.
5. **The fix is an engineering change applicable to every animal without new surgery.** D2 went from 0.0 to 87.9 percent usable EEG on a tether swap alone, at day 8 after surgery.

## A claim corrected on 2026-08-09

🔴 **"The soldered tether took the duty cycle from 45 percent to 100 percent" is threshold dependent and must no longer be quoted that way.** That figure was computed at the 2 MOhm pass mark, which was retired the next day when a cut cable with no animal was found to pass 22 percent of the time at 2 MOhm. Re-scored at the corrected **0.5 MOhm** pass mark, the same 40 sweeps give **B1 EEG 5/20 to 2/20** (the improvement disappears and reverses, p = 0.41) and **B1 EMG 0/20 to 7/20** (still improves, p = 0.0083). The concurrent control animal does not improve at either threshold, so the design is intact; the threshold was doing the work. ⚠️ The census memory had already said "re-score old blocks before quoting them" and this block was never re-scored.

⭐ **What survives:** the tether conclusion never rested on this block. It rests on the recording, D2 going from 0.0 to 87.9 percent usable EEG with the implant untouched. This is exactly the rule the project adopted after the arm C retraction: **impedance blocks screen, only a multi-hour recording is an outcome.**

## Claims I have withdrawn

- ❌ "First sleep biology recorded" (15 July). Clipping artefact, flipped sign when railed epochs were excluded.
- ❌ "The EMG failed on 23 of 24 legs, we may need new mice." The channel map was wrong. The EMG mostly worked.
- ❌ "Six channels recovered." Found with the buggy persistence metric, all false.
- ❌ "The new long tether harmed D2, p equal to 1.0 times 10 to the minus 7." Backwards. The swap fixed it. The block was 21 minutes long and caught one open state.
- ❌ "Movement causes the contact loss." Proposed and disproved the same day.
- ❌ "Physiology passes 5 out of 5." Four of the five checks cannot fail.
- ❌ "The circadian agreement is threshold independent." It swings by up to 66 points.
- ❌ "About 6 percent yield." Both of those runs were commissioning tests, run 2 to 6 days earlier than our own standard operating procedure.

## Claims I refuse to make until they are earned

- ⛔ **Any REM percentage.** Our percentile rule and an independent threshold disagree by a factor of five (3 to 8 percent of sleep versus 33 to 34 percent), and the published value is under 10 percent. Neither of ours is a measurement. **I report wake versus non REM, plus the ORDER of transitions, and nothing else about REM.**
- ⛔ **Any statement about scoring accuracy.** No human has scored anything yet.
- ⛔ **Any claim resting on an ABSENCE of signal**, for example "the manipulation reduced X". We have no positive control, so we cannot yet demonstrate the pipeline would find a signal that is really there.
- ⛔ **Normal sleep architecture.** B1 sits above the published mean, D2 sits near it but is the most threshold fragile of the three, and n equals 2.

---

# PART 4 — Still open

**Two items, both open by choice rather than by obstacle.**

1. 🔴 **The blind scoring and Cohen kappa. This is the blocking item.** Three packs of 300 clips each are built and verified unscored in `/home/skimlab/eeg-processed/2026-08-06/`. Each clip shows 20 seconds with the 4 second epoch to be scored shaded in the middle, matching how the lab normally views it, in random order so bout structure cannot be followed, on a fixed vertical axis because auto scaling leaks the answer. The automatic label is never shown. Keys 1, 2, 3 and 4 are wake, non REM, REM and unsure, and unsure is allowed and excluded from the statistic.

   **The decision rules were written down BEFORE any epoch was scored**, in `02-procedures/blind-scoring-and-kappa.md`, so the result cannot be reinterpreted afterwards: kappa at or above 0.80 keeps the current staging; 0.60 to 0.80 means we report it with the confusion matrix and treat the automatic architecture as approximate; 0.40 to 0.60 makes it a screening tool only and anything published gets hand scored; below 0.40 means we stop using automatic staging entirely and the pipeline becomes a signal provenance instrument.

   The REM specific kappa decides the REM question, including whether we adopt the k means split. **Score D2 first**, because D2 is the animal whose circadian number swings 66 points and whose 70 percent figure is load bearing.

   The harness itself was validated against a simulated scorer with 15 percent injected disagreement, in a temporary copy so no fake sheet could touch the real packs, and it recovered the injected value correctly.

2. 🟡 **A positive control**, specified in `02-procedures/positive-control-known-signal-injection.md` but not scheduled. A function generator, a roughly 1000 to 1 divider and a few precision resistors, half a day, about 20 pounds, no animals. Four tests: amplitude accuracy, frequency response, spectral slope recovery, and impedance against known resistors. ⭐ The frequency response test would also **finally measure what the 1.10 hertz hardware high pass does to the bottom of the delta band**, which we currently only reason about. 🛑 Bench only, spare headstage, and the amplifier input range is plus or minus 5 millivolts, so the divider must be verified before anything is connected.

**Deferred and not coming back:** fitting the new tether chain to the other five animals of this cohort, and the interference test, both of which needed these animals, which have now been replaced. Restoring the cameras is still owed and still blocks two things, one animal's ambiguous muscle channel and the video to EEG synchronisation work.

---

# Scope note

Everything above concerns the ORIGINAL EEG plus EMG cohort. Those animals were replaced on the evening of 7 August by seven new mice carrying EEG, EMG and ECG. **No further data will come from the animals described here. These three recordings are the complete dataset.**

The new cohort is currently blocked on a separate and fully diagnosed fault: the cerebellum ground pin was mated to the wrong wire on every animal, so all seven are floating. The fix is a connector re-mate and needs no anaesthesia.
