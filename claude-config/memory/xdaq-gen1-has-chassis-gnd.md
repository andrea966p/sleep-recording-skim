---
name: xdaq-gen1-has-chassis-gnd
description: "Gen-1 XDAQ Core DOES have a chassis GND wired to building earth (confirmed 2026-09-30); the 07-16 'no chassis GND' claim was wrong. Noise series detail in the vault"
metadata:
  type: project
---

Andrea confirmed 2026-09-30 (DMM continuity): the Gen-1 XDAQ Core has a chassis GND terminal wired to the wall-socket (building) earth. The vault's "no chassis GND" claim since 2026-07-16 was wrong (correction callouts added). Whether a separate Sys GND exists on the Gen-1 is still unverified.

Details: [[2026-09-30-xdaq-noise-series]] · [[noise-hunt-verdict-2026-10-06]]

- Treat chassis-GND tests (earth-wire lift, shield bond) as possible: the false claim made earlier agents drop them as "not executable".
- Record noise tests with the DIRECT USB cable (the FIT1019 isolator doubled broadband noise on open inputs); test files go in `~/radix/noise-tests/`, never `~/radix/data`.
