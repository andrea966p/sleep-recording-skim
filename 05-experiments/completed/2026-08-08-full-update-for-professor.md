---
tags: [status, eeg, report, professor, troubleshooting, analysis, claims]
created: 2026-08-08
status: complete
---

# The test mice, start to finish: the rig, the troubleshooting, and what the data can and cannot say

Covers the ORIGINAL EEG plus EMG cohort (surgeries 21 to 23 July 2026, tethered 30 July, recorded through 7 August). It does NOT cover the seven new EEG plus EMG plus ECG mice implanted on the evening of 7 August, which are a separate story and are currently blocked on a wiring fault.

---

# PART 0 — The very short version

> [!quote] Paste ready. No dashes, plain wording, nothing below is needed to follow it.
>
> **Where we ended up.** Out of eight animals in this cohort, **two produced continuous, scoreable EEG and EMG across a full 24 hour light and dark cycle**. One of them, B1, gave **23.66 hours in a single unbroken block**, which is the best recording this project has ever produced. The second, D2, gave 23.28 hours with a longest block of 9.6 hours. The other six gave nothing usable.
>
> **What was actually wrong.** Not the surgeries, not the amplifier, not the recording computer, not the room, not the mains hum, and not the electrodes. It was **electrical contact in the tether chain**, and it was intermittent. The same electrode on the same animal in the same session measured 0.052 megaohms one minute and 8.649 megaohms the next, a factor of 166. That single fact explains almost every confusing result we had for six weeks.
>
> **What fixed it.** Tethers rebuilt with **soldered joints sealed in resin**, replacing the thin heat shrink joints the original ones had. D2 went from 0.0 percent usable EEG to 87.9 percent within 24 hours of the swap, and it had been tethered only 8 days after surgery. So the long recovery time we suspected was not the deciding factor. The tether was. That matters because it means the fix is an engineering change we can apply to every animal, without new surgery.
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

## 1.3 The measurement that changed everything: the no wire control (31 July)

Every amplifier chip has 16 inputs and each mouse uses only 2 of them. That means **112 real amplifier inputs with no electrode attached are being recorded simultaneously, in the same file, on the same board**. We had been throwing them away.

Once we scored them, the picture inverted:

- Unwired inputs read a median impedance of 5.233 megaohms. The 32 mouse electrode legs read 5.329 megaohms. **Statistically identical.** So 5 to 8 megaohms does not mean "a high impedance electrode", it means **not connected at all**. 22 of 32 legs were open.
- Contact **flips on its own**. One channel went from 5869 to 11 microvolts, a factor of 522, in half a second, with nobody touching anything.

**Consequence: an impedance snapshot is not a go or no go gate.** Every ranking and comparison we had built on single sweeps was comparing two moments, not two conditions.

## 1.4 The biggest mistake: the channel map was wrong all along (1 August)

For weeks I reported that the EMG (electromyography, the neck muscle channel) had failed on 23 of 24 legs, and that we should consider new surgeries.

**You refused that result.** Your argument was that you did the surgeries yourself and it was not plausible that every single EMG had failed, so we must be reading the data wrong. That was correct.

The chip is an **Intan RHD2216, which is bipolar**. Each channel already reports the difference between its own plus and minus pins. The four solder pads on the headstage board are therefore **two channels, not four**: pads 0 and 1 together are the EEG channel, pads 2 and 3 together are the EMG channel. Our old analysis computed "EEG = pad0 minus pad1", which actually computed **EEG minus EMG**, and it computed "EMG" from **two empty pads that never had a wire on them**.

So the 24 "failed EMG surgeries" were empty pads. **The EMG mostly worked the whole time.** The real failure was always the EEG channel.

I confirmed this four independent ways (cross correlation between the two channels, high frequency burstiness, muscle power versus delta power, and the fact that the supposedly failed pads matched the no wire controls exactly).

**The lesson I want to keep: an implausible result is a bug report about your own method.** Audit the channel map first.

Fixing the map immediately produced the project's first real sleep architecture, from animal C1 on 31 July: 8.7 hours, wake 66.8 percent, non REM 29.3 percent, with correct physiology and strong persistence. That was the first evidence the rig could ever work.

