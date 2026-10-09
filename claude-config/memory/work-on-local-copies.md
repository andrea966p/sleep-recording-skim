---
name: work-on-local-copies
description: Andrea works on local copies of recordings; the SKIM NAS is storage only, never a working directory
metadata:
  type: feedback
---
Recordings are copied from /mnt/skimnas/02_Data_Sleep/... to ~/sleep-data/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSE>_<B|R>/ and
staged there; the NAS is storage only (Andrea, 2026-10-07).

**Why:** SleepStager writes outputs beside a recording (and used to move loose files), and the NAS CSV is the declared single source
of truth; working on it risks the canonical tree.
**How to apply:** never open or stage a file straight from /mnt/skimnas; copy, check sha256 against info.json upload.sha256_remote,
then work locally. Where finished scorings go back on the NAS is still undecided.
