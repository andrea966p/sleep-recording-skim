# nanotag

Analysis code for the HLB SOD1 studies recorded with implanted Kissei nanotag loggers
(activity + temperature, no EEG). Procedure, file layout and decisions:
`vault/20-areas/nanotag/nanotag-recording-and-analysis.md`.

```
analysis/nta_qc.py      parse a nanotagViewer CSV export, QC, immobility sleep scoring (stdlib only)
analysis/cohort.py      HLBNSL cohort: windows, Run 1 + Run 2 merge, sleep / bout / rhythm / temperature, figures
analysis/cohort_sd.py   NS-SD / NW-SD cohort: reuses cohort.py; Run 1 baseline vs SOD1 (Run 2 / SD not yet)
analysis/export_nas.py  per-mouse CSV + info.json + raw/ staging for the SKIM NAS
analysis/plots.py       early single-file figures (2026-09-09 pilot)
report/build.sh         rebuild report/methods .docx and figures .pptx from the HTML pages
```

Figures need matplotlib >= 3.7 (`fig.legend(loc="outside ...")`); Ubuntu 24.04's `python3-matplotlib` is 3.6.3 and
fails at the first summary figure. Where the system one is too old, use a venv (office PC, 2026-10-31):

```bash
uv venv -p /usr/bin/python3 ~/.venvs/nanotag
uv pip install -p ~/.venvs/nanotag/bin/python matplotlib==3.11.2 numpy==2.5.4
```

and run the commands below with `~/.venvs/nanotag/bin/python` in place of `/usr/bin/python3`.

```bash
/usr/bin/python3 nanotag/analysis/cohort.py --demo
/usr/bin/python3 nanotag/analysis/cohort.py ~/Desktop/Andrea/nanotag/"nanotag recording data/HLBNSL"
nanotag/report/build.sh
```

Raw data stay outside git (`.gitignore`): on the SKIM workstation under
`~/Desktop/Andrea/nanotag/nanotag recording data/`, and on the SKIM NAS under
`02_Data_Sleep/andrea/HLBNSSL`, `HLBNWSL`. Outputs go to `analysis/out/` (ignored).
