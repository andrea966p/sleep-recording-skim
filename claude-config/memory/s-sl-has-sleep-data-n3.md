---
name: s-sl-has-sleep-data-n3
description: "S-SL has sleep architecture as of 2026-09-26 with a paired n=3 at rung 3. Supersedes every earlier claim about this batch's n."
metadata:
  node_type: memory
  type: project
  originSessionId: e12a4d2d-f4ec-4c07-aac7-6552d9960701
  modified: 2026-09-26T04:03:57.083Z
---

⭐ **S-SL has sleep architecture, paired n = 3 at rung 3** — stage 2 and stage 3
run for the first time on 2026-09-26. Scoreable at BOTH protocol timepoints:
**HLBSSL31 (A1), HLBSSL33 (B1), HLBSSL35 (C1)**.

| animal | baseline 09-12 r@1min | endpoint 09-21 r@1min |
|---|---|---|
| HLBSSL31 | 0.532 | 0.632 |
| HLBSSL33 | 0.554 | 0.722 |
| HLBSSL35 | 0.678 | 0.734 |

Day folders: `~/eeg-processed/2026-09-12` (6 files, 3 scoreable),
`2026-09-20` (8, 5), `2026-09-21` (8, 6). NOT in the repo — regenerate with
`pipeline/stage2_split.py` then `stage3_features.py`.

🛑 **This supersedes every earlier claim about S-SL's n.** It is NOT the "n = 2 at
rung 2" reported 2026-09-23, and not n = 1.

🛑 **NO SLEEP CONCLUSION IS WARRANTED.** Baseline is 12.0 h light / 12.06 h dark;
endpoint is **16.0 / 20.71** — dark-heavy because it starts 00:17 mid-dark. Mice
are far more awake in the dark, so whole-file "more wake at recovery" is mostly
WINDOW COMPOSITION. Light-phase only: all three move +1.4 to +4.1 points; in the
dark the direction is inconsistent (−0.6 to +11.6). n = 3, no statistics.

🔑 **First concrete answer to the trimmed-window question**: trimming the endpoint
to its protocol window (09-21 09:00 → 09-22 13:00) drops exactly the 8.71 h of
dark that skews it, giving 16 h light / 12 h dark.

🔴 **`allego_0__uid0920-09-00-07` is the SAME RUN as `uid0921`**, not a separate
recording — 15.145 h, ends 09-21 00:08:48, uid0921 starts 8 min 46 s later. Allego
split it on restart after the mouse problem. Wholly outside the protocol window.

⚠️ The rung 2 verdicts on uid0920 and uid0921 are NOT usable — see
[[contaminated-floor-rejects-good-eeg]]. The 2026-09-23 "attrition" write-up was
retracted 2026-09-26.
