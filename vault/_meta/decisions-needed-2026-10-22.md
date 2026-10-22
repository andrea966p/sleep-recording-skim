---
summary: "Open questions only Andrea (or the professor) can settle, collected during the 2026-10-22 vault rehaul"
---

# Decisions needed (from the 2026-10-22 rehaul)

Every row was found while checking the vault against its sources. None is a vault bug: each
needs a person who knows. Codes point to the per-area logs in `_meta/contradictions/`.
When you settle one, write the answer in the hub (or a decision note) and mark the row
settled in its log.

## Recording and the rig

| Code | Question | Where |
|---|---|---|
| EA-10, ER-4, NU-6 | The 800 µV ground gate (`FLOOR_MIN_HUM_UV`) now calls every chip UNJUDGEABLE after the 10-07 earthing fix. Replace it how (the era-dated option c)? | [[_eeg-analysis-hub]] |
| EA-11 | The −1.90 floor-slope cut no longer separates contaminated floors after 10-07. Redesign? | [[_eeg-analysis-hub]] |
| ER-5, AC-1, AC-10 | Keep Allego without `--disable-gpu` (Monitor works, Mesa crash risk) and update `rig-check.sh`, which still warns? Test Chan height 30 with the flag? | [[_allego-hub]] |
| ER-11 | Bond the headstage foil to the Gen-1 chassis GND? | [[_eeg-rig-hub]] |
| ER-3 | Does the Gen-1 have a separate Sys GND besides the chassis GND? (low) | [[_eeg-rig-hub]] |
| NU-1 | Was the foil earth busbar fitted on 10-07, or is it still to come? | [[_noise-hunt-hub]] |
| (new) | "No more environmental-noise trials or spending": your rule, or Claude's 10-06 recommendation? The vault only records the recommendation. | [[2026-10-06-noise-hunt-verdict]] |
| RB-15 | Close `experiment-pad7-floating-input-B1` (its animal is gone) or retarget it? | [[_rig-bringup-hub]] |
| AC-9 | `multi-user-independent-recording-schedules`: still planned, or done (recording is global)? | [[_recording-console-hub]] |

## SOD1 study and scoring

| Code | Question | Where |
|---|---|---|
| HS-8 | What replaced the TSV paste route for SOD1 sheet changes? | [[sod1-sheet-change-log-workflow]] |
| HS-10 | "SOD from 3 days after baseline" means after a 3-day baseline? (low) | [[hlb-sod1-design]] |
| SC-4 | Handbook convention C12 (one-sided arousal in NREM): NR or W, or a delta threshold? | [[_sleep-scoring-hub]] |
| SC-5 | Feature notch 50 Hz vs 60 Hz mains (the professor decides; epochs up to 8441 were scored with 50 Hz). | [[_sleep-scoring-hub]] |
| SC-7 | Is there still no off-site copy of the nanotag raw files? | [[_nanotag-hub]] |

## Rig expansion

| Code | Question | Where |
|---|---|---|
| RX-1 | Does Pinnacle wireless replace the XDAQ 32-mouse route, or run beside it? | [[_rig-expansion-hub]] |
| RX-3 | Real headmount size limit: 6 mm, or larger (the board is drawn at 6.4 x 7.8 mm)? | [[pinnacle-wireless-plan-status]] |
| RX-5 | Confirm the head-unit model code (8474-HR-SE4-C) against the quote. | [[pinnacle-wireless-plan-status]] |
| RX-8 | Is "proven on our bench" dropped as a differentiator, or kept? | [[2026-07-24-daq-32-mouse-final-comparison]] |
| RX-12, RS-4 | One PC or two for two XDAQ boxes (Kontex's answer)? | [[_rig-expansion-hub]] |

## Machines, storage, video

| Code | Question | Where |
|---|---|---|
| ST-9 | Rotate the Slack webhook that sat in plain text in a note (still in git history; the same URL is in `/etc/netdata/health_alarm_notify.conf`, and `nvr-mqtt-slack` may use it, so a new one must be installed before the old is revoked). | [[_computing-hub]] |
| ST-1 | Does an AWS budget alert exist? (the S3 note says yes, memory says it was deleted 2026-09-20) | [[_data-storage-hub]] |
| ST-10 | Is `skimworkstation-1` a duplicate tailnet registration to remove? | [[_computing-hub]] |
| VN-2 | Turn `sessions.auto_start` back on when video resumes? | [[_video-nvr-hub]] |

## Housekeeping left from the rehaul

- Archive `04-journal/_JOURNAL-INDEX.md` now that [[journal.base]] lists every day? (It is kept until you are happy with the Bases view.)
- Delete the six memory files marked stale (they are archived verbatim): `eeg-analysis-codebase`, `eeg-qc-2026-07-14-two-runs`, `eeg-rig-current-state`, `project_multiuser_recording_schedules`, `staging-circadian-validation-2026-08-07`, `reference_vault_07_decisions`.
- Outside the vault, not changed: `~/eeg-analysis-venv`'s editable install and the `FIGURE_STYLE_DIR` default in `eeg-emg-analysis/core/paths.py` still point at the deleted `~/Monitoring_project`.
- Regenerate the Obsidian Local REST API key (its old key was in git history; the settings file is no longer tracked).
