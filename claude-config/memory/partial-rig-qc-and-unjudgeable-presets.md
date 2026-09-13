---
name: partial-rig-qc-and-unjudgeable-presets
description: A partly loaded rig used to be graded on all eight positions, producing UNKNOWN@slot cards that read PASS; and unipolar_lfp has no QC criterion at all, by design.
metadata:
  type: project
---

Found 2026-09-13 by asking what the recording console does with four mice instead of eight.
Partial occupancy itself was always fine — three mice in `A1 C2 D1` strip to six channels,
bit-exact, verified. Two things behind it were not.

🔴 **QC bundles made BEFORE 2026-09-13 for a partially loaded rig contain fabricated rows.**
`cards/ladder.py` defaults to `spec.positions()` — every slot the LAYOUT has, not every slot
the OPERATOR filled — so a four-mouse run came back with eight cards, four named
`UNKNOWN@<slot>`, built from floating amplifier inputs. **Three of them read PASS at rung 2**,
so the noise does not look like noise; it looks like an animal nobody labelled. Ignore every
`UNKNOWN@` row in an older bundle. Fixed by passing `--positions` from the run's occupied
slots. The floor was never at risk: floor sites `/3`–`/16` and `/35`–`/48` belong to no slot.

🔴 **`unipolar_lfp` has NO QC verdict and never will.** Its sites are `/18`–`/23` on
32-channel ports; `CohortSpec` derives the floor as `base+n`–`/16` on a 64-channel chip, so
no wire-free floor exists for that layout. The preset declares `qc: none`; the run records
`qc_not_applicable`, which is NOT `qc_bundle_skipped` (a person waiving a possible check).
`presets.py` refuses a site-based preset that omits the declaration.

🔑 **The rule worth keeping: a guard that can never be satisfied is a guard people learn to
click past.** The old behaviour demanded a manual override on every unipolar run.

✅ Real strip of the only 134-channel file on disk: 58.75 → 13.82 GB, gate A exact over
107,987,328 samples, checksum confirmed OUTSIDE the tool. ⚠️ No unipolar headstage has ever
been connected to this rig, and `8mice_eeg_emg_ecg` has never gone through the console end
to end.

🔴 **A STALE `VERIFIED` ROW IN `eeg-recorder/deploy/uploads.jsonl` MAKES THE UPLOADER SKIP A
REAL FILE.** The manifest is keyed on `(folder/filename, size)` and a VERIFIED row means "do
not upload". On 2026-09-13 a test wrote 8 such rows for files never uploaded, because
`manifest_load(path=MANIFEST)` bound the path as a DEFAULT ARGUMENT at import time and setting
`nas_upload.MANIFEST` did nothing. Now late-bound + `EEG_UPLOAD_MANIFEST`. Check with:
`python3 -c "import json;print(sorted({json.loads(l)['rel'].split('/')[0] for l in open('eeg-recorder/deploy/uploads.jsonl')}))"`
— every folder it names must exist on the share.

✅ **NAS folders are now named by the operator** (2026-09-13):
`03_Data_Mouse/<user>/YYYYMMDD_<batch>_<BSR|RSR|SDR>/` with files
`..._<N>mice_data.xdat`. Date = the START date, from the uid (already local). Mixed
conditions join codes (`BSR-SDR`). Rename is **NAS-side only** — the local stripped copy keeps
its Allego name, because the strip is idempotent on that name. Blank batch name = old layout.

Full write-ups: vault `02-procedures/eeg-recording-console.md` §2.4–2.5,
`02-procedures/installation/xdat-channel-stripping.md` §4b,
`01-infrastructure/eeg-recorder/pipeline-architecture.md` §5 (defects 7 and 8).
Related: [[skim-nas-smb-and-channel-stripper]], [[cohort-identity-every-run-is-new-mice]],
[[animal-card-verdict-ladder]].
