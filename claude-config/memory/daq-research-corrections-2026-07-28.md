---
name: daq-research-corrections-2026-07-28
description: "8 primary-source corrections (2026-07-28): Core has NO isolation, Port Expander mandatory for 16/box and mains powered, per-animal scheduling caps at 8 (do not buy Allego), Intan only via White Mountain, OE ground isolation impossible."
metadata: 
  node_type: memory
  type: project
  modified: 2026-07-28T06:33:32.710Z
  originSessionId: a71f4126-a668-426f-b904-b7936fd73591
---

From 5 parallel research agents on PRIMARY sources. Core has "Signal Isolation: No" (all 8 mice share one power/ground circuit); Port Expander is MANDATORY for 16/box and treat it as MAINS powered (the 2024 manual's battery claim is stale); radiens per-animal scheduling is per-PORT and caps at 8, so 16 independently schedulable animals is unreachable and the Allego licence does not deliver what justified it; Intan sells only via White Mountain Systems (no Korea distributor); OE vendor confirmed 8 headstages per board in writing; OE reply 2: per-animal REFERENCING is already independent on any system (RHD2216 has no REF pin), per-animal GROUND isolation is impossible on OE.

Details: [[daq-research-findings-primary-sources]]

🔑 Justify the Port Expander as a PORT MULTIPLIER, not as the 60 Hz fix (the dominant term is the 53x electrode Z imbalance). OE's advice "ground the Faraday cage/foil" CONFLICTS with Intan's app note and the 2026-07-16 decision: do NOT re-chase it. Intan's twisted-pair advice for the RHD2216 is the actually-free item. Verify the C3442 orientation (SPI cable in the CENTER connector) on the bench.
