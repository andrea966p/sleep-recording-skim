---
title: W-SD cohort, first screen after surgery
date: 2026-08-18
status: active
tags: [experiment, eeg, emg, cohort, w-sd, recording, grounding]
subjects: 8
---

# The W-SD cohort: what the first six minutes say

> [!abstract] TL;DR
> Eight newly operated mice from batch **W-SD** went on the rig today and I took a short
> recording to see whether they are worth a long run. **Five of the eight give clean, real
> brain signal (electroencephalogram, EEG): W-SD A1, A2, B2, C1 and D2.** Four of those five
> also give a believable muscle signal (electromyogram, EMG); W-SD B2 has EEG only.
>
> **One mouse, W-SD C2, has an open electrode.** Nothing to do about that from the outside.
>
> **Two headstages, on W-SD B1 and W-SD D1, have no ground connection.** That is a plug
> problem, not an animal problem, and it appeared TODAY. Andrea is checking the seating of
> those connectors tomorrow morning.
>
> ⚠️ **THIS IS NOT A PASS FOR ANYBODY.** The recording is 6.43 minutes long and our own rule
> asks for at least 15 unbroken minutes before a channel counts as connected. Read this as
> "worth a long run", not as "these mice work".

Recording **`allego_0__uid0818-18-56-33`**, started 2026-08-18 18:56:33 KST, stopped 19:02:59.
Related: [[2026-08-18]] · [[animal-card-and-verdict-ladder]] ·
[[2026-08-07-ecg-cohort-baseline]].

## How I am naming these mice

They are batch **W-SD**, and I refer to them as **W-SD** plus the rig position: W-SD A1, W-SD A2,
W-SD B1 and so on, where the letter is the amplifier port and the number is the slot on that port.

⚠️ **THESE ARE EIGHT BRAND NEW ANIMALS. NOTHING FROM ANY EARLIER COHORT CARRIES OVER.** A rig
position is a socket on the amplifier, not an identity. "D2" in this note and "D2" in any note
written before today are different mice. Every judgement below is made against wire free
amplifier inputs recorded **inside this same file**, so no earlier animal is used as a yardstick
anywhere.

Still missing for these eight, and I need it before a proper cohort manifest can exist: individual
animal identifiers, surgery dates, sex, and which tether arm is on which port.

## The recording

| | |
|---|---|
| duration | **6.43 min** (386.048 s) |
| size | 404,578,304 bytes |
| sample rate | 1000 Hz |
| data samples | 386,048 |
| timestamp samples | 386,048 |
| remainder bytes | **0 and 0** |
| channels | 262 total, 256 amplifier |
| hardware band pass | 1.098 to 475.17 Hz on all four ports |

✅ **The file is intact.** Data and timestamps agree to the sample and neither has a partial record.

**Two roles this time, not three.** The file's own channel map says electroencephalogram on `/1`
and `/33`, electromyogram on `/2` and `/34`. There is **no electrocardiogram (ECG) wired on this
cohort**: `/3` and `/35` read as bare unconnected inputs on every properly grounded chip. So the
wire free floor for this cohort is `/3` to `/16` and `/35` to `/48`, which is one site wider per
slot than the previous three role cohort.

## ⚠️ THE STANDARD ENGINE GIVES THE WRONG ANSWER ON THIS FILE

`core/criteria.py` builds its floor by pooling **all 112 wire free sites in the file** into one
distribution and taking the 1st percentile. That is correct only when every amplifier chip is in
the same electrical state. Here two chips are floating, their unconnected inputs are about fifty
times quieter than everyone else's **and** spectrally steep, and they drag the pooled threshold
down to a spectral slope of **−2.002**. That is steeper than every animal channel in the file, so
the pooled run condemns the whole cohort:

| position | pooled usable EEG % | per chip usable EEG % |
|---|---|---|
| W-SD A1 | 0.0 | **100.0** |
| W-SD A2 | 0.0 | **100.0** |
| W-SD B1 | 13.2 | not judgeable |
| W-SD B2 | 2.6 | **100.0** |
| W-SD C1 | 0.0 | **100.0** |
| W-SD C2 | 0.0 | 0.0 |
| W-SD D1 | 10.5 | not judgeable |
| W-SD D2 | 0.0 | **100.0** |

🔴 **THE POOLED FLOOR IS UNSAFE THE MOMENT ANY ONE HEADSTAGE FLOATS**, and it fails quietly: the
pooled falsification check still reports a mean of 0.35 %, which passes, because the check asks
whether the floor scores usable and not whether the floor is homogeneous.

**So every number below uses a per chip floor**: each animal channel is judged only against the
fourteen wire free inputs on **its own port and slot**, which is the same chip, the same cable and
the same room. That is what the in file control was always supposed to be. Every chip passes its
own falsification check, mean 0.00 to 0.38 % against the 1 % that is expected by construction.

📌 **Code change owed:** `core/criteria.py` needs a per chip floor option. Until it has one, do not
run `cards/ladder.py` on a file where the per chip 60 Hz numbers below are not all in the same
range.

## The eight mice

Per chip floor, slope criterion for EEG, hum plus root mean square (rms) amplitude for EMG,
10 second quality control epochs, 38 of them. **Zero railed epochs on all sixteen animal channels.**

