---
tags: [experiment, eeg, emg, S-SL, connection, audit]
created: 2026-09-23
status: complete
recordings: [allego_0__uid0912-08-55-18, allego_0__uid0921-00-17-34]
cohort: S-SL
---

# S-SL: five of eight connected at baseline, two of eight eight days later

> [!abstract] TL;DR
> The S-SL batch had **no page in this vault at all** until now, although both of
> its recordings have existed for weeks. This is the connection audit, and it
> stops at connection deliberately.
>
> 🛑 **There is no sleep result here, and none exists.** Rung 3 is INSUFFICIENT on
> all sixteen cards with the same reason — `no stage 3 output for this
> animal-recording`. `pipeline/stage3_features.py` has never been run on either
> day folder. Nothing on this page says anything about sleep.
>
> ⭐ **What it does say: attrition.** Five of eight positions were connected at
> baseline; **two** were still connected at the recovery endpoint eight days
> later. The two that survived, **B1/HLBSSL33 and C2/HLBSSL39**, are the paired
> set — n = 2, at rung 2 only.
>
> 🔴 Three positions went from excellent to nothing: A1 **90.6% → 0.0%**, C1
> **87.0% → 0.0%**, B2 **88.0% → 23.5%**.

## The two recordings

| | baseline | recovery |
|---|---|---|
| recording | `allego_0__uid0912-08-55-18` | `allego_0__uid0921-00-17-34` |
| window as run | 2026-09-12 08:55 → 09-13 08:59 | 2026-09-21 00:17 → 09-22 13:00 |
| duration | **24.065 h** | **36.707 h** |
| protocol window | 24 h, ZT0 → ZT0 ✅ | 28 h, 09-21 09:00 → 09-22 13:00 |
| `thresholds_hash` | `c54b0f83af37` | `01e11630dcbf` |

> [!warning] The recovery cards cover the WHOLE file, not the protocol window
> The canonical window is the **last 28 h** of that 36.707 h recording — 09-21
> 09:00 to 09-22 13:00 — which is unbroken inside it. The cards were computed
> over all 36.707 h, so **every recovery percentage below includes 8.71 h that
> are outside the window**. They are reported as computed, not as the protocol
> window. See [[02-procedures/CANONICAL-recording-windows-and-protocol]].
>
> Why the file is longer than the protocol: sampling slipped from 09-21 to 09-22
> because of the mouse problem, and the recording was extended to meet it.

## Baseline — 2026-09-12, 24.065 h

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| A1 | HLBSSL31 | ✅ PASS | 90.6% | 94.8 min |
| B2 | HLBSSL34 | ✅ PASS | 88.0% | 51.2 min |
| C1 | HLBSSL35 | ✅ PASS | 87.0% | 72.7 min |
| C2 | HLBSSL39 | ✅ PASS | 79.8% | 67.3 min |
| B1 | HLBSSL33 | ✅ PASS | 73.8% | 53.3 min |
| D1 | HLBSSL40 | ❌ FAIL | 66.9% | **13.7 min** |
| A2 | HLBSSL32 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.2 min |

⚠️ **D1 is the row to read carefully.** At 66.9% usable it looks comparable with
B1's 73.8%, and it fails — because its longest unbroken block is 13.7 min against
a 15 minute bar. Usable percentage and scoreability are different questions, and
D1 is where they disagree. A2 and D2 are not marginal; they are flat zero.

## Recovery — 2026-09-21 to 09-22, 36.707 h as computed

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| C2 | HLBSSL39 | ✅ PASS | 82.7% | 52.8 min |
| B1 | HLBSSL33 | ✅ PASS | 78.2% | 44.7 min |
| B2 | HLBSSL34 | ❌ FAIL | 23.5% | 8.0 min |
| A1 | HLBSSL31 | ❌ FAIL | 0.0% | 0.0 min |
| A2 | HLBSSL32 | ❌ FAIL | 0.0% | 0.2 min |
| C1 | HLBSSL35 | ❌ FAIL | 0.0% | 0.0 min |
| D1 | HLBSSL40 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.0 min |

## The attrition

| pos | animal | baseline | recovery | |
|---|---|---|---|---|
| B1 | HLBSSL33 | 73.8% | **78.2%** | ✅ held, and improved |
| C2 | HLBSSL39 | 79.8% | **82.7%** | ✅ held, and improved |
| B2 | HLBSSL34 | 88.0% | 23.5% | 🔴 degraded past the bar |
| A1 | HLBSSL31 | 90.6% | 0.0% | 🔴 total loss |
| C1 | HLBSSL35 | 87.0% | 0.0% | 🔴 total loss |
| A2, D1, D2 | SSL32, 40, 38 | already failing | 0.0% | ❌ never recovered |

🔑 **The two that survived are the two that were mid-table at baseline, not the
best.** A1 and C1 were the strongest positions on 09-12 at 90.6% and 87.0%, and
both read exactly 0.0% eight days later. B1 and C2 sat at 73.8% and 79.8% and
both came back slightly *higher*. Baseline connection quality did not predict
which positions would last — five positions were connected and the two that
survived were not the two that looked best.

## What this does not support

- 🛑 **No sleep architecture, for either recording.** Rung 3 is INSUFFICIENT on
  all sixteen cards. No hypnogram, no NREM percentage, no `r@1min` exists for any
  S-SL animal. Running `pipeline/stage3_features.py` on both day folders is the
  prerequisite, and it has not been done.
- ⚠️ **n = 2 here is not comparable with n = 1 elsewhere.** W-SL's n = 1 is at
  rung 3, scoreability. This n = 2 is at rung 2, connection — a lower bar. The
  numbers are not interchangeable and a larger n at a lower rung is not a better
  result.
- ⚠️ **The two recordings were judged under different thresholds**
  (`c54b0f83af37` against `01e11630dcbf`) and different code revisions. The
  baseline-to-recovery deltas above are therefore not strictly like-for-like.
  Re-carding the baseline under the current thresholds would settle it.
- ⚠️ **Recovery percentages include 8.71 h outside the protocol window**, as above.
- ⚠️ **No husbandry.** `cohorts/S-SL.yaml` deliberately carries no sex, date of
  birth, surgery date, weights or tether date, so no age, weight or
  days-post-surgery can be reported for any animal here.
- ❌ **Nothing here explains WHY three positions went to zero.** The failure
  signature work that distinguishes a bent tether from a severed one was not run
  on these recordings.

## Provenance

Cards at `eeg-emg-analysis/cards/out/S-SL/`, generated by `cards/ladder.py` against
`cohorts/S-SL.yaml`. Both recordings are stripped to 16 channels, bit-exact, and
on the SKIM NAS as `20260912_HLBSSL_BSR/` and `20260921_HLBSSL_RSR/`; raw is in S3.

⚠️ **Both card sets were regenerated on 2026-09-23 and the recovery's are new to
this cohort.** Until then `allego_0__uid0921-00-17-34` was absent from
`cohorts/S-SL.yaml` entirely, and its cards lived under the throwaway console
cohort `auto-a91ef30eab66`. The verdicts are identical either way — only the
cohort they are filed under changed. `allego_0__uid0913-11-20-07` and
`allego_0__uid0920-09-00-07` are still in that state.

Not checked: figures (none drawn), stage 3, and the failure-signature
classification.

## Related

[[02-procedures/CANONICAL-recording-windows-and-protocol]] ·
[[02-procedures/CANONICAL-recording-naming-and-inventory]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] ·
[[05-experiments/completed/2026-09-18-W-SL-light-phase-sleep]]
