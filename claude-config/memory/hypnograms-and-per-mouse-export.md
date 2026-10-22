---
name: hypnograms-and-per-mouse-export
description: "2026-08-21/22 first hypnograms (A1, A2, D2 usable; C2, D1 rejected; B2 no states) and the per-mouse raw export. Rules: r@1min decides (bar 0.30), never report REM %, everything provisional, setsid not nohup."
metadata:
  type: project
---

**First hypnograms the project ever produced, from the 39.7 h run:** A1 (W 43.3 / N 52.1, r@1min 0.495), A2 (52.3 / 43.3, 0.592), D2 (54.2 / 42.8, 0.446), REM-from-NREM 70.9-82.4 % above their shuffled nulls; C2 (r 0.11) and D1 (r 0.001) REJECT; B2 = NO STATES (EEG good, EMG open, WAKE is an Otsu cut on log EMG rms); B1 and C1 animals were gone with their tethers. Per-mouse export `~/eeg-processed/per-mouse/<recording>/` (.mat + .txt + hypnogram + `_VERDICT.txt`; not EDF).

Details: [[2026-08-21-39h-run-score]]; export procedure [[per-mouse-export]]

🛑 `r@1min` IS THE NUMBER THAT DECIDES IT (bar 0.30). 🛑 REM % in the summaries is FIXED BY CONSTRUCTION (top 20 % of sleep): NEVER report it. 🛑 ALL PROVISIONAL: no human has scored a single epoch, the kappa is still the gate; do NOT invent an EEG-only stager. 🔴 `nohup` is NOT enough for a long job, use `setsid` (a shell timeout killed an export and left a 0-byte .mat). Verify an export against source (counts, spread-point bytes); a partial write looks identical in `ls`. `stage2_split.py` needs `--all-verdicts` or OPEN positions are silently skipped. `radiens` is ONLY in the daemon venv; analysis runs under `/usr/bin/python3` (it is runnable; the earlier "unrunnable" claim was my error).

Rules:
🛑 **DID NOT invent an EEG-only stager** — published but not implemented/validated here.
🛑 **REM % in the summaries is FIXED BY CONSTRUCTION (top 20% of sleep) — NEVER report it.**
🛑 **ALL PROVISIONAL — no human has scored a single epoch. The kappa is still the gate.**