| mouse | EEG slope | steepest wire free input on its own chip | margin | usable EEG | EMG rms / 60 Hz, µV | verdict |
|---|---|---|---|---|---|---|
| **W-SD A1** | −1.50 | −0.23 | **−1.27** | **100 %** | 78.7 / 15.2 ✅ | EEG and EMG |
| **W-SD A2** | −1.51 | −0.27 | **−1.24** | **100 %** | 53.8 / 7.9 ✅ | EEG and EMG |
| **W-SD B2** | −1.73 | −0.52 | **−1.20** | **100 %** | 475.5 / 639.9 ❌ | **EEG only** |
| **W-SD C1** | −1.69 | −0.16 | **−1.53** | **100 %** | 21.9 / 27.5 ✅ | EEG and EMG |
| **W-SD D2** | −1.72 | −0.56 | **−1.16** | **100 %** | 13.9 / 11.5 ✅ | EEG and EMG |
| **W-SD C2** | **−0.16** | −0.38 | **+0.22** | **0 %** | 61.9 / 78.4 | **open electrode** |
| **W-SD B1** | −1.85 | −1.91 | **+0.06** | — | 29.0 / 28.8 | **chip floating** |
| **W-SD D1** | −1.82 | −1.96 | **+0.13** | — | 1232 / 1644 | **chip floating** |

The five good channels are not marginal. Their delta share sits at 0.34 to 0.38 and their low to
high frequency ratio at 13 to 27, both in the range a working animal has produced before, and the
scale free guard reports `raw` on all of them, so none of this is a filter corner being read as
slope.

### W-SD C2 is a single open electrode, and the criterion says so out loud

Its chip is fine: the wire free inputs on port C slot 2 sit at 3088 µV of mains hum, which is
normal. But C2's own EEG channel is **quiet at 122 µV and spectrally FLAT at −0.16**, with a delta
share of 0.085 and a low to high ratio of 1.4. Quiet and flat at once is the signature of an input
connected to nothing, not of an electrode.

⚠️ **The hum criterion calls this channel 86.8 % usable.** The hum versus slope guard fires and
refuses it, exactly as it is designed to. This is the third time that guard has caught a floating
channel that the older criterion would have published as a working animal.

## 🔴 Two headstages have no ground, and it happened today

Here is the median 60 Hz on the **wire free** inputs of each chip. These are amplifier inputs with
no wire attached, so this table is a statement about hardware and contains no animal information at
all. That is why it is legitimate to compare it across files that hold completely different mice.

| recording | A1 | A2 | B1 | B2 | C1 | C2 | D1 | D2 |
|---|---|---|---|---|---|---|---|---|
| `uid0818` (today) | 5192 | 3952 | **162** | 4132 | 4596 | 3088 | **82** | 5006 |
| `uid0816` | 5609 | **119** | 4613 | 3368 | 3264 | 5097 | 3614 | 1138 |
| `uid0814` | 3785 | **114** | 5592 | 4555 | 2846 | 5153 | 4443 | 1278 |
| `uid0809` | 1611 | 4753 | 3286 | 3601 | 1640 | 4686 | 4871 | 4763 |

A grounded chip sees the room's mains hum on its unconnected inputs, thousands of microvolts of it.
A chip whose ground is not connected rejects mains as common mode and goes silent. **On 14 and 16
August the silent chip was port A slot 2. Today port A slot 2 is normal and port B slot 1 and port
D slot 1 have gone silent instead.**

🔑 **The fault follows whatever was last unplugged and replugged.** That is the same root cause as
[[2026-08-07]]: the ground pin sitting in the wrong position on the
connector, so the ground pad touches nothing. It is fixed by re mating the connector and **needs no
anaesthesia**.

On those two chips, nine of fourteen wire free inputs on B slot 1, and six of fourteen on D slot 1,
have a spectral slope steeper than −1.0. In other words the unconnected inputs look as much like
EEG as the animals do, which is precisely why W-SD B1 and W-SD D1 cannot be judged at all: their
own control has stopped being a control.

⚠️ **VERIFY THE FIX ON THE 60 Hz OF THE WIRE FREE INPUTS, NOT ON IMPEDANCE.** A floating channel
can read a beautifully low and stable impedance. Want to see those two chips back above roughly
1000 µV.

## What this does not say

🛑 **Nobody passes rung 2.** The verdict ladder asks for a longest unbroken usable block of at
least 15 minutes. The longest block here is 6.3 minutes, which is the entire file, so the honest
verdict for all five good mice is **INSUFFICIENT, not PASS**. Contact on this rig has flipped
between open and connected inside a single 23 minute window before, so six minutes cannot show
stability. This is a screen and nothing more.

🛑 **No sleep claim, no architecture, no yield.** Rungs 3 and above were not evaluated and no
hypnogram exists for this cohort.

## Still open

- [ ] **Check the seating of the ground connectors on port B slot 1 and port D slot 1** (Andrea,
      tomorrow morning). Confirm by re running the per chip 60 Hz table, not by an impedance sweep.
- [ ] **Re record for at least an hour** once the two grounds are fixed. If it is going to run over
      a day, start it at ZT0, which is 09:00, with `qc/start_recording_at.py`.
- [ ] **Give `core/criteria.py` a per chip floor option**, and make the falsification check notice
      when the chips disagree with each other.
- [ ] **Write the cohort manifest for W-SD** once the animal identifiers, surgery dates, sex and
      tether arms exist. Until then the eight are known only by batch and rig position.
- [ ] W-SD C2's electrode is open and W-SD B2 has no usable EMG. Both are animal side, so neither
      has an action beyond recording it here.

> [!warning] The analysis scripts behind this page are scratch
> The per chip floor run and the blind 256 channel scan were written outside the repository and are
> not committed. `~/Monitoring_project/eeg-emg-analysis` still has zero git commits, so nothing on
> this page can currently be reproduced from a tagged version of the code.
