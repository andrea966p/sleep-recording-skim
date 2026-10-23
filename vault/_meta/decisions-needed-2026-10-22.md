---
summary: "Open questions from the 2026-10-22 vault rehaul; answered by Andrea on 2026-10-23 except the few still open"
---

# Decisions needed (from the 2026-10-22 rehaul)

Andrea answered on 2026-10-23 ([[2026-10-23]]). Each answer is now in the hub that owns it
and in the per-area log in `_meta/contradictions/`.

## Still open

- **SC-4:** handbook convention C12 (one-sided arousal in NREM): NR or W, or a delta threshold? [[_sleep-scoring-hub]]
- **HS-8:** the SOD1 sheet request route, until the professor approves the Claude for Sheets connector. [[_hlb-sod1-hub]]
- **Pinnacle:** ask Pinnacle about the TTL pulse (premium software alone, their TTL generator, or our own). [[_rig-expansion-hub]]
- **GND bus:** where the bus connects (perhaps the metal rack). [[_eeg-rig-hub]]

## Work these answers created

- Measure the current grounds and replace the 800 µV gate; redesign the −1.90 slope cut. [[_eeg-analysis-hub]]
- Shrink the headmount drawing to the 6 mm limit. [[_rig-expansion-hub]]
- Rotate the Slack webhook; remove `skimworkstation-1` from the tailnet. [[_computing-hub]]
- Refuse overlapping recording reservations when they are booked. [[_recording-console-hub]]
- Check on the SKIM workstation whether SleepStager's features notch (backlog item 1) is at 60 Hz. [[sleepstager-changes-and-backlog]]
- Later: move acquisition from Allego to the Open Ephys GUI. [[_allego-hub]]

## Answers, 2026-10-23

| Code | Answer | Filed in |
|---|---|---|
| EA-10, ER-4, NU-6 | Replace the 800 µV ground gate by measuring the current (post-fix) grounds; to do. | [[_eeg-analysis-hub]] |
| EA-11 | Yes: redesign the −1.90 floor-slope cut; to do. | [[_eeg-analysis-hub]] |
| ER-5, AC-1, AC-10 | Keep Allego without `--disable-gpu`; no Chan-height test. Later: move to the Open Ephys GUI with our XDAQ (a big switch for the recorder code and the daemon). Procedures and `rig-check.sh` updated. | [[_allego-hub]] |
| ER-11 | Planned GND bus: headstages (in their 3D-printed plastic enclosures) inside a closed aluminium box, a wire from the box to the bus; where the bus connects (perhaps the metal rack) is open. | [[_eeg-rig-hub]] |
| ER-3 | No separate Sys GND on the Gen-1, only the chassis GND. | [[_eeg-rig-hub]] |
| NU-1 | The foil busbar is still not fitted. | [[_noise-hunt-hub]] |
| noise trials | Andrea's own decision: no more long tests chasing a ghost; the noise is considered fixed. | [[_noise-hunt-hub]] |
| RB-15 | Close the pad 7 test (done). | [[_rig-bringup-hub]] |
| AC-9 | Recording stays global; several people must be able to queue schedules for following dates. Already works; refusing overlaps at booking is the open item. | [[_recording-console-hub]] |
| HS-8 | Still open: the Claude for Sheets connector is not yet approved by the professor. | [[_hlb-sod1-hub]] |
| HS-10 | Yes: SOD1 or water administration and monitoring start after the baseline recording. | [[hlb-sod1-design]] |
| SC-4 (scoring) | Not sure yet: stays open. | [[_sleep-scoring-hub]] |
| SC-5 (scoring) | The 60 Hz mains notch is our own modification of the fork; no professor approval needed. | [[_sleep-scoring-hub]] |
| SC-7 (scoring) | Off-site copies of the nanotag raw data exist. | [[_nanotag-hub]] |
| RX-1 | Pinnacle runs on a separate Windows PC (Sirenia does not support Linux); later maybe our own Linux interface, depending on the premium software (sleep scoring, video sync). Ask Pinnacle whether the premium software alone exposes a TTL pulse or their TTL generator (or our own) is needed. | [[_rig-expansion-hub]] |
| RX-3 | The 6 mm headmount limit is real (average B6 skull and surgical area); the 6.4 x 7.8 mm drawing must shrink. | [[_rig-expansion-hub]] |
| RX-5 | Model code 8474-HR-SE4-C confirmed. | [[pinnacle-wireless-plan-status]] |
| RX-8, RX-12, RS-4 | Not important now: parked. | [[_rig-expansion-hub]] |
| ST-9 | Rotate the Slack webhook: steps in the computing hub (needs Slack and sudo). | [[_computing-hub]] |
| ST-1 | No AWS budget alert needed. | [[_data-storage-hub]] |
| ST-10 | Remove `skimworkstation-1` from the tailnet (Tailscale admin console). | [[_computing-hub]] |
| VN-2 | Later, when video work resumes. | [[_video-nvr-hub]] |

## Housekeeping

- ✅ 2026-10-23: `_JOURNAL-INDEX.md` moved to `90-archive/`; [[journal.base]] is the journal index.
- ✅ 2026-10-23: the six stale memory files were deleted (verbatim copies stay in `90-archive/claude-memory-2026-10-22/`).
- Outside the vault, not changed: `~/eeg-analysis-venv`'s editable install and the `FIGURE_STYLE_DIR` default in `eeg-emg-analysis/core/paths.py` still point at the deleted `~/Monitoring_project`.
- ✅ 2026-10-23: the Obsidian Local REST API plugin was uninstalled (nothing used it; the vault MCP reads the files directly), so its old key is dead. [[2026-10-23]]
