---
name: openephys-scale-up-option
description: "Open Ephys as a 16-mouse DAQ path: extension board dead (reply 2026-07-23), 16 = 4 boards or custom Atlanta build; OE GUI drives our XDAQ license-free. Detail in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: dfe12453-7955-4bc1-a2fe-bdca0e0878a9
  modified: 2026-10-22T00:00:00.000Z
---

Open Ephys Acquisition Board (2026-07-21, reply from OE Support 2026-07-23): the `extension-board` route to 16 headstages is DEAD (OE disowns the repo README). 16 mice = 4 boards synced via I/O boards, or a paid custom board from the OE Atlanta team; no per-animal ground-isolation product; software is free. XDAQ ONE+ still leads. The OE GUI + XDAQ-OE plugin fully drives our Gen-1 XDAQ licence-free (validated 2026-07-23; plugin needs a symlink fix on GUI 1.1.0).

Details: [[2026-07-21-openephys-acquisition-board-scale-up-option]] · setup + caveats [[openephys-gui-setup-xdaq-sleep-eeg]] · [[openephys-inquiry-email]] · [[acquisition-device-16-32-mice]]

- ⚠️ Close Allego before OE (one process owns the Opal Kelly USB `151f:0130`); never reflash the production Core without KC.