## 1.5 The second bug, and the second retraction (3 August)

Then I found a bug in the persistence statistic itself. Persistence is our main check that a hypnogram is real and not noise: it asks whether the state one minute from now resembles the state now.

The code computed it as a fixed lag on the array of surviving epochs. **That is only a one minute lag if the epochs are contiguous in time.** Ours were not, because bad epochs had been removed. So the statistic silently measured a lag across arbitrary time gaps.

**It failed in BOTH directions**, which is why it was hard to catch: it gave an impossibly low value to a good recording, and an impossibly high value (0.854) to a recording whose longest block was 39 minutes of continuous wakefulness. Fixed by computing autocorrelation strictly within unbroken blocks.

I then rescored **every recording we have ever made**: 8 recordings, 41 animal recordings, about 174 animal hours. The result was **about 10.4 scoreable mouse hours, all of it from a single day, 31 July**. The 72 hour run and the 20 hour run contained zero. Six apparent recoveries found with the buggy metric were all false and were discarded.

## 1.6 The root cause: contact is intermittent and mechanical (4 August)

Seven impedance sweeps in 23 minutes settled it.

- **The electrodes and the implants are GOOD.** Animal B1's EEG measured **0.052 megaohms**, the best number ever recorded on this rig, and inside the published 10 to 50 kiloohm band for this kind of electrode. A degraded or badly implanted electrode cannot produce that. D2 recovered completely from a fully open state. **Damage is not cumulative.**
- **The problem is fast, reversible intermittency.** B1's EEG across 23 minutes: 6.236, then 0.052, then 8.649, then 0.177 megaohms.

⚠️ **WARNING, and this is a correction to something I said out loud that day:** I proposed that movement causes the contact loss, and I **disproved it the same day**. The pre-registered eight mouse test gave 50 percent connected among moving animals versus 50 percent among still animals. B1 contradicted itself directly, reading 8.649 while moving and then 0.177, connected, also while moving. **Do not repeat the movement explanation.**

Also settled and closed permanently: it is not the port, not the splitter, not the XDAQ recording box (B1 works in two different ports), not a cold solder joint, not board leakage, and not a statically broken slip ring. We put a multimeter across the whole fleet on 4 August, including a 360 degree rotation test, and everything passed.

## 1.7 Duty cycle, and the control that embarrassed our threshold (6 August)

Because a single sweep proves nothing, we automated the sweeps and started measuring the **fraction of sweeps in which a channel is connected**, over 20 to 40 repeats. That number reproduces across days, which is what makes it a real measurement.

Then we discovered that **one rig position, A2, held a cut cable with no mouse on it at all**. It had been sitting there as an accidental negative control.

🔴 **That empty cable passed our "connected" test 22 percent of the time.** Our threshold of 2 megaohms had a 22 percent false positive rate. Tightened to 0.5 megaohms, the empty cable drops to 2.5 percent.

Rescoring against that control: **only 4 of 14 channels across 7 animals beat a cable attached to nothing.** The rig was recording one animal out of eight, not the 1.8 we had counted.

We also tore the chain down rung by rung on the empty slot, and the false positive rate stayed flat (22.5 percent with the full chain, 26.7 percent without the tether, 23.3 percent with the headstage alone). **The false positives come from the amplifier's own floating input, not from our cabling.** Tether, slip ring and splitter are all innocent of that particular effect.

⚠️ **WARNING, and it is the most counterintuitive result of the whole project: the unwired floor reached 0.051 megaohms**, which is better than our best ever real electrode. **A single low impedance reading is NEVER evidence of contact.**

## 1.8 The filtering trap (6 August)

We took the standard textbook cleanup, a notch at 60, 120 and 180 hertz plus a bandpass from 0.5 to 30 hertz, and applied it to the animals **and to the 112 unwired inputs**.

🔴 **After filtering, a channel with no wire on it produces a median of 69 microvolts of plausible, EEG looking signal**, with a 95th percentile of 423 microvolts. **Filtering manufactures a convincing trace out of nothing.** So "the filtered trace looks good" is never evidence.

