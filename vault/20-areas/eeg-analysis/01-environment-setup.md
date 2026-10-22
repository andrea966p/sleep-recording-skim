---
type: procedure
area: eeg-analysis
status: active
status-note: "complete"
tags: [procedure, eeg, analysis, python, environment, onboarding]
created: 2026-06-30
---

# 01 — Environment Setup (the one analysis venv)

> [!abstract] TL;DR
> Make ONE Python virtual environment for all EEG analysis. Install numpy, scipy, matplotlib, pandas, pyedflib into it. Use that venv's python for every script in this section. This avoids the version clashes that bit us (system matplotlib built for numpy 1.x crashing under numpy 2.x). Hub: [[_eeg-analysis-hub]].

## Why a dedicated venv

There are several Pythons on this machine and they fight:
- **Project venv** `/opt/neurosurveillance/venv` — numpy 2.x, but its **scipy is broken** and its matplotlib clashes. Fine for the daemon, not for analysis.
- **System** `/usr/bin/python3` — numpy 1.26, scipy 1.11, matplotlib — works, but old and shared with the OS (don't pip into it).

One clean venv ends the confusion: numpy 2.x + scipy + matplotlib + pandas + pyedflib that all agree.

## Create it (once)

```bash
python3 -m venv /home/skimlab/eeg-analysis-venv
/home/skimlab/eeg-analysis-venv/bin/pip install --upgrade pip
/home/skimlab/eeg-analysis-venv/bin/pip install numpy scipy matplotlib pandas pyedflib
```

Verify (all import together):

```bash
/home/skimlab/eeg-analysis-venv/bin/python -c \
 "import numpy,scipy,matplotlib,pandas,pyedflib; \
  print(numpy.__version__,scipy.__version__,matplotlib.__version__,pandas.__version__,pyedflib.__version__)"
```

Known-good set (verified 2026-06-30):
`numpy 2.5.0 · scipy 1.18.0 · matplotlib 3.11.0 · pandas 3.0.3 · pyedflib 0.1.42`

## Use it

Always call this interpreter; a handy alias:

```bash
alias eeg-py=/home/skimlab/eeg-analysis-venv/bin/python
```

Run scripts **from the scripts folder** (so `import xdat_io` resolves):

```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault/02-procedures/eeg-data-analysis/scripts
/home/skimlab/eeg-analysis-venv/bin/python qc_report.py <recording_base>
```

> [!note] Pitfalls we already hit
> - Do **not** mix the project venv (numpy 2) with the **system apt matplotlib** (built for numpy 1) — it aborts with a NumPy 1.x/2.x compile error. Installing matplotlib *into* this venv fixes it.
> - `pyedflib` installs fine under numpy 2 (0.1.42+).
> - If you ever see `RuntimeWarning: invalid value` from `get_metrics` in the *acquisition* SDK, that's a different env (numpy-2 `np.NAN`) — not this analysis venv.

## Related
- [[_eeg-analysis-hub]] · [[03-scripts-and-usage]]
