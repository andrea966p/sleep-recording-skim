---
tags: [experiment, eeg, emg, S-SL, connection, audit]
created: 2026-09-23
status: complete
recordings: [allego_0__uid0912-08-55-18, allego_0__uid0920-09-00-07, allego_0__uid0921-00-17-34]
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
> ⭐ **What it does say: attrition, and WHEN it happened.** Five of eight
> positions were connected at baseline; **two** were still connected at the
> recovery endpoint eight days later. The two that survived, **B1/HLBSSL33 and
> C2/HLBSSL39**, are the paired set — n = 2, at rung 2 only.
>
> 🔴 Three positions went from excellent to nothing: A1 **90.6% → 0.0%**, C1
> **87.0% → 0.0%**, B2 **88.0% → 23.5%**.
>
> 🔑 **The collapse was already complete before the recovery run started.**
> A third recording, `allego_0__uid0920-09-00-07`, was added to this cohort on
> 2026-09-26 and carded for the first time. It is the run's own first segment —
> Sunday 09-20 09:00, 15.145 h — and on it A1, C1 and D1 already read 0.0% and
> B2 already reads 26.7%. Across the recovery run itself every position is
> stable within a few points. **Nothing failed during recovery; everything that
> failed had already failed in the eight-day gap between 09-12 and 09-20.**

## The two recordings

| | baseline | recovery, segment 1 | recovery, segment 2 |
|---|---|---|---|
| recording | `allego_0__uid0912-08-55-18` | `allego_0__uid0920-09-00-07` | `allego_0__uid0921-00-17-34` |
| window as run | 2026-09-12 08:55 → 09-13 08:59 | 2026-09-20 09:00 → 09-21 00:08 | 2026-09-21 00:17 → 09-22 13:00 |
| duration | **24.065 h** | **15.145 h** | **36.707 h** |
| protocol window | 24 h, ZT0 → ZT0 ✅ | none — wholly outside it | 28 h, 09-21 09:00 → 09-22 13:00 |
| `thresholds_hash` | `c54b0f83af37` | `01e11630dcbf` | `01e11630dcbf` |

> [!note] The two recovery files are ONE run that Allego split
> `uid0920` ends 09-21 00:08:48 and `uid0921` begins 00:17:34 — a gap of 8 min
> 46 s. The mouse problem on the Sunday is why the run was restarted and why
> sampling slipped from the Monday to the Tuesday. `uid0920` is reported here
> because it dates the attrition; **none of it belongs in the recovery numbers**,
> since the protocol window lies wholly inside `uid0921`.

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

## Recovery segment 1 — 2026-09-20, 15.145 h, outside the window

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| C2 | HLBSSL39 | ✅ PASS | 87.3% | 64.3 min |
| B1 | HLBSSL33 | ✅ PASS | 83.0% | 42.7 min |
| B2 | HLBSSL34 | ❌ FAIL | 26.7% | 5.8 min |
| A2 | HLBSSL32 | ⬜ UNJUDGEABLE | — | — |
| A1 | HLBSSL31 | ❌ FAIL | 0.0% | 0.0 min |
| C1 | HLBSSL35 | ❌ FAIL | 0.0% | 0.0 min |
| D1 | HLBSSL40 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.0 min |

🔑 **This is the table that dates the attrition.** It was taken on the Sunday
morning, before the recovery run proper, and A1, C1 and D1 already read 0.0%
while B2 already reads 26.7%. Every loss visible at the endpoint is already
here.

⚠️ **A2 is UNJUDGEABLE here and FAIL on the other two recordings.** Its chip read
ungrounded for this segment, so rung 2 could not be asked — which is not the same
as answering no. See [[03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode]].

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

| pos | animal | 09-12 baseline | 09-20 segment 1 | 09-21 segment 2 | |
|---|---|---|---|---|---|
| B1 | HLBSSL33 | 73.8% | 83.0% | **78.2%** | ✅ held throughout |
| C2 | HLBSSL39 | 79.8% | 87.3% | **82.7%** | ✅ held throughout |
| B2 | HLBSSL34 | 88.0% | **26.7%** | 23.5% | 🔴 degraded BEFORE recovery |
| A1 | HLBSSL31 | 90.6% | **0.0%** | 0.0% | 🔴 lost BEFORE recovery |
| C1 | HLBSSL35 | 87.0% | **0.0%** | 0.0% | 🔴 lost BEFORE recovery |
| D1 | HLBSSL40 | 66.9% (FAIL) | 0.0% | 0.0% | ❌ never recovered |
| D2 | HLBSSL38 | 0.0% | 0.0% | 0.0% | ❌ never recovered |
| A2 | HLBSSL32 | 0.0% | UNJUDGEABLE | 0.0% | ❌ never recovered |

⭐ **Read the middle column first.** Every change happened between 09-12 and
09-20, in the eight days when nothing was being recorded. Between the Sunday
segment and the Monday-to-Tuesday endpoint, the largest move on any position is
B1's 83.0% → 78.2%. The recovery run did not damage anything; it recorded a rig
that had already lost six of eight positions.

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

⚠️ **The card sets were regenerated in two passes.** On 2026-09-23
`allego_0__uid0921-00-17-34` was added to `cohorts/S-SL.yaml`, having been absent
from it entirely; its cards had lived under the throwaway console cohort
`auto-a91ef30eab66`, and the verdicts were identical either way. On 2026-09-26
`allego_0__uid0920-09-00-07` was added and **carded under this cohort for the
first time** — that is the segment-1 table above, and it is new evidence, not a
refile.

✅ **Every `auto-*` console cohort has now been retired from `cards/out/`.** Seven
existed. Two duplicated a named cohort, four were 0.6-to-8-minute aborted starts,
and one — `auto-df0f5562873b` — held this recording. 🔴 The `uid0917` set under
`auto-6255ffcf2575` was NOT a duplicate but a **stale** set that reached only
rung 3 and carried a nonexistent animal id, `HLBWSL7`; the current `cards/out/W-SL/`
set reaches rung 4 and names `HLBWSL27`. Deleting it removed that ghost from disk.

🛑 `allego_0__uid0913-11-20-07` is deliberately NOT in this manifest: 8.4 minutes,
an aborted start, no result.

Not checked: figures (none drawn), stage 3, and the failure-signature
classification.

## Related

[[02-procedures/CANONICAL-recording-windows-and-protocol]] ·
[[02-procedures/CANONICAL-recording-naming-and-inventory]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] ·
[[05-experiments/completed/2026-09-18-W-SL-light-phase-sleep]]