What does survive filtering is **the shape of the spectrum**. Real brain activity falls steeply with frequency; a bare wire is flat. The unwired floor sits at a spectral slope between minus 1.10 and minus 0.04. Our two working animals sit at minus 1.81 and minus 2.05, far outside it. That is the discriminator we now use, and it agrees with the impedance based test while being completely independent of it.

⚠️ Plot every trace on a **fixed** vertical scale. Auto scaling makes every channel look like signal.

## 1.9 The retraction I am least comfortable about (6 to 7 August)

On 6 August I reported, with a p value of 8.4 times 10 to the minus 8, that the new long tether had **harmed** animal D2, taking its EMG from 67 percent to 0 percent.

**That was exactly backwards.** The overnight recording showed the swap had **fixed** D2: usable EEG went from 0.0 percent to 87.9 percent, railed epochs from 29.7 percent to 0.0 percent, median hum from 916.9 to 133.2 microvolts.

The reason the statistic lied is that the 40 sweep block spanned only **21 minutes**, and it happened to sit inside one long open state. Contact on this rig stays in one state for longer than 21 minutes, so a short block can sample a single state and then report it with enormous, entirely spurious confidence.

🔑 **The rule that came out of this, and it now governs how we report everything: an impedance block SCREENS, only a multi hour recording is an OUTCOME.** Always state the block duration next to any duty cycle. Never conclude harm or benefit from a block alone.

## 1.10 The overnight recording that worked (6 to 7 August)

`allego_1__uid0806-16-57-38`, 23.66 hours, 89.3 gigabytes, a full light and dark cycle.

- **B1: EEG usable 100 percent, EMG 99.6 percent, longest unbroken block 3.6 hours by the strict combined criterion**, and the whole 23.66 hours as a single block by the analysis pipeline's own criterion. Both numbers are correct; they use different epoch lengths and different gates. **Quote the pipeline numbers for scoreability.**
- **D2: EEG 87.9 percent, EMG 98.6 percent, longest block 87.3 minutes strict, 9.6 hours by the pipeline.**
- **Everything else 0.0 percent.**
- Neither working animal railed at all.
- Falsification passed: the unwired floor scored 0.00 percent usable and the no mouse slot scored 0.0 percent.

**Why the tether is the answer and recovery time is not.** D2 was tethered on 30 July, day 8 after surgery, which is short of our own 14 day standard operating procedure. It had 0.0 percent usable EEG. A new tether chain took it to 87.9 percent without touching the animal's implant. That was the pre-registered disambiguation and it came out cleanly.

⚠️ **HONEST LIMIT: four things changed together in that swap.** Tether construction, slip ring removed, connector reseated, and one isoflurane episode. So "does the new chain help" is answered YES. "Is it specifically the slip ring" is NOT answered, and answering it would cost one anaesthesia per animal. The best circumstantial argument is that one successful chain kept its slip ring and the other did not, so what the two share is **soldered and resin encapsulated construction**.

⚠️ Also: a per animal forensic pass on the six failures showed that **five of the six point at the tether chain rather than the implant.** One animal's tether is confirmed chewed. Two animals show a correlation of 0.74 and 0.50 between their own two independent channels, where working animals sit at 0.07, which is the signature of one shared fault path rather than two independent electrode failures.

## 1.11 One animal died

B1, the original, died under isoflurane on 5 August during a tether swap. The replacement animal in that slot is the one referred to as B1 throughout the recording results above. That loss also permanently ended the slip ring isolation experiment.

---

# PART 2 — The analysis, and what it is worth

The pipeline takes the raw file, gates out unusable epochs, scores each 4 second epoch as wake, non REM or REM, and then produces architecture, bout statistics and light versus dark breakdowns. Every threshold in it was re-derived from our own data, 1,137,955 epochs of it.

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

## Claims I have withdrawn

- ❌ "First sleep biology recorded" (15 July). Clipping artefact, flipped sign when railed epochs were excluded.
- ❌ "The EMG failed on 23 of 24 legs, we may need new mice." The channel map was wrong. The EMG mostly worked.
- ❌ "Six channels recovered." Found with the buggy persistence metric, all false.
- ❌ "The new long tether harmed D2, p equal to 8.4 times 10 to the minus 8." Backwards. The swap fixed it. The block was 21 minutes long and caught one open state.
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
