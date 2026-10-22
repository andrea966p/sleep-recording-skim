---
name: 2mice-per-board-test
description: "2026-07-01: 2 mice per Intan headstage = NO (one mouse per headstage); HDMI/SPI adapter TOP socket dead, use BOTTOM only; dual headstage = 64 ch. Facts live in the vault."
metadata: 
  node_type: memory
  type: project
  originSessionId: abfbe866-1a63-40c4-8952-2c43bd0d9802
---

**2026-07-01 final test:** 2 mice per headstage = NO (two greens on one GND bus = one shared ground; use ONE mouse per headstage). The HDMI/SPI adapter TOP SPI socket is never detected (dead by design on XDAQ Core): use the BOTTOM socket only. Headstage C3313 = one RHD2216 chip, 16 real channels, 1 MISO; the C3442 dual adapter puts a 2nd headstage on the free MISO (2 mice/port x 4 ports = 8). Mouse naming locked: A1 first mouse, A2 second (dried blood), D1/D2 Diane's mice.

Details: [[2026-07-01]]

Rule: never call SDK `GetIntanImpedance` while streaming (it crashes allegoserver); impedance only with the stream OFF.
