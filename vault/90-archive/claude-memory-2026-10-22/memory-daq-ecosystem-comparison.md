---
name: daq-ecosystem-comparison
description: The 3-way DAQ comparison (XDAQ vs Open Ephys vs Intan) for 32 mice — REVISED 2026-07-28 to no-Allego / OE-GUI-everywhere / complete-rig BOM; commutators now dominate the budget
metadata:
  node_type: memory
  type: project
  originSessionId: d82d08e4-aa65-41f6-9c48-c49e1066f262
  modified: 2026-07-28T01:05:27.763Z
---

Vault `07-decisions/2026-07-24-daq-32-mouse-final-comparison.md` (VAULT-ONLY, Kontex quote confidentiality — never publish as Artifact). Supersedes 2-way 16-mouse `daq-ecosystem-comparison-xdaq-vs-openephys.md`.

**🔴 REVISED 2026-07-28 — Andrea reset 4 ground rules:** (1) **NO Allego license** — drive ALL three ecosystems with the **free Open Ephys GUI** (Kontex OFFICIALLY supports XDAQ Gen1+Gen2 under OE via Plugin Installer, kontex.io/software). (2) Price the **COMPLETE rig** (headstages, cables, commutators, adapters, PC, storage), not just the box. (3) PC-per-XDAQ question answered. (4) **Our code/daemon EXCLUDED from evaluation** — rig only, code can be rewritten.

**What moved:** XDAQ lost pipeline-reuse (its biggest edge, now worth $0) AND lost license (~$5-10k) + 2nd PC. OE lost "free software" edge (everyone free now). SyncLink/multi-box-sync stopped being a differentiator. **Surviving axes = per-animal ground isolation + complete-rig cost + adapter-chain depth.**

**🆕 PC question ANSWERED: ONE PC, not one-per-XDAQ.** Old "2 PCs" was an **Allego seat-license artifact**, not hardware. OE GUI runs multiple boards in one instance (one source node per board), verbatim OE devs: *"you can add two Rhythm nodes... each will use a different board"* (groups.google.com/g/open-ephys/c/Cz0YjSBm494). Caveats: board order arbitrary (USB descriptors) → **must verify node↔box mapping before every run or mouse IDs silently swap**; boards asynchronous → fix with shared TTL; **XDAQ = Thunderbolt 3** (60W) so 2× ONE+ needs 2 TB3 ports (Intan/OE = USB3, easier). ⏳ XDAQ OE-plugin multi-device support UNCONFIRMED. Bandwidth NOT a limit: 512ch×2B → 30.7MB/s @30kS/s (2.65TB/day), 1.0MB/s @1kS/s (88GB/day) → **storage, not bandwidth; sample rate = 30× budget swing**.

**🆕 Multi-box sync EQUALIZED (and better than we thought):** OE Record Node does **ONLINE** sync off a shared TTL line, recomputes relative sample rates **every 10s**, tolerance **<1 ms** (open-ephys.github.io/gui-docs/Tutorials/Data-Synchronization.html). Not homebrew. Same TTL fans out to DAQ boxes + Pi cameras (one pulse train serves both). **SyncLink now OPTIONAL**, dropped from BOM.

**🔴 COST OF DROPPING ALLEGO: per-mouse independent START/STOP is GONE.** radiens `start_recording(port=)` was the ONLY documented per-animal scheduling across all 3 ecosystems. Under OE GUI start/stop is **GLOBAL** (`PUT /api/status` RECORD; per-node endpoints are CONFIG only). Separate FILES still ✅ via Record Nodes. → **plan: record continuously at modest sample rate, slice offline per user.** OVERTURNS [[project_multiuser_recording_schedules]].

**🔴 NEW HEADLINE: commutators dominate the budget, and they're ecosystem-neutral.** 1/mouse × 32. OE torque-free SPI **OEPS-7761 €2,595 ea = €83,040** (more than ANY DAQ block!). Alternatives: Doric/AlphaOmega Intan-ready ⏳quote; **Open-MAC open-source motorized ~$300-600 ea ≈ $10-19k**; passive slip-ring + Intan **C3430** SPI breakout (Intan app-note; SPI is digital so commutator adds NO noise). **Swings total ~€70k — more than the ecosystem choice does.** ACTION: inventory what the current 8-mouse rig uses before any quote.

**Complete-rig totals (Scenario A, isolation):** blocks = DAQ (differs) + tether chain ~$50-55k (identical) + commutators €10-83k (identical) + infra ~$5-14k (identical). DAQ block: **XDAQ ~$60-74k EST** (ONE+ still unquoted) / **OE ~€27.2k** (board now €3,385, was €3,245; weak isolation) / **Intan $57,000 PUBLISHED**. Rig totals: XDAQ ~$127-226k, OE ~€94-186k, Intan ~$124-209k. **DAQ = only 25-45% of rig; the three are far closer than before.**

**🆕 READING CHANGED: Intan direct now looks STRONGEST** — isolation included free (ports isolated by design), **zero adapters** (XDAQ chain = HDMI→bridge→PortEXP→SAdpt→headstage, deepest = most failure points), fully published pricing, and no longer priciest once XDAQ's license+2nd-PC come off. XDAQ still credible (only PROVEN 72h byte-perfect on our bench) but **quote-gated + support-gated**. OE hardware = weakest fit (we're buying isolation; they don't sell it) though its GUI is now our front end everywhere.

**⏳ TOP OWED (2 could sink the XDAQ column):** (1) **Is Port Expander supported/isolating under the OE GUI plugin, not just Radiens?** (2) Does OE XDAQ plugin bind 2 XDAQ devices in one instance? (3) real ONE+ 32-mouse quote. (4) OE: are the 4 board ports galvanically isolated from each other? (5) **commutator inventory + quotes**. (6) **headstage count — old doc claimed "we own 32", almost certainly 8** (Core has 8-hs ceiling) → +24 × $820 ≈ $19,680. (7) sample-rate decision.

Still gated behind **surgical yield** ([[eeg-60hz-saga]]) — no box fixes an open frontal electrode. Council only after the gates. Related: [[acquisition-device-16-32-mice]], [[openephys-scale-up-option]].
