---
name: eeg-60hz-mains-discovery
description: "Korea mains is 60Hz not 50Hz — EEG \"bad electrode\" weeks were mostly 60Hz hum + wrong notch"
metadata: 
  node_type: memory
  type: project
  originSessionId: f385765f-e351-48d5-99db-fea82c4d69f4
---

🔴 **2026-07-05 MAJOR:** South Korea mains = **60 Hz**, not 50 Hz. Allego notch + all vault analysis had been set to **50 Hz** for weeks, so the real interference (60 Hz) was never filtered. Single EEG legs carry ~10 mV of **60 Hz common-mode mains hum** (real EEG is tens of µV under it) → they looked "railed/open" → we wrongly concluded 8 mice were badly implanted. It's **one systematic environmental problem, not bad surgeries.**

Measured proof (all 8 mice, 4-port C3442): dominant freq = **59.9 Hz on every channel**; "railing" = ~100% 60 Hz, ~0% in 1–45 Hz band. After **60 Hz notch + bipolar difference (pad0−pad1)**: 5/8 mice give usable EEG now (M4 delta-rich); 3 (M2,M7,M8) have legs **clipping** the ±6.4 mV amp (12–17%) = unrecoverable until hum cut. Common-mode 60 Hz ranged 15 µV→4900 µV, tracking **ground quality** (A1/M1 good ground → 88 µV → clean EEG; proves rig can reject it).

**Fixes:** set Allego notch → 60 Hz; sweep 50→60 across vault + analysis scripts; cut hum at source (grounding = biggest lever, check ground loops mini-PC+cams+rig, shielding); then record non-clipping mice.

**Corrects earlier durable claim** in [[eeg-recording-state]]: "railing wired channel = OPEN input" is REFINED — a railing single channel was usually 60 Hz common-mode hum present even on good electrodes. Judge the **bipolar difference with a 60 Hz notch**, never the raw single channel.

Full: vault `20-areas/eeg-rig/60hz-mains-hum-discovery.md` + journal `04-journal/2026-07/2026-07-05.md`. Also this session: 8-mouse map finalized (passthrough_64, select `/1-4`+`/33-36` per port, 2nd headstage = native +32). See [[eeg-recording-state]].
