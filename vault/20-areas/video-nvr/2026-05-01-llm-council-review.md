---
tags: [decision, council, audit, review, weak-spots, roadmap]
date: 2026-05-01
created: 2026-05-01
type: architectural-review
status: closed (Stage 1 + 2 shipped; Stage 3 deferred — see status appendix)
sourced-from: 04-journal/2026-05/2026-05-01.md
---

# LLM Council Review of NeuroSurveillance — 2026-05-01

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A structured peer review of the NeuroSurveillance system by 5 LLM advisors (Contrarian, First Principles, Expansionist, Outsider, Executor), each then peer-reviewed by 5 independent reviewers, with a chairman synthesis. The goal was to surface weak spots, blind spots, and the right order of work — *excluding* the EEG/video TTL-pulse upgrade, which was already designed.
>
> **Why it exists.** Anchors the stabilization sprint plan ([[2026-05-stabilization-sprint-week-1-plan]]). When someone asks "why are we doing X in this order?", the answer is here. Also the bus-factor artifact: a future operator can read this once and understand the system's threat model.
>
> **How to read this page.** [[#TL;DR — Council Verdict]] is the short version. [[#Chairman Synthesis — Verbatim]] is the actionable summary. [[#The Staged Plan (executable, with filline citations)|Staged plan]] is the to-do list (largely done — see [[#Status appendix — what shipped]]). The advisor responses and peer reviews are kept verbatim for provenance.

> [!quote] Paper-ready
> "On 2026-05-01 the NeuroSurveillance system was reviewed by a structured LLM council of 5 advisors and 5 peer reviewers (Klumpp-style adversarial-review methodology). The review produced a 3-stage stabilization plan prioritizing data chain-of-custody (append-only session WAL + nightly reconciler) over feature expansion and over the planned TTL-pulse synchronization upgrade."

> [!history] Historical note (extracted 2026-05-28)
> This content originally lived in `04-journal/2026-05/2026-05-01.md` as a daily entry. It was extracted on 2026-05-28 to its own decision doc so the council output stops being entangled with the daily-log timeline; the original daily entry is now a thin stub pointing here.

---

## Focus

LLM Council review of NeuroSurveillance system. Goal: identify weak spots and improvements (codebase, efficiency, structure, anything else) **excluding** the EEG/video sync mechanism — TTL-pulse upgrade (XDAQ DAQ_ON → Pi GPIO 17 input; Pi GPIO 27 → XDAQ DIN 03 output, 50 µs frame markers in EEG stream) is already designed and queued for deployment.

This entry captures the **full** council process (5 advisors, 5 peer reviews, chairman synthesis) plus the executable staged plan it implies. Work it little by little — the order in [[#The Staged Plan]] is intentional.

## TL;DR — Council Verdict

- **Strongest advisor (5/5 peer reviewers): the Contrarian.** The JSON sidecar is the system's most dangerous single point. No fsync, no atomic rename, no append-only log. Manual sessions persist *only at stop*. Daemon crash mid-recording → MP4 chunks orphaned, unattributable. Apr 8 stuck export = data integrity bug masquerading as a reliability bug (Frigate evicts cache in ~24h).
- **Biggest blind spot (4/5): the Expansionist.** Detection / DeepLabCut / JOSS-paper packaging on top of an unverified provenance chain compounds uncertainty. Right vision, wrong moment.
- **Council's emergent insight (4/5 reviewers, independently): the TTL upgrade itself is the largest unaddressed risk on the roadmap.** No parallel-run, no pulse-count reconciliation, no rollback criterion, no `sync_method` session field. Trading known 1 s jitter for unknown, undetectable misalignment.
- **Second emergent insight:** human bus factor is 1. No off-machine code backup; no "if Andrea is unreachable" runbook.

## The One Thing To Do First

```bash
sudo apt-mark hold docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

5 minutes. Prevents recurrence of the [[2026-04-01|Apr 1 unintended-recording incident]] — documented, never actually fixed. `unattended-upgrades` blacklist is insufficient (aptdaemon bypasses it).

---

## Method

Three Explore agents surveyed in parallel:
1. Backend code quality (`neurosurveillance/backend/`) — architecture, race conditions, error handling, testing, sync mechanism, storage management.
2. Frontend + infrastructure (`neurosurveillance/frontend/`, `config/config.yaml`, deploy artifacts) — components, polling strategy, settings persistence, Frigate/go2rtc/Pi configs, deployment.
3. Vault survey (`Monitoring_project_obsidian_vault/`) — design intent, decisions, known issues, current sync mechanism, planned TTL upgrade docs.

Council convened: Contrarian, First Principles, Expansionist, Outsider, Executor — all dispatched in parallel. Their responses anonymized as A–E and sent to 5 independent peer reviewers (also in parallel). Chairman synthesized everything.

## Pre-Council Findings (evidence base)

### Backend — concrete weak spots

- **Race condition.** `frigate_controller.py:170` mutates `_last_known_state` from MQTT background thread *without* a lock. Only `_expected_states` is locked.
- **Dead code.** `daemon.py:565-566` — duplicate `storage_monitor.stop()` call.
- **No reconnect backoff.** `radiens_poller.py:63-84` — Radiens reconnect retries every 1 s if server is down; no backoff, will hammer.
- **Export timeout has no retry.** `daemon.py:378-382` — 5-min timeout marks session "failed: export timed out", no retry mechanism. The [[2026-04-08|Apr 8 incident]] needed manual recovery.
- **Manual sessions persisted only at stop.** Crash mid-manual-recording → metadata gone, MP4 chunks unlabeled on disk.
- **Active sessions in-memory only.** Daemon crash mid-export → `export_status="pending"` orphan forever.
- **`sudo` in `_move_export_file`** without password caching — single password prompt blocks the export thread.
- **Zero test coverage.** No `tests/`, no `pytest.ini`, no mocks.
- **Type hints ≈ 41%** of functions.
- **Logical duplication** between `session_manager.py` and `manual_session_manager.py` (export-status update, history load).
- **`storage_monitor.py` recovered from `.pyc`** after the [[2026-04-29|Apr 29 Syncthing wipe]] — pycdc artifacts noted in file header.

### Frontend — concrete weak spots

- **Three independent polling hooks** (`useStatusPoll` 1.5 s, `useHealthPoll` 5 s, `useStoragePoll` 10 s) — no coalescing, no backoff on error, sustained 3–4 HTTP/s.
- **Silent failures.** `ChamberSilo` receives `error` prop but never displays it. `useHealthPoll`/`useStoragePoll` set error state, no UI for it.
- **Settings split.** `SettingsModal.tsx` writes only to `localStorage` (`useSettings.ts:40-42`) — cameras, recording types, lab members, Frigate URL never reach `config.yaml`. Two researchers on two laptops have different settings with no merge.
- **Tauri configured but unused.** No native APIs invoked, no Rust backend code. Web app in a webview wrapper.
- **Storage badge JSX duplicated** at `App.tsx:116-137` AND `:144-168`.
- **Prop drilling** moderate (App → ChamberSilo → SessionSetup), 7 props deep.

### Infrastructure / deployment — concrete weak spots

- **Mosquitto runs `allow_anonymous true`** on the LAN. Any host can publish `frigate/+/recordings/set`.
- **Docker NOT pinned with `apt-mark hold`** — only `unattended-upgrades` blacklist (proven insufficient, [[2026-04-01|Apr 1]]).
- **Frigate `record.enabled: true` is fragile** — depends on Frigate not auto-upgrading.
- **Single NVR is SPOF.** Frigate + Mosquitto + daemon all on one ASUS NUC. NVR down = no recording, no exports, no API.
- **No automated backup.** NAS sync stubbed (`enabled: false`); MP4s + sidecars + Frigate sqlite all on one NVMe.
- **No off-machine git remote.** [[2026-04-29|Apr 29]] backend wipe was rebuilt from `.pyc` decompile + transcripts. Could have been a `git clone`.
- **Vault gaps.** No emergency failover runbook, no storage troubleshooting guide, no "first 10 minutes" checklist for a new researcher.

---

## The Council — Verbatim Advisor Responses

### The Contrarian

The single most dangerous thing in this system is the **JSON sidecar**.

Everything you call "scientific integrity" rests on a file written by a Python process holding a dict in memory, flushed at session boundaries, on a daemon with zero tests, that just got resurrected from `.pyc` decompilation. You think your sync problem ends when the TTL pulse lands. It doesn't. The TTL gives you sample-accurate alignment *if and only if* the metadata recording that alignment survives. Right now it doesn't, and nobody has noticed because the failures are silent.

Concrete blind spot: **you have no ground-truth audit trail.** When a session ends, the only record that the recording happened, what chamber, what mouse, what timestamps, lives in one JSON file written by one writer with no atomic rename, no fsync, no checksum, no append-only log, no database. Manual sessions are persisted *only at stop* — daemon crash mid-recording and the metadata is gone, but the MP4 chunks Frigate wrote are still on disk, unlabeled. Six months from now, when Andrea is reviewing a cohort, he will find orphan video he cannot attribute to any animal. He will not know it's wrong. He will publish it.

The Apr 8 stuck export marked "failed" with no retry is not a reliability issue — it is **a data integrity issue masquerading as a reliability issue**. The video exists in Frigate's recordings cache for ~24h, then gets evicted. The session JSON says failed. The actual footage is silently deleted by Frigate's own retention. You lost the data and your logs say "we tried."

The team's blind spot: you are treating this like a *web app with monitoring* (Netdata, Uptime Kuma, Slack alerts) when it is actually **a scientific instrument with no chain of custody.** Netdata tells you CPU is fine. It does not tell you that chamber 3's recording for mouse #47 from 02:14 to 06:33 doesn't exist on disk anymore.

Three things, in order: (1) Write every session state transition to an append-only SQLite WAL *before* acting. (2) Add a nightly reconciler that diffs Frigate recordings against session JSONs and screams about orphans. (3) Fix Mosquitto anonymous auth today — a lab visitor's laptop can stop your recording.

The TTL pulse fixes alignment. It does not fix the fact that you cannot prove, today, what you recorded yesterday.

### The First Principles Thinker

The TTL pulse is the experiment. Everything else is plumbing around it.

Once GPIO 27 marks every frame into the EEG stream at 50 μs, the *aligned dataset* is: an EEG file with an embedded frame-index channel, plus N video files whose frames map to that channel. That's it. That's the scientific artifact. A grad student in 2029 reanalyzing this data needs (a) the EEG, (b) the video, (c) a function `frame_n → EEG_sample_n`. Nothing else in the current architecture is load-bearing for science.

Now look at what's been built around that core:

**Frigate is the wrong abstraction.** Frigate is an NVR — its mental model is "continuously surveil a property, detect events, alert humans." You've disabled detection, disabled the web UI workflow, disabled alerts. You're using it as `ffmpeg + a circular buffer + an HTTP export endpoint`, wrapped in a 200 MB Docker container with an MQTT bus you only use to toggle a boolean. The ±2s export buffer exists *only* because Frigate-the-NVR records continuously and you have to carve clips out. Once TTL fires the GPIO, you don't need a circular buffer at all — you start `ffmpeg` on the rising edge, stop on the falling edge. No clipping, no MQTT, no export race condition (which already bit you Mar 6).

**The daemon shouldn't exist as a Flask service.** It exists because Frigate exists and needs orchestration. Strip Frigate out, and the "daemon" collapses to: a GPIO ISR on each Pi that spawns `ffmpeg -i <camera> -c copy session_<id>_cam_<n>.mp4`, plus a tiny coordinator that writes the JSON sidecar. ~300 lines, not 3000. The MQTT broker, the HTTP export client, `frigate_controller.py`, `manual_session_manager.py`, the export wait logic — all gone.

**Tauri is theater.** You wrote a desktop wrapper that invokes zero native APIs to display a status page for one researcher who is sitting at the NVR. A bookmark to `http://localhost:8585` does the same thing. The settings/localStorage/config.yaml split is a symptom: there's no actual desktop app, so there's no actual settings store.

**Reframe:** the question isn't "how do I improve this Frigate+daemon+Tauri stack." It's "after TTL, do I need any of these three?" Recording becomes `ffmpeg-on-GPIO-edge` on the Pi itself. The NVR becomes a file server. The frontend becomes a status page. The vault — the 93 notes — is the most valuable artifact you have, and it's the only piece that survives this question intact.

Build the instrument, not the surveillance system.

### The Expansionist

**What Andrea is sitting on, and doesn't see yet:**

The dataset is the asset. Not the daemon, not the vault, not the Tauri app — the *frame-aligned mouse-behavior + EEG corpus* that starts accumulating the moment the TTL pulse lands. Four chambers, 24/7, multi-month cohorts, 50 μs alignment. That is a **pretrained-model-grade dataset** in a field where labeled sleep behavior data is famously scarce. Klumpp 2025 was a methods paper. Andrea is positioned to publish the methods paper *and* the dataset paper *and* the model paper. He's thinking like a lab building a tool. He should be thinking like a platform releasing a benchmark.

**Turn on Frigate's detection. Today.** The Coral/iGPU is sitting idle. Even without retraining, generic detection gives you mouse bounding boxes at 15 fps for free — which, fused with EEG state, becomes automatic sleep-stage-vs-locomotion labeling. Six months from now that's a DeepLabCut/SLEAP pipeline running on the same NVR, producing pose timeseries that are *already EEG-aligned*. Behavioral phenotyping as a side effect of recording. No one else's NVR does this.

**The platform play.** "Frigate-for-neuroscience" is a real category that doesn't exist. The 3000-line daemon, the vault, the hardware sync design, the storage manager — package it as `neurosurveillance` on GitHub with a methods paper and you own the niche. Every behavioral neuroscience lab running RPi cameras is currently writing this badly in bash. A JOSS or eLife Tools & Resources paper writes itself. The 93-note vault *is* the supplement.

**The Tauri layer is wildly underused.** Right now it's a thin wrapper over a web UI. It could be the offline analysis client — native EEG plotting next to video scrubbing, frame-accurate annotation export, behavior labeling that pushes back to the dataset. That's the difference between "lab tool" and "instrument other labs install."

**Multi-user/multi-chamber isn't future work, it's distribution strategy.** The moment a second lab adopts this, the roster, per-chamber metadata, and session lifecycle stop being overengineering and start being the moat.

Andrea undervalues that he's two small decisions away from being the maintainer of a standard, not the user of a script.

### The Outsider

Walking in cold, the thing that hits me hardest is the **scale-to-complexity mismatch**. One researcher. Four cameras. And there's a Tauri desktop app, a Python daemon with a REST API, an MQTT broker, a containerized NVR, two SBC streaming bridges, a monitoring stack with Slack alerts, and a 93-note documentation vault. That's enterprise-shaped infrastructure for a setup that could plausibly run on one machine with a cron job and a shared folder. I'm not saying it should — but no one in your docs seems to have written down *why* it shouldn't. The justification for each layer is missing, and a future grad student inheriting this will assume every piece is load-bearing when some of it might be vestigial.

**Terminology is heavily insider-coded.** "Session daemon," "chamber silo," "R_ON/R_OFF," "EEG reserve," "go2rtc bitrate sync" — none of these mean anything without the lab context. The frontend component is called `ChamberSilo`. Is a silo a UI pattern or a physical thing? The README (if there is one — I don't see one referenced) needs a glossary. A stranger opening `daemon.py` doesn't know that "session" means "one animal recording session," not "an HTTP session" or "a tmux session."

**The recovery story is the loudest smell.** A file-sync tool deleted the backend and it was rebuilt from `.pyc` decompilation and chat transcripts. That happened, was survived, and apparently nothing structural changed afterward. No `git push` to a remote? No off-machine clone? The fact that the Obsidian vault has 93 notes but the *code* wasn't safely versioned tells me documentation has been prioritized over the artifact being documented. That's inverted.

**`users = ["andrea"]`.** If there's one user, why is there a user list at all? Either delete the abstraction or admit it exists for a future that may never arrive. Speculative generality has a cost — every endpoint that takes a user ID is now a thing to maintain for a field that's always the same value.

**Other oddities:** the desktop app talks *only* to localhost — so it has to run on the NVR itself, which means the "desktop" is also the server. That deserves a sentence somewhere. And the Python service's config and the frontend's localStorage drifting apart isn't just a sync bug; it's a sign that nobody decided which one is the source of truth. Pick one. The other becomes a cache.

### The Executor

**Triage Plan**

The question isn't "what's wrong" — plenty is wrong. The question is "what gets fixed Monday before lunch."

---

**TIER 1 — DO MONDAY (under 2 hours total, blocks data loss)**

1. **`apt-mark hold docker-ce docker-ce-cli containerd.io docker-compose-plugin` — 5 minutes.** This is the Apr 1 incident. You documented it, you didn't fix it. One command. Stop reading and do it now.
2. **Delete the duplicate `storage_monitor.stop()` at `daemon.py:565-566` — 2 minutes.** Free fix.
3. **Stop Syncthing from touching the backend directory — 15 minutes.** Add the backend path to Syncthing's ignore patterns OR move backend out of the synced tree. Apr 29 happened. It will happen again. This is not a "review Syncthing strategy" task; it's an ignore-pattern edit.
4. **Pin Frigate image tag in `docker-compose.yml` — 10 minutes.** If not already done. Same class of failure as Docker auto-upgrade.
5. **Bind Mosquitto to 127.0.0.1 OR add a password — 20 minutes.** Pick the lazy one (localhost bind, since daemon is on the same NVR). One config line.

**TIER 1 buys you: no more silent recordings, no more wiped backends, no more LAN-exposed MQTT. ~50 minutes.**

---

**TIER 2 — FREE AFTERNOON (3–4 hours, biggest leverage left)**

6. **Persist active sessions to disk on every state change — 2 hours.** JSON file. Reload on startup. Kills the orphan-export class of bugs entirely. Don't engineer it; just `json.dump` after every mutation.
7. **Add the lock on `_last_known_state` in `frigate_controller.py:170` — 15 minutes.** `threading.Lock()`. Done.
8. **Exponential backoff on Radiens reconnect — 30 minutes.** Cap at 60 s. Trivial.
9. **Automated backup of `/opt/neurosurveillance/config.yaml` + Frigate config + vault — 1 hour.** systemd timer + rsync to a USB stick or second disk. Don't wait for the NAS. The NAS has been "stubbed" for months; it isn't coming.

---

**TIER 3 — SKIP ENTIRELY (for now)**

- **Tests for a 3000-line daemon.** No. You'd spend a week and your behavior would barely change. Skip.
- **Settings sync (localStorage ↔ config.yaml).** Annoying, not dangerous. You're the only user. Skip.
- **Splitting `daemon.py`.** Refactor theater. Skip.
- **Removing Tauri.** Cosmetic. Skip.
- **NVR redundancy / SPOF.** Buy a second NUC or stop worrying. There's no middle move.
- **Frontend JSX dedup.** Skip.

---

**Monday's first move:** the `apt-mark hold` command. Then Syncthing ignore. Everything else can wait one more day; those two cannot.

---

## The Council — Peer Reviews (Anonymized A–E)

Mapping (de-anonymized after review): A=Executor, B=Outsider, C=Contrarian, D=Expansionist, E=First Principles.

### Reviewer 1

**1. Strongest: C.** C is the only response that correctly identifies the threat model. Andrea's stake is *scientific integrity*, and C names the specific failure mode: orphan MP4s with no metadata, silent data loss masquerading as "failed export," publication of unattributed footage. The append-only SQLite WAL + nightly reconciler is concrete, cheap, and directly addresses the Apr 8 incident. A is operationally excellent but tactical; C is operationally excellent *and* strategic about what actually matters.

**2. Biggest blind spot: E.** E is writing a grant application, not answering the question. Andrea has zero tests, a backend resurrected from .pyc six weeks ago, and Mosquitto open on the LAN — telling him to enable detection, build a SLEAP pipeline, and package for JOSS is malpractice. E misses that the foundation is unstable; you don't pour a second story on a cracked slab. It also ignores the explicit "1 active researcher" constraint and treats distribution as if maintainer burden were free. The platform play might be right in 2027; recommending it now actively endangers the dataset E claims is the asset.

**3. What all five missed: the human single point of failure.** Andrea is the only researcher, the only operator, and the only one who knows how any of this works. If he gets hit by a bus — or just takes a sabbatical — the vault is unreadable to anyone who doesn't already know what a "chamber silo" is (B gestured at this but framed it as terminology, not continuity). No runbook for "the daemon is down at 3 AM and Andrea is unreachable." No second pair of eyes on data integrity. The bus factor is 1 across code, ops, and scientific interpretation simultaneously. That's a bigger SPOF than the NVR hardware.

### Reviewer 2

**1. Strongest: C.** C identifies the actual failure mode that threatens scientific integrity: the metadata layer is a single in-memory dict flushed at boundaries, with no audit trail and no reconciliation. The Apr 8 stuck export reframe — "data integrity masquerading as reliability" — is the sharpest observation in the council. The three concrete fixes (append-only SQLite WAL, nightly reconciler, Mosquitto) directly address Andrea's stated stake.

**2. Biggest blind spot: D.** D dismisses Frigate as "wrong abstraction" and proposes ripping it out for GPIO-triggered ffmpeg. This ignores that Frigate is already deployed, debugged, monitored, and producing data for an active experiment. "Strip Frigate, daemon collapses to 300 lines" is a rewrite proposal disguised as a simplification — exactly the move that breaks a working scientific instrument mid-study. D also ignores the existing 4-chamber multi-Pi distribution, manual session UI, and export pipeline that Andrea uses daily. Elegance on a whiteboard, catastrophe in production.

**3. What all five missed.** None addressed the **TTL upgrade migration risk itself**. The hardware pulse replaces 1 s polling — meaning Radiens R_ON/R_OFF logic, session_manager triggering, and the entire timing contract change. No advisor proposed: parallel-run old and new sync for N sessions, validate frame-to-EEG offset on known signals, or define the rollback criterion. Andrea is about to swap the synchronization primitive on a live experiment with zero tests and a daemon recently rebuilt from .pyc. That is the highest-leverage risk on the table, and the council walked past it.

### Reviewer 3

**1. Strongest: C.** C identifies the only failure mode that destroys scientific integrity silently: unattributable recordings. A's checklist is useful but treats symptoms; B's critique is sharp but observational; D's reframe is intellectually clean but speculative (rebuilding post-TTL is a quarter of work, not a Monday fix); E is a career pitch, not engineering. C names a specific corruption path (JSON write-without-fsync, manual sessions persisted only at stop, 24h Frigate eviction) and proposes the minimum mechanism — append-only SQLite WAL + nightly reconciler — that makes the system *provable*. For a sleep researcher, "I can prove what I recorded" beats every other improvement.

**2. Biggest blind spot: E.** E treats a single-researcher, zero-tests, JSON-sidecar, anonymous-MQTT system as a publishable platform. Before "JOSS paper" and "Frigate-for-neuroscience standard," the data has to be trustworthy and the code has to survive a Syncthing event. E skips the integrity layer entirely and proposes turning ON detection — adding ML-derived labels to a corpus whose recording attribution isn't even guaranteed. That's compounding uncertainty.

**3. What all five missed.** None addressed the **TTL transition itself as a risk window**. Switching sync mechanisms on a live 24/7 instrument means a period where old sessions (1 s polling) and new sessions (hardware pulse) coexist in the same dataset with different alignment guarantees. There's no mention of: a session-level field recording which sync method produced the data, a validation protocol that runs both in parallel before cutover, or how to handle the inevitable boundary recordings. C's reconciler is closest but operates on existence, not provenance. For scientific integrity, the cutover is more dangerous than any item on A's Monday list.

### Reviewer 4

**1. Strongest: Response C.** C identifies the only failure mode that destroys the work irretrievably: scientific provenance loss. A neuroscientist with zero tests, a `.pyc`-resurrected daemon, and unflushed JSON sidecars is one crash away from orphan MP4s that can't be attributed to mouse/chamber/timestamp — and won't notice for months. The append-only SQLite + nightly reconciler is the right primitive. C also correctly reframes Apr 8's "stuck export" as a chain-of-custody bug, not reliability theater. A is operationally tight but optimizes uptime; C protects the publication.

**2. Biggest blind spot: Response E.** E proposes a dataset/methods-paper empire while the foundation is a daemon that lost itself to Syncthing three weeks ago and has no tests. Turning on detection, DeepLabCut, multi-user distribution, and JOSS packaging on top of an unverified provenance chain compounds risk — every downstream label inherits whatever metadata corruption C describes. E also ignores the constraint of one researcher's time. It's the "rewrite in Rust" of scientific software: aspirational, expensive, premature.

**3. What all five missed:** None addressed the **TTL pulse itself as a new failure surface**. GPIO ISRs miss edges under load, Pi clocks drift, and a dropped or duplicated pulse silently desynchronizes EEG↔video with no detector. The system needs a pulse-counter reconciliation (EEG channel pulse count vs. video-side pulse count per session, logged and alarmed) before TTL goes live — otherwise the "hardware sync upgrade" trades a known 1 s jitter for an unknown, undetectable misalignment. D came closest by treating TTL as primary but assumed the edge is reliable. For sleep staging, a missed pulse at hour 4 of an 8-hour recording is a publication-ending error nobody would catch.

### Reviewer 5

**1. Strongest: C.** C is the only response that correctly identifies what's actually at stake. Andrea said "scientific integrity" — C is the only one that takes that seriously at the data layer. The JSON-sidecar-with-no-fsync-no-atomic-rename observation is concrete, code-level, and catastrophic: it's the bug that causes a retraction, not an inconvenience. The Apr 8 stuck export reframe ("integrity issue masquerading as reliability, Frigate evicts in 24h") is the sharpest single sentence in the council. A is operationally tighter but solves Monday; C solves the paper.

**2. Biggest blind spot: E.** E pivots to a dataset/career strategy without engaging the question asked. Worse, "turn Frigate detection ON today" ignores that detection was deliberately disabled (Apr 1 unintended-recording incident shows this system is fragile to Frigate config changes), and assumes a single researcher with no tests and a recent data-loss event should add an ML pipeline. E is missing the risk axis entirely — it's upside-only reasoning applied to a system that just lost its backend to Syncthing.

**3. What all five missed:** **The TTL upgrade itself is unvalidated and untested.** Every response either accepts the TTL upgrade as solved (A, B, C, E) or builds a new architecture around it (D). Nobody asked: what's the rollback plan if TTL hardware fails mid-cohort? Is there a parallel-run period where 1 s polling and TTL both record so drift can be measured? With zero tests and a recent rebuild-from-pyc event, swapping the sync mechanism on a live 24/7 experiment is the highest-risk change on the roadmap — and the council treated it as a given. That's the real Monday question.

---

## Chairman Synthesis — Verbatim

### Where the Council Agrees

Four of five advisors converge on a single thesis: **the foundation is unstable, and the most dangerous failures are silent ones**. The Contrarian, Outsider, Executor, and (implicitly) First Principles all point at the same wound — the system can lose or mis-attribute data without anyone noticing. The Apr 8 stuck export, the Apr 29 Syncthing wipe, the Apr 1 docker auto-upgrade, and the JSON-sidecar-as-source-of-truth all rhyme: state lives in fragile places, and the alarms watch CPU instead of provenance.

All five also agree, explicitly or implicitly, that **scope has outrun the operator**. One researcher, four cameras, but a Tauri app, MQTT broker, REST API, container orchestration, two SBCs, Slack-routed monitoring, and a 93-note vault. The Outsider names it directly; the Executor's "TIER 3 — SKIP" list is the same observation in operational form; First Principles pushes it furthest.

Peer reviewers were unusually unanimous: **5/5 named the Contrarian strongest, 4/5 named the Expansionist the biggest blind spot**. That is as close to consensus as a council gets.

### Where the Council Clashes

The genuine disagreement is about direction of travel.

**(a) Consolidate around chain of custody (Contrarian + Executor).** Patch the holes, persist session state on every transition, run a nightly reconciler against Frigate's recordings, fix Mosquitto, pin Docker. This is the conservative read: the system mostly works, but cannot today *prove* what it recorded. Make it provable, then stop.

**(b) Simplify post-TTL by removing Frigate (First Principles).** Once GPIO marks frames into EEG, the circular buffer and MQTT toggle become vestigial. A 300-line GPIO-triggered ffmpeg coordinator replaces the daemon. Elegant on a whiteboard — but Reviewers 2 and 5 flag it as catastrophic in production: ripping out a working instrument mid-study, with zero tests, after a `.pyc` rebuild, is the wrong move at the wrong time. The argument is correct in principle and dangerous in timing.

**(c) Expand into a publishable platform (Expansionist).** Turn on detection, add DeepLabCut, package as `neurosurveillance`, write the methods + dataset paper. Reviewers were near-unanimous (4/5) that this is upside-only reasoning on a cracked foundation. Turning detection ON specifically echoes the Apr 1 incident pattern — adding behavior to a system that just demonstrated it can change behavior unintentionally.

Reasonable advisors disagree because they're optimizing different objectives: Contrarian optimizes for *not retracting a paper*, First Principles for *system clarity*, Expansionist for *career trajectory*. Given the stakes (data Andrea cannot recover) and the constraint (Andrea is not a SWE), the integrity objective dominates.

### Blind Spots the Council Caught

The biggest emergent insight came from peer review, not from any single advisor: **4 of 5 reviewers independently flagged that the TTL upgrade itself is the largest unaddressed risk on the roadmap, and the council treated it as a given.** Specifically:

- **No parallel-run protocol** — old polling and new pulse sessions will coexist with different alignment guarantees, and no session-level field records which method produced the data (Reviewers 2, 3, 4).
- **No pulse-count reconciliation** — Reviewer 5's point is the sharpest: GPIO ISRs miss edges under load, Pi clocks drift, and a dropped pulse at hour 4 of an 8-hour recording is publication-ending and *undetectable* without an EEG-side vs video-side pulse-count audit per session, logged and alarmed.
- **No rollback criterion** — what failure rate during validation triggers reverting to 1 s polling? Nobody decided.

Trading known 1 s jitter for unknown, undetectable misalignment is a worse bargain than the upgrade narrative suggests. This must be solved *before* TTL goes live.

The second emergent insight is **Reviewer 1's bus-factor point**: Andrea is sole researcher, sole operator, sole interpreter, sole maintainer. No advisor addressed this. The vault helps but isn't a substitute for a second human. At minimum: a remote git push, an off-machine config backup, and a one-page "if Andrea is hit by a bus" runbook.

### The Recommendation

Stop expanding. Stabilize, instrument the foundation, then validate the TTL transition before cutover. Concretely, in this order:

1. **Monday morning, 50 minutes (Executor Tier 1).** `apt-mark hold` the Docker packages, delete the duplicate `storage_monitor.stop()`, exclude the backend from Syncthing, pin the Frigate image tag, and either bind Mosquitto to 127.0.0.1 or set a password. This blocks roughly 80% of known data-loss vectors for under an hour of work.

2. **One free afternoon (Contrarian + Executor Tier 2).** Persist session state to an append-only SQLite store on every transition — not just at stop. Add a nightly reconciler that diffs Frigate recordings against session records and alerts on orphans. Add the lock at `frigate_controller.py:170`, exponential backoff on Radiens reconnect, and a USB-targeted backup of `config.yaml`, Frigate config, and the vault. Push the repo to a remote — the `.pyc` rebuild must never happen twice.

3. **Before TTL cutover (council emergent insight).** Build pulse-count reconciliation: log EEG-side pulse count and video-side pulse count per session, alarm on mismatch. Run polling and TTL in parallel for at least one full cohort. Record the sync method as a session-level field. Define a numeric rollback criterion in advance.

**Explicitly defer:** the Expansionist platform play (detection, DeepLabCut, JOSS paper) until items 1–3 are done — adding ML labels on top of unproven attribution compounds uncertainty. **Explicitly defer:** First Principles' Frigate removal — correct long-term, wrong during an active study with no tests. **Explicitly skip:** retrofitting tests onto the 3000-line daemon, the settings/localStorage sync, and NVR redundancy. None of these prevent a retraction.

### The One Thing to Do First

```
sudo apt-mark hold docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Five minutes. Prevents the exact incident already suffered on Apr 1. Documented, never fixed. Do it before reading the rest of this verdict a second time.

---

## The Staged Plan

The plan below is the original spec the council produced; sub-headings show the original file:line citations. The detailed sprint execution + status tracking now lives in [[2026-05-stabilization-sprint-week-1-plan]].

Order matters — earlier stages buy stability that later stages depend on. This section is the original spec for provenance.

### Stage 1 — Monday morning (≈50 minutes, blocks ~80% of known data-loss vectors)

- **Pin Docker packages** (5 min) — `sudo apt-mark hold docker-ce docker-ce-cli containerd.io docker-compose-plugin`. Prevents recurrence of [[2026-04-01|Apr 1]]. `unattended-upgrades` blacklist is insufficient.
- **Stop Syncthing from touching the backend** (15 min) — remove `neurosurveillance/backend/` from the synced folder set; do NOT rely on `.stignore` alone.
- **Pin Frigate image tag** (10 min) — replace any `:latest` / floating tag with `:0.16.1` in `/srv/frigate/docker-compose.yml`.
- **Lock down Mosquitto** (20 min) — bind `listener 1883 127.0.0.1` OR add a password.
- **Delete duplicate dead code** (2 min) — `daemon.py:565-566` duplicate `storage_monitor.stop()`.
- **Push the repo to a remote** (5 min) — GitHub private. The `.pyc` rebuild must never happen twice.

### Stage 2 — One free afternoon (~3–4 h, the chain-of-custody fix)

- **Append-only session journal** (~2 h) — SQLite WAL; every state transition written before the side effect.
- **Nightly reconciler** (~1 h) — diffs Frigate recordings against the journal; Slack on orphans.
- **Local concurrency fixes** (~45 min) — `threading.Lock()` on `_last_known_state`; exponential backoff on Radiens; persist export status to journal.
- **USB backup** (~1 h) — systemd timer + rsync of config + Frigate config + vault + journal.

### Stage 3 — Before TTL cutover (council's emergent insight)

- **Pulse-count reconciliation** — Pi-side outgoing edges + Radiens-side incoming pulses per session; mismatch → Slack + journal `sync_integrity: failed`.
- **Parallel-run protocol** — ≥1 cohort with both 1 s polling and GPIO pulse; per-session `sync_method` field (`software_poll | hardware_pulse | both`).
- **Numeric rollback criterion** — defined in advance (e.g., "if pulse-count mismatch occurs in >1% of sessions during validation, revert to polling primary").
- **One-page bus-factor runbook** (~30 min) — "If Andrea is unreachable: how to start/stop a session, where the data lives, how to restart the daemon, how to read a journal entry." Lives in `02-procedures/`.

### Explicit non-goals

- ❌ Retrofitting unit tests onto the 3000-line daemon — refactor theater for a solo researcher.
- ❌ Settings sync between localStorage and `config.yaml` — annoying, not dangerous; one user.
- ❌ Splitting `daemon.py` or removing Tauri — cosmetic.
- ❌ Building a second NVR for redundancy — no middle move; either buy a second NUC or accept the SPOF.
- ❌ Turning on Frigate object detection / DeepLabCut / JOSS paper packaging until Stages 1–3 are complete. Right vision, wrong moment.
- ❌ Removing Frigate post-TTL (First Principles' suggestion) — correct in principle, catastrophic mid-study with zero tests.

---

## Status appendix — what shipped

Live status is maintained in [[2026-05-stabilization-sprint-week-1-plan#Status snapshot]]. Summary as of 2026-05-28:

| Stage | Council intent | Status |
|---|---|---|
| Stage 1 | Stop-the-bleeding (Docker pin, Syncthing isolation, Frigate pin, Mosquitto lockdown, dead-code, off-machine git) | ✅ Done (1.2 Syncthing `*.py` exclude still 🟡 — `__pycache__`/`*.pyc`/`venv` excluded but `*.py` still synced) |
| Stage 2 | Chain-of-custody (append-only WAL + nightly reconciler + concurrency + off-machine backup) | ✅ Done — WAL shipped 2026-05-23; reconciler 2026-05-24; reconciler→Slack enabled 2026-05-28; NAS backup over Tailscale superseded the USB-stick plan, deployed 2026-05-26 |
| Stage 3 | Pre-TTL (pulse-count reconciliation, parallel-run, rollback criterion, bus-factor runbook) | ❌ Open — 3.1/3.2/3.3 hardware-gated on KC Kong (Kontex) reply re: fan-out + grounding + Ubuntu 24.04 Core2 drivers; 3.4 bus-factor runbook is doable now (no hardware dependency) |
| Non-goals | Tests, settings sync, daemon split, Tauri, 2nd NVR, detection/JOSS, Frigate removal | 🚫 Intentionally not done |

---

## References

- Plan file (mirror of this analysis, machine-readable): `~/.claude/plans/read-the-vault-and-optimized-hopcroft.md`
- [[2026-04-01]] — Frigate auto-upgrade, unintended recording (root cause for Stage-1 item 1).
- [[2026-04-08]] — Stuck Frigate export incident (root cause for Stage-2 reconciler).
- [[2026-04-29]] — Syncthing wipe + recovery (root cause for Stage-1 items 2 & 6).
- [[2026-04-30]] — Post-recovery verification.
- [[overview|Hardware sync overview]] — TTL pulse design (Stage 3 prerequisite).
- [[production-values]] — canonical IPs/ports/paths.
- [[2026-05-stabilization-sprint-week-1-plan]] — the executable sprint plan derived from this council.
