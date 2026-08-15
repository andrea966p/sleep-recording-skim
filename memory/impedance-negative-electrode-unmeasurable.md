---
name: impedance-negative-electrode-unmeasurable
description: "Open Ephys CANNOT measure the negative electrode of a bipolar pair either — XDAQ-OE plugin compiles setZcheckPolarity but never calls it (0 call sites, verified in the binary). Switching software buys nothing; DMM per pad is still the fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73d8f40f-8fe5-4e49-9c74-3b734c900c35
  modified: 2026-08-03T14:49:57.898Z
---

**Question asked 2026-08-03: "can we measure impedance per electrode, before the difference, with the Open Ephys GUI?" ANSWER: NO, not as shipped.**

Verified by inspecting the installed binary, not by reading docs: `~/.config/open-ephys/plugins-api10/XDAQ-OE.so` (XDAQ-OE v0.4.4, API10, working on this machine).

- `Rhd2000Registers::setZcheckPolarity(ZcheckPolarity)` **is compiled in** at `0x7a420`, but has **ZERO call sites**.
- Control: `setZcheckScale` = 3 call sites, `setZcheckChannel` = 1, `enableZcheck` = 1 — all called **out of line** from the impedance path. So the missing polarity call is real, not an inlining artefact. It is dead code carried along because `Rhd2000Registers.cpp` compiles whole.
- Confirmed by its own export `~/Downloads/OE imp with mouse split ground` (XML): exactly **one** `magnitude`/`phase` per amplifier, no polarity dimension. Same shape as Radiens.

⇒ **Allego and Open Ephys are equally blind to the negative electrode.** Software gap in BOTH, not a chip limit — the RHD2216 CAN test either pin and that register bit exists precisely for bipolar chips. **Do not propose switching acquisition software to solve this.**

**Fix hierarchy (cheapest first):**
1. ⭐ **DMM each C3410 pad vs the GND pad — free, today, sees both sides.** DC continuity, not 1 kHz impedance, so not comparable to a sweep, but it answers "is this electrode connected at all". Still the recommended next step.
2. **Patch the plugin** (open source): run the measurement pass twice, call `setZcheckPolarity(ZcheckNegativeInput)` before the second, emit a 2nd value per amp. Code is trivial; cost is owning an unofficial plugin on a live production rig across upgrades.
3. **Ask Kontex** — small, concrete, well-specified request against a plugin they maintain, open thread already exists. Cheapest *supported* fix.

Written up in vault `06-references/impedance-sweep-register.md` (last section, with the call-site table and a paper-ready sentence). See [[eeg-rig-current-state]], [[electrode-failure-literature]].
