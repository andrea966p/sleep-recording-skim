# nanotag

Analysis code for the HLB SOD1 studies recorded with implanted Kissei nanotag loggers
(activity + temperature, no EEG). Procedure, file layout and decisions:
`vault/02-procedures/nanotag-recording-and-analysis.md`.

```
analysis/nta_qc.py      parse a nanotagViewer CSV export, QC, immobility sleep scoring (stdlib only)
analysis/cohort.py      HLBNSL cohort: windows, Run 1 + Run 2 merge, sleep / bout / rhythm / temperature, figures
analysis/export_nas.py  per-mouse CSV + info.json + raw/ staging for the SKIM NAS
analysis/plots.py       early single-file figures (2026-09-09 pilot)
report/build.sh         rebuild report/methods .docx and figures .pptx from the HTML pages
```

```bash
/usr/bin/python3 nanotag/analysis/cohort.py --demo
/usr/bin/python3 nanotag/analysis/cohort.py ~/Desktop/Andrea/nanotag/"nanotag recording data/HLBNSL"
nanotag/report/build.sh
```

Raw data stay outside git (`.gitignore`): on the SKIM workstation under
`~/Desktop/Andrea/nanotag/nanotag recording data/`, and on the SKIM NAS under
`02_Data_Sleep/andrea/HLBNSSL`, `HLBNWSL`. Outputs go to `analysis/out/` (ignored).
