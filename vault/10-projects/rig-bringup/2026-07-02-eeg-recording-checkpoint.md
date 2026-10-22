---
type: decision
area: rig-bringup
status: done
status-note: "active"
tags:
  - decision
  - checkpoint
  - eeg
  - emg
  - council
  - grounding
created: 2026-07-02
audience: team
supersedes-status-in:
  - 03-troubleshooting/incidents/2026-06-28-eeg-recording-troubleshooting-report.md
---

# EEG Recording — Checkpoint & Council Review (2026-07-02)

> [!warning] Updated 2026-10-22: Its "no validated recording yet" status was overtaken: first scoreable sleep on 2026-08-01 [[2026-08-01-channel-mapping-correction-first-sleep]], then 48.19 h of one control mouse with 47.09 h of usable EEG and a state-dependent EMG [[2026-08-11-a2-control-48h-reference-profile]]. The frontmatter status-note "active" is stale: this is a dated record.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** An honest snapshot of the mouse sleep-EEG/EMG rig after ~2 weeks of intense troubleshooting, plus a plan for how to continue. It was produced by running the project through a 5-advisor "LLM council" (Contrarian, First-Principles, Expansionist, Outsider, Executor) that critiqued the work and each other.
> **Why it exists.** The rig is now electronically cleared, and it's tempting to declare victory and scale to 8 mice. The council's blunt finding: **we do not yet have a single validated recording** (one 4.5 h EEG-only session with dead EMG is an existence proof, not validation). This doc resets the goal to the right bar before more animals are cut.
> **How to read it.** Start with §1 (the truth), then §3 (what to do). §2 is the council verdict; §4 is the criteria that define "done"; §5 is the fix already applied to the analysis code.

Continues [[2026-07-01]] and the narrative report [[2026-06-28-eeg-recording-troubleshooting-report]]. This checkpoint is now the single source of truth for "where we are and what's next" on the EEG side.

---

## 1. State of truth (no rounding up)

