---
name: skim-nas-per-mouse-csv-layout
description: "Since 2026-09-29 the recorder exports one CSV per mouse to the SKIM NAS (02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<date>_<ID>_<B|R>/), trimmed 24 h windows, 64 folders rebuilt 2026-09-30. Detail in the vault"
metadata:
  node_type: memory
  type: project
  originSessionId: 533bb1b2-75c7-42ef-bdb1-704e3dd70a51
  modified: 2026-10-22T00:00:00.000Z
---

Since 2026-09-29 the chain is QC, STRIP, EXPORT (`eeg-emg-analysis/export/per_mouse_csv.py`), UPLOAD: one `<date>_<MOUSEID>_<B|R>.csv` + `.info.json` per mouse in `02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/` (batch name required). CSVs are trimmed to 09:00-09:00 (24 h; SD recovery 13:00-09:00, 20 h). 64 folders / 291 GB rebuilt and audited 2026-09-30; each `info.json` carries the ladder `qc` verdict (the CSV has no wire-free floor). Scoreable at both timepoints: HLBWSD08, HLBWSL24, HLBSSL33.

Details: [[per-mouse-csv-format]] · [[skim-nas-smb-and-upload]] · [[2026-09-30-scoreable-mice-on-the-24h-windows]] · [[backup-architecture-three-destinations]]

- Run stage 3 and the ladder under `/usr/bin/python3`: the recorder venv's NumPy 2 breaks the system SciPy.
- Pending when written (2026-09-30), check the vault before assuming: a real 2-minute UI run with headstages connected, and the commit.
- The analysis reads the per-mouse CSV, NEVER the xdat. A batch name is required in the folder path.
