---
name: tether-soldered-duty-cycle-result
description: "2026-08-05 — soldered tether took B1's EEG duty cycle 45%->100% (p=0.0001); sweeps are now automated via gRPC; B1 was sacrificed after its skull electrode detached, so the slip-ring isolation is permanently lost"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c8ce7c5-ec36-4595-9a71-7100cbae80c1
  modified: 2026-08-06T07:59:46.391Z
---

🔴⭐⭐⭐ **ARM C RAN 2026-08-06 ON D2 AND WENT THE WRONG WAY. See §13 of the vault page.**
D2 → **long custom tether DIRECT to headstage, slip ring REMOVED** (port D, mouse-2 ⇒ `D/33`
EEG, `D/34` EMG). **D2 EMG 10/15 = 66.7% (pre-swap, 20 min before) → 0/41 = 0.0%, p = 8.4e-08**;
at 2 MΩ 15/15 → 25/41, p = 0.0025. EEG median 3.450 → **8.235**.
✅ **Drift excluded** (untouched B1 33.3%→34.1%; no-mouse cable 0%→4.9%).
✅ **Anaesthesia recovery excluded** — arm B drifted up across its block (rho +0.51); here D2
EMG is **FLAT, rho −0.00, p=0.99**, EEG slightly worse (rho +0.38). Stable new state.
⭐ **⇒ THE SLIP-RING HYPOTHESIS NOW HAS EVIDENCE AGAINST IT**: arm B (short soldered, WITH ring)
45→100%; arm C (long soldered, NO ring) 67→0%. Construction ~held constant. ⚠️ **Different
animals + different lengths ⇒ a LEAD, not a conclusion.**
❌ **Tether inspected same evening: NOT twisted.** So binding is not the explanation.
🔴⭐ **THE HARM FINDING IS PROVISIONAL — D2 RECOVERED ~40 min later.** A single sweep at ~17:30
gave **D2 EEG 0.396 and EMG 0.404**, i.e. **below EVERY one of the 41 arm C values** (block
minima 3.127 and 0.694). ⇒ **arm C may have captured ONE LONG OPEN STATE, not permanent harm.**
The flat rho −0.00 that excluded anaesthesia is **equally consistent with being stuck in one
state for 21 min**. **Do NOT report arm C harm as established.** The overnight recording settles
it — a usable fraction over 12+ h cannot be fooled by state sampling.
✅ **Twisting B1's slip ring by hand caused NO harm** — B1 EEG read **0.084 MΩ** during the
twist, its best value of the day (n=1).
⚠️ **Data hygiene: `armC-long-direct-noslipring/` holds THREE conditions** (pre-block single
sweep, the 40-sweep block, the twist sweep) ⇒ a folder glob scores **41 not 40**. Separate them
before any future analysis.
🛑 **Do NOT revert D2 under anaesthesia same-day.**

**The 2026-08-05 session.** Write-up: vault `05-experiments/active/2026-08-05-tether-comparison.md`.
Journal `04-journal/2026-08/2026-08-05.md`. Files `~/Downloads/impedance measurments/2026-08-05/`.

⭐⭐⭐ **THE RESULT.** B1, within-animal, 20 sweeps per arm, duty cycle = fraction below 2 MΩ:

| channel | arm A original heatshrink | arm B short **soldered + resin** | p |
| --- | --- | --- | --- |
| `B/1` EEG | 9/20 = **45%**, 5 flips, median 2.913, max 9.089 | **20/20 = 100%**, **0 flips**, median 0.903, **max 1.341** | **0.0001** |
| `B/2` EMG | 4/20 = 20% | 15/20 = **75%** | 0.0006 |

**Not a threshold artefact — the whole distribution moved.** Controls in D2 did **not**
improve (`D/1` fell 40%→15%), so session-wide drift is excluded.

⚠️ **DO NOT SAY "the soldered tether works".** The swap bundled **tether construction +
connector re-seating + an isoflurane episode**, and arm A was the only block with no
preceding anaesthesia. The handling control (arm A2) was **ruled out on welfare grounds**.
Partial evidence against the anaesthesia explanation: arm B drifts up across the block
(rho +0.51) yet stayed 10/10 connected in **both** halves.

🔴 **B1 WAS SACRIFICED 2026-08-05 BECAUSE ITS SKULL ELECTRODE DETACHED (corrected 2026-08-09; it was NOT an isoflurane death and anaesthesia is not implicated). Colony n = 7**
(A1, A2, B2, C1, C2, D1, D2). Its data stands. **Arm C vs arm B in one animal — the only
comparison that isolated the SLIP RING — is permanently lost.** ⚠️ Check the anaesthesia
setup before the next induction.

📌 **NEXT (2026-08-06): D2 + long custom tether.** Only remaining animal with a real
baseline: `D/1` **11/40 = 27.5%** (headroom), `D/2` **39/40 = 97.5%** (ceiling ⇒ harm
detector). Keep D2 on **port D**; put **D1 on port B as a free concurrent control**
(rig-end connection needs no anaesthesia); first sweep **~4 min after the swap** to match
arm B; **40 sweeps**. ⚠️ It changes **construction AND slip ring together** ⇒ it tests
"does the new chain help", **NOT** "is it the slip ring".

⭐⭐ **SWEEPS ARE AUTOMATED NOW.** Allego runs on `e10ubuntu` itself. `allegoserver` gRPC on
`127.0.0.1:50051`, RPC `AllegoCore.GetIntanImpedance(port)`, **~30 s per call, and it fires
a REAL measurement** (verified: two calls 3 s apart differ). Auth = **Cognito Bearer token**
reused from `radiens.utils.interceptors.SessionMetaData._instance._id_token` after one
`AllegoClient().get_status()`; the deviceUUID path CANNOT work (`generate_hardware_uuid()`
returns nothing on Linux). `radiens` 4.0.0 has **no** impedance method; **`radiens-core`
0.0.8 exposes `get_intan_impedance(port)` officially** and should be adopted (separate venv,
never `/opt/neurosurveillance/venv`). Scripts: scratchpad `sweep_loop.py`, `remap.py`.

🔑 **THREE SILENT TRAPS.** (1) The `port` argument is ignored — all connected ports come
back. (2) **`ntvChanIdx` is GLOBAL**, so adding a port shifts everything; **always run
`remap.py` after any port change** or files get the wrong animal. (3) Only ~half of
wall-clock time is measured at 60 s cadence, so behaviour events fall in the gaps.

⚠️ **Phase is NOT a reliable classifier** — 20 sweeps killed the "180° connected vs 30-55°
open" split. Use magnitude.

See also [[movement-dependent-contact-root-cause]], [[dmm-continuity-test-result]].