- **Rig electronics: cleared.** Chip = **RHD2216 bipolar** (single 16-ch chip; `REF` empty by design; Allego shows 32/port because the port reserves 2 MISO — 2nd slot empty → natives 16–31 = quiet floor). **Bottom SPI socket works, top socket dead** on both HDMI adapters (root cause of the multi-day "won't enumerate" saga). **Dual headstage = 64 ch works**, each mouse self-grounds via green → brass bus → C3410 `GND`.
- **Recordings that count: ZERO.** One 4.5 h session exists (mouse **A1**, `allego_1__uid0629-12-05-09`): clean EEG (RMS ~107 µV, 1/f delta PSD) but **EMG open (7 MΩ, implant fault)** → **not full 3-state scoreable** (no EMG = can't split REM vs quiet wake). Every mouse tested so far: ~1 clean EEG leg, the rest rail (open contacts).
- **The real limiter = per-animal electrode contact** (surgery + connector cleanliness), *and* — per the council — **endurance and crash-resilience over 72 h, which are completely untested.**
- **Hardware host risk:** mini-PC (Ultra 5 125H) hits **~90 °C on a 1-mouse recording**; 8-mouse × 72 h thermal survival is unproven (see the separate mini-PC-vs-desktop question).

## 2. Council verdict (2026-07-02)

Full method: 5 advisors + peer review. Highlights:

**Agreed (high confidence):**
1. **"Validated" is false.** Validation = clean EEG **and** EMG, simultaneously, on one properly-implanted mouse, sustained across a full sleep cycle. Has never happened.
2. **Bottleneck is surgery + endurance, not electronics.** Scripting/scaling does not move us toward scoreable data.
3. **A live code bug existed:** `xdat_io.py`'s `2mice32` map was labelled "validated 2026-07-01" when that day's verdict was the *opposite* (one mouse/headstage). Would silently mislabel animal channels. **FIXED — see §5.**
4. **AI ran ahead of evidence.** Real resolutions came from reading hardware docs / physical inspection, not AI hypotheses (which cost days: RHD2132, cold joints, wrong-mode-as-root-cause, near-RMA). **Rule going forward: human owns the physical/measurement call; AI proposes, evidence disposes.**
5. **72 h runs have zero crash resilience.** Allego forgets mode/rate/channel-select on restart; the session daemon watches Frigate/video but **not whether Allego is still writing**. No watchdog, no 3 am alert.

**Blind spots surfaced only in peer review:**
- **Slip-ring wear** = the silent 72 h killer. Hand-soldered custom ring rotates continuously under locomotion; nobody knows its rated rotation life or contact-resistance drift. Could read clean at t=0 and degrade to high-Z by t≈36 h → looks fine in the morning, unusable next day, no detection.
- **Animal triage / 3Rs.** Implanting new mice into an unvalidated pipeline wastes animals. Each existing implant should be scored against a minimum threshold *before* new surgery.
- **3 am operator recovery.** All diagnostic knowledge lives in a Claude session + an unsearchable vault. Who recovers a dropped headstage mid-night, with what printed card? What does recovery mean for a half-written xdat set with **no checksum**?
- **Hardware-vs-software bipolar** unresolved: RHD2216 has hardware differential inputs; scripts also do `n0 − n1` in software. Needs explicit reconciliation (is the software step re-referencing, redundant, or correct?). The one clean result doesn't prove it.
- **MEMORY.md truncated** (33 KB > 24 KB limit) → the corrections/retractions at the top may not load into the next session's context → next session could inherit the *old wrong* model. **Trim it.**

**Recommendation:** Stop treating this as "rig done → scale to 8." **Freeze scaling, commercialization, and C3442/8-mouse work until the minimum-viable bar is met:** one fully-instrumented mouse producing a scoreable **72 h 2-state (EEG + EMG)** trace.

## 3. What to do next (in order)

**Before any new surgery:**
1. **Endurance + thermal + Allego-survival test in ONE run.** Wire up 2 headstages / 64 ch (or resistor phantoms if no animals ready), record continuously (aim 24 h+, min 4 h). Log `sensors` temp every 60 s **and** track contact / slip-ring stability over time. This single test answers: (a) does the mini-PC survive multi-headstage thermally, (b) does contact/slip-ring hold over hours, (c) does Allego stay alive unattended. Fail here = learn it with wires, not with implanted animals + a burned 72 h experiment. *(This is the ONE thing to do first.)*
2. **Written, printed pre-closure surgery checklist** (tape to OR bench): DMM continuity every electrode pin before closing; EMG tips stripped + confirmed in muscle belly + anchored; dedicated animal-ground dura/bone pin DMM-beeped to bus; GUI impedance sweep (Allego paused) before leaving OR.
3. **Animal triage:** score each already-implanted mouse against §4 criteria; only implant new animals into a pipeline that has produced ≥1 passing trace.

**Engineering hardening (parallel, not blocking surgery):**
4. **Allego watchdog + alert:** detect if Allego stops writing (file size not growing / process gone) and push to the existing MQTT→Slack bridge. Reuse the `recording_watchdog` pattern.
5. **Put the analysis scripts under git.** They live in the vault (NAS-backed nightly) but are **not version-controlled** — that's why the `2mice32` flip-flop went uncaught. Git = the next one is catchable.
6. **Reconcile hardware-vs-software bipolar** — write down explicitly what `n0 − n1` does given RHD2216's differential front-end; confirm the EDF derivations are correct, not double-referenced.
7. **Trim MEMORY.md under 24 KB** so corrections load reliably.
8. **Laminated Allego startup card** (mode `XDAQ_ONE_REC` → 1000 S/s → reselect channels → STREAM not Record) + a 3 am recovery card.

## 4. Validation criteria — what "done" means (fill in exact numbers)

A recording counts as validated only if, on a **single fully-instrumented mouse**:
- **EEG:** RMS in the tens-to-low-hundreds µV; PSD shows 1/f falloff, delta-dominant with theta/delta cycling (sleep/wake structure); 60 Hz clean after notch.
- **EMG:** real muscle signal with **atonia during REM** (the discriminator); RMS above noise floor, not railed, not open (impedance in the good window, ≈0.1–1 MΩ; ≫5 MΩ = open).
- **Stability:** signal holds across a **full sleep cycle** and ideally the target **72 h**, with contact/impedance drift within tolerance (define threshold).
- **Handoff:** XDAT → EDF+ imports into the IIIS scorer AND is actually scored into 3 states (not just "opens").
- **% railed samples** below a set ceiling per channel.

## 5. Code fix applied this session (log)

`02-procedures/eeg-data-analysis/scripts/xdat_io.py`:
- Renamed the retracted map key `2mice32` → **`DEPRECATED_2mice32_shared_ground`** in both `CHANNEL_MAPS` and `BIPOLAR_DERIVATIONS`.
- Removed the false "validated 2026-07-01: impedance sweep good" comment; replaced with a note explaining the retraction (shared single ground for two animals is not electrically independent; correct topology = one mouse per headstage, use `single_mouse`).
- Updated the usage/help strings in `eeg_pipeline.py`, `xdat_to_edf.py`, `xdat_to_csv.py`, `qc_report.py` to drop `2mice32` and note the deprecation.
- Effect: all scripts default to `single_mouse`; passing `--config 2mice32` now **fails loudly (KeyError)** instead of silently mislabeling animal channels. Import verified: `CHANNEL_MAPS` keys = `['single_mouse', 'DEPRECATED_2mice32_shared_ground']`.

## Related
- [[2026-07-01]] — closure day (bottom-socket root cause, one-mouse-per-headstage verdict, dual-headstage 64 ch)
- [[2026-06-28-eeg-recording-troubleshooting-report]] — narrative report (status now superseded by §1 here)
- [[grounding-reference-noise-concepts]], [[signal-mapping-guide]], [[intan-headstage-troubleshooting]]
- [[2026-05-01-llm-council-review]] — prior council format


---

## UPDATE 2026-07-03 — "the one thing to do first" is DONE ✅

The endurance + thermal + Allego-survival test (§3.1 / "one thing to do first") **ran overnight and PASSED**. See [[2026-07-03]]. Results:
- **Thermal: PASS** — 14.23 h of 2 headstages + 4 cameras peaked **82 °C** (never 90), avg 65 °C. Mini-PC thermally adequate at this scale; the 90 °C scare was transient/GUI. Council mini-PC-vs-desktop concern answered for 2-mouse+4-cam scale.
- **Allego endurance: PASS** — 14 h unattended, stream continuous, Port A 64 ch stable, **zero dropped samples**, watchdog clean (triples the prior 4.5 h record).
- **Data integrity: PASS** — `data.xdat` byte-exact, contiguous timestamps; M1_EEG_F held clean ~110 µV for 14 h.
- **Video: PASS** — 4 cams, 5121 segments each, continuous.
- **C3442 dual-headstage-per-port VALIDATED** → 8-mice path confirmed with owned headstages.

Still open from this checkpoint: clean **bipolar EEG pair + working EMG** (electrode/surgical), and the crash-resilience gap is now partially covered (temp logger + Allego watchdog exist in `~/stress_test_2026-07-02/`, reusable). Daemon rough edges (JSON collision, partial long-export, log rotation) are **deferred** — daemon is being replaced by hardware sync; auto video start/stop disabled 2026-07-03 (`sessions.auto_start=false`).
