---
type: experiment
area: noise-hunt
status: active
status-note: "planned"
tags: [experiment, plan, noise, shielding, grounding, usb-isolator, faraday, slip-ring, tether, counterbalance, series]
created: 2026-10-02
---

# Noise troubleshooting plan: the next trials, with mice (from 2026-10-02)

> [!warning] Updated 2026-10-22: scaled down on 2026-10-06 ([[2026-10-06-noise-hunt-verdict]]) and the main target (EMG mains) was met on 2026-10-07 by the electrician's socket and rack bond. Still open: the foil busbar A/B/A (T2a/T2b; no entry yet records the busbar fitted) and Phase 3 per-mouse reliability. Phase 2 and T3 are dropped. Hub: [[_noise-hunt-hub]]

> [!success] ⭐⭐ 2026-10-07: the main target is met
> The electrician's isolated-earth socket and the XDAQ bonded to the earthed rack collapsed the mains: A2's EMG 60 Hz went from 26-33 to
> 1 µV, and the chip floors dropped 12-60x ([[2026-09-30-xdaq-noise-series#Entry 11: the electrician's work, and the first block after it (2026-10-07)|Entry 11]]).
> - **Still worth doing:** the foil busbar (T2a/T2b) as an A/B/A test. Judge it against the NEW floors (about 40 µV); the old
>   thresholds no longer apply.
> - **Still useful:** Phase 3 (per-mouse reliability).
> - 🔴 **Any future trial is judged by our scripts, not by the official QC.** The 800 µV ground gate now calls every chip UNJUDGEABLE.

> [!important] ⭐ 2026-10-06: the plan is scaled down ([[2026-10-06-noise-hunt-verdict]])
> With the per-mouse faults set aside, the room's noise is mostly a ghost. The EMG mains is the only noise that hurts, and a
> validated notch removes it in post-processing. Adopting the notch is Andrea's decision.
> - **Recommended to keep:** the electrician's isolated-earth socket, and the foil busbar (T2a/T2b).
> - **Recommended to drop:** Phase 2 (boxes, Faraday cage) and T3 (tether shield).
> - **Phase 3 stays** as per-mouse reliability work: counterbalance and slip ring, judged on long runs.

> [!abstract] TL;DR, where we are right now
> Drafted by Claude Code on 2026-10-02 from Andrea's list, for Andrea to edit. The measurements behind it are in
> [[2026-09-30-xdaq-noise-series]], and what they can and cannot say is in [[2026-10-02-noise-series-method-audit]].
>
> - **Already fine:** no electrical injection reaches the clean mice except the light timer (one event per switching, about 2 a day,
>   Fig B). EEG hum is 2-9 µV peak (A1 about 20), far under the 50-100 µV target.
> - **Still hurting the data:** the **60 Hz in the EMG**. A2 carries 13-26 µV, about the size of its quiet muscle tone, and that
>   corrupts wake staging (audit C3, Fig E). We do NOT notch, so this has to be fixed at the source, which makes it the main target.
>   After that: the switching transients, the broadband floor, and, over long runs, movement and contact artefacts.
> - **How:** one change at a time, A/B/A (before, with, before again) in one session, with the same measurement block every time,
>   using the same scripts as the no-mice series. Simplest and fully reversible trials first.
> - **Order:** prerequisites (P1-P5) → **Phase 1, nothing to build, mice stay on**: USB isolator, foil grounded, tether shield
>   termination → **Phase 2, build, mice stay on**: aluminium box, box grounded, shield to the box, Faraday cage →
>   **Phase 3, needs a tether change under isoflurane and long runs**: counterbalance arm (tether, then the whole slip ring
>   + tether), new slip ring, slip ring as the tether.
> - **New tool:** `qc/record_block.py` records one block the same way every time and logs it. It refuses while the console
>   records or post-processes. Session 1 is written out as commands below.

> [!important] ⭐ Priority after the 2026-10-02 rig session: GROUNDING first (Andrea + Claude)
> The probe tests (noise-series Entry 8) showed that the foil's potential feeds A2's floor AND its mouse's EMG (floating lead on the
> foil: floor x2.1, EMG 60 Hz x1.17; same lead with 10 MΩ to chassis: x1.25-1.4 / x1.05). That predicts, but does not yet show, that a
> SOLID bond lowers both below today's floating foil. Next session, in this order, each A/B/A:
> 1. **T2a: A2's foil solidly bonded** (crocodile lead, short) to the XDAQ chassis lug. Prediction: A2 floor down, A2 EMG 60 Hz below 19-30 µV.
> 2. **T2b: all four foils**, one star point.
> 3. **T2c: slip-ring housings**, after a DMM check (XDAQ off, mice off) that the housing is NOT continuous with any ring.
> 4. Then the aluminium boxes (T4/T5), grounded the same way.
> Solid low-ohm bonds only: a loose or high-ohm wire on a foil ADDS pickup.

> [!info] 2026-10-06: the building electrician's work (noise series, Entry 10)
> - **The rig socket will become an isolated-earth socket**, installed by the electricians. Record a block before the work and one after.
> - **The headstage foils will be joined to one earth busbar** (= T2b). Each foil can be added or removed by us, so T2a/T2b stay A/B/A tests.
> - Details and his escalation steps: [[2026-09-30-xdaq-noise-series#Entry 10: building electrician's inspection, and what he will change (2026-10-06)]].

## What we are trying to reduce, and the number each trial is judged by

The spread column comes from three **untouched** runs of these 4 mice (10-01 19:50, 20:36, 20:42), measured with
`qc/noise_scan.py` + `qc/baseline_compare.py`, the same tools the trials use. A change only counts if it is bigger than that.

| target | metric (script) | now (these mice) | untouched spread | counts as real if |
|---|---|---|---|---|
| ⭐ **mains in the EMG** | EMG 60 Hz line peak, `EMG60` (`noise_scan` `mains_peak`) | A2 31-33 µV (evening), 13-26 overnight; B1 4.1-4.5 | A2 x1.07, B1 x1.10 | B differs from A AND A' by >= x1.2, same direction |
| field pickup at the board | chip floor 60 Hz, `floor60` (gate scale) | A1 2770-2826, A2 2068-2130, B2 1800-1890, B1 740-839 µV | x1.02-1.04 (B1 x1.13) | >= x1.10 (B1 >= x1.3) |
| broadband floor | `floor_bb1-45`, `floor_hf100-450` (rms, mains masked) | A2 15.6-17.6 / 3.9; B1 7.4-8.1 / 11.0-11.7 µV | A2 x1.13 / x1.01, B1 x1.09 / x1.07 | >= x1.25 |
| tether pickup ("open-EMG probe") | 60 Hz on the two OPEN EMGs, A/2 and B/34 | 4.7-4.9 and 4.8-5.0 mV | x1.03-1.05 | >= x1.15 |
| switching transients | how many of the 5 lamp switchings reach every chip, and their peak per chip (`allchip_scan_file`, `night_events_plot`) | timer 10-02: floors 0.5-4.1 mV (Fig B); wall switch 09-30: 3-9 mV on every chip (Fig 2) | n/a | fewer switchings detected, or peaks down >= x2, in B vs A and A' |
| EEG mains (watch only) | `EEG60` | A2 3-6, B1 5-7 µV | x1.5-1.8 (tiny numbers) | not a target; flag only if it gets x2 worse |
| long-run quality (Phase 3) | stage-1 usable %, railed epochs/h, impedance duty cycle < 0.5 MΩ, flicker | overnight: A2 99.97 %, B1 100 % usable | per trial | pre-registered in Phase 3 |

Notes on the meters:
- **A2 is the best meter** (spread 1-7 % on everything except EEG60). B1 works but is noisier, and its floor sits on a few
  collapsed inputs (Fig C), so moving anything near its board will move it.
- **A1 and B2 broadband floors are useless as meters** (x2.5-4.5 on their own; their railing open EMG drives the chip). Their
  60 Hz floors are fine (x1.02).
- **The open EMGs are a free sensor.** An open input at the end of ~36 cm of analog cable (30 cm tether + 6 cm slip ring to board,
  see [[headstage-shielding-faraday-foil#Our architecture, in context (do not panic about the tether)]]) shows the pickup along
  the tether and the implant. They are the most sensitive meter for anything done to the tether (T3, T6, T7).
- **The floors do not pass through the tether or the slip ring.** The wire-free inputs sit on the board, so they see the field
  at the board only. Anything that changes the animal channels but NOT the floors comes from the tether, the slip ring, or the animal.

## The measurement block (same as the no-mice series, adapted for mice)

1. **Nothing else may record.** Recording is GLOBAL in radiens 4.0.0, so a console run and a trial cannot overlap, and a trial must
   not overlap a console run's post-processing (strip, export, upload). `record_block.py` refuses in both cases.
2. **Write down what you changed, with the clock time.** `record_block.py --note "..."` puts it in `TRIAL_LOG.tsv` next to the files.
3. **After touching anything near the mice, wait 5 min before the block.** Handling wakes them, and the first minutes after a change
   are not comparable.
   **Then hands off and step away to the SAME spot every time** (2 m or more, or leave the room) before the block. Measured on
   10-02 16:03-16:06 (noise-series Entry 8, Fig F): a hand near a headstage drops that chip's floor 60 Hz by 28-42 % for those
   seconds and adds HF bursts up to x94; waving hands -11 to -31 %; the open EMGs +28 %. Standing still at 50 cm changed nothing,
   and the mice's own EEG/EMG did not move at all. The floors are the meters, so a moving person nearby can fake or hide an effect.
4. **Record 10 min:** `$PY qc/record_block.py $D <NAME> 10 --note "<condition>"` (commands below).
5. **Standard provocation, minutes 6-8 of every block:** switch the test lamp ON/OFF 5 times, about 10 s apart, and write down the
   times. Use the SAME lamp, socket and switch every time: an LED desk lamp in the room's wall socket, covered or facing away so the
   mice see no light. **DO NOT USE THE ROOM LIGHTS WITH MICE ON.** Light pulses shift the mice's clock, worst of all in the dark phase.
6. **A/B/A:** A (as is) → change → B → change back → A'. If there is time, A/B/A/B is stronger against drift.
7. **Analysis per block** (from `eeg-emg-analysis/`, at idle priority with `nice -n 19 ionice -c3` whenever anything else records):
   - `python3 qc/noise_scan.py BASE 30 300 $D/out/NAME.json`: floors, lines, broadband over 0:30-5:30, before the provocation
   - `python3 qc/baseline_compare.py A.json B.json A2.json`: side by side, with max/min per metric
   - `python3 -m qc.allchip_scan_file BASE $D/out/NAME_allchip.csv`: which lamp switchings reached every chip
   - `python3 qc/site_floor_compare.py BASE_A 30 300 BASE_B 30 300`: per-input floors (catches a single input collapsing, like B1's)
   - `python3 qc/mice_first_look.py BASE $D/out/NAME.png`: a picture of each mouse
8. **Decide with the rule written BEFORE the session** (table above, filled in the trial sheet at the bottom). B must differ from both
   A and A', in the same direction, by more than the untouched spread. **If A and A' disagree by more than the spread, the session
   drifted: repeat it, do not interpret it.**

## P. Before the first trial (one visit, about 30-45 min, no recording)

- **P1. B1 adapter board check** (pending since the 10-02 morning). Seating, the pads under the foil (sites /6, /10-/16 region),
  any foil or wire touching pads. If anything moves, record a fresh 10 min block afterwards: it resets B1's floor.
- **P2. DMM (digital multimeter) checks, XDAQ powered off.** Probes only on the foil, the chassis GND lug and the board pads,
  NEVER on anything that ends in an implant.
  - foil ↔ chassis lug: expect open (the foil floats today);
  - foil ↔ board GND pad: expect open. If it beeps, the foil is touching ground: that is a finding in itself, and it may be B1's problem;
  - ⚠️ the AC-volts reading foil ↔ chassis is no help on the Harden 661002: its `V~` `200` range (just right of OFF) read **0.0** on
    10-02, because it resolves only 0.1 V and its ~10 MΩ input drags the foil down while measuring. Use the recording instead;
  - chassis lug ↔ board GND pad: tells us whether the amplifier ground is already tied to the chassis inside the XDAQ (the
    "Sys GND vs chassis" question left open on 09-30). It decides what bonding a shield to the chassis actually connects to.
- **P3. Where do the slip-ring wires land on the board?** Only to confirm that sites /3-/16 (/35-/48) really are wire-free, as the
  QC floor assumes. ✅ **The tether's copper shield was NEVER inserted into any pad** (Andrea, 2026-10-02): it is connected to nothing.
  The 06-28 plan in [[grounding-reference-noise-concepts]] to record it on pad 6 was never built (that page now says so).
- **P4. Pick and label the test lamp; print the trial sheet.**
- **P5. The day's baseline:** one 10 min A block, nothing changed.

## Phase 1: now, nothing to build, the mice stay connected

One session of about 2.5 h, in the light phase (ZT2-ZT8, 11:00-17:00, when the mice mostly sleep), never across 09:00 or 21:00.

### T1. USB isolator with mice
- **Why:** without mice it changed nothing in mains or switch spikes and doubled the broadband on open inputs (Entry 3, Fig 3). The open
  question is whether that rise reaches real electrodes, which have much lower impedance than a GΩ open input. With the dummy loads
  declined for now, the mice ARE the load.
- **How:** A direct → B isolator → A' direct. For each swap, the same way as Entry 3:
  1. close Allego;
  2. confirm `allegoserver` is gone (`pgrep -f "[a]llegoserver hardware"` prints nothing);
  3. swap the cable;
  4. relaunch WITHOUT `--disable-gpu`;
  5. check `XDAQ_ONE_REC`, 1000 Hz, and the link speed (`lsusb -t`: 5000M direct, 480M through the isolator).

  `record_block.py` checks the stream rate itself.
- **Judged by:** floor broadband (as in Entry 3), plus `EEG_hf` and `EMG_hf` on A2 and B1 (only if A and A' agree within x1.25). Mains as a check.
- **Prediction, written now:** floor broadband up about x2 again, mains unchanged, no visible change on the animals' EEG (its own power
  is far above a few µV).
- **Keep the isolator only if it improves something.** Otherwise stay with the direct cable, which is the current verdict.

### T2. Foil bonded to the XDAQ chassis GND (the "shared ground")
- **Why now:** the 2026-07-16 decision not to ground the foil rested on two things. First, the hum was already low, which is still
  true for the EEG. Second, the Gen-1 "has no chassis GND", which is FALSE (corrected 09-30). The EMG mains on A2 and the 2 mV floors
  say there is still field pickup to drain. Intan's rule: the shield goes to the controller's chassis ground, and the animal and the
  headstage GND must NOT touch it ([[headstage-shielding-faraday-foil]]).
- **How:** one insulated wire from the foil to the chassis GND lug. Use one wire per shield, all to that same lug (a star). If the four
  wraps are separate, bond each or join them first. Nothing else changes. A floating → B bonded → A' floating (unclip the wire).
- **Judged by:** `floor60` on all four chips, `EMG60` on A2 and B1, the open-EMG probes, and the lamp switchings.
- **Prediction:** the floors drop, because they are the field at the board. `EMG60` drops only if A2's EMG mains comes in at the
  board rather than along the tether and slip ring. **If the floors drop and the EMG does not, the EMG mains is tether-side** (go to T3/T6/T7).
- **NOT this variant:** bonding the foil to the headstage or board GND. That is the animal's ground, Intan says the tissue must stay
  isolated from the shield, and it would push shield currents into the reference.

### T3. Tether shield termination (only if the shield end is reachable at the top)
- **Why:** the analog run is about 36 cm, and the open EMGs show 4.7-5 mV of pickup on it. Today the shield is connected to nothing at
  either end, so it shields nothing.
- **How:** A as is → B shield moved to the chassis GND at the BOARD END ONLY (through the T2 bond or its own wire), with the mouse end
  still cut and insulated → A'. The tether sits on the ROTATING side of the slip ring, so a wire from the shield to a fixed ground would
  twist as the mouse turns: either a spare slip-ring channel carries it across, or it is bonded to something on the rotating side.
  Work this out before T3.
- **Judged by:** the open-EMG probes, and `EMG60` on A2 and B1.

## Phase 2: needs building, the mice can stay connected

| trial | what | A/B/A | judged by | build notes |
|---|---|---|---|---|
| **T4** | aluminium box around each headstage + board, replacing the foil | foil (in its best T2 state) → box (same ground state) → foil | `floor60`, `EMG60`, lamp switchings | insulate the inside (kapton); NO contact with pads, pins or the SPI connector; close every side including the bottom, cable holes only; keep the SPI ferrites |
| **T5** | box grounded vs floating | box floating → box bonded → floating | as T4 | same star point (the chassis lug) |
| **T6** | tether copper shield coiled and attached to the (grounded) box, never connected at the mouse end | as is → shield on box → as is | open-EMG probes, `EMG60` | single-ended: bonded at the box only; same rotating-side problem as T3 |
| **T7** | Faraday cage around the whole home cage | no cage → cage (bonded) → no cage; then floating vs bonded | `EMG60`, open-EMG probes, lamp switchings, floors as the control | see below |

**T7 details:**
- **Build it as a removable hood**, so that A/B/A is possible: mesh or foil on a frame, all six sides, a door that makes contact, and a
  small opening for the tether. Bond it with one wire to the same star point.
- **Nothing the mouse can touch may touch the cage.** That means the metal lid, the food hopper and the water spout: a grounded cage
  touching them gives the animal a second ground path through its skin.
- **Decide where the headstages sit.** Intan puts them inside and the controller outside. If they stay outside (on top), the floors
  become an internal control (field at the board only), and the animal channels show what the cage did for the tether and the
  animal. Entry 3 says switch spikes arrive "through the air or the power/earth wiring". The cage tests the air path.

## Phase 3: mechanical, needs hardware and a tether change (isoflurane), long runs

- **Why it is different:** these trials change movement and contact, and those only show over hours. Impedance screens; only a
  multi-hour recording is an outcome, and 1 h snapshots badly overstate a 24 h run.
- **Every tether change means isoflurane.** So these go with the next PLANNED tether change, never just for a short test, and mice are
  never re-tethered or rewired for a trial.
- **Design: concurrent control plus crossover.** Recording is global, so in one run two slots get the new part and two keep the old
  (same room, same night). Swap them at the next planned change. Each arm runs for at least a full light phase (12 h), ideally ZT0 to ZT0 (24 h).
- **Pre-registered metrics:**
  - primary: stage-1 usable fraction (EEG AND EMG in the same epoch), railed epochs per hour, the impedance-block duty cycle (contact
    < 0.5 MΩ, `qc/sweep_block_ports.py` + `qc/block_duty_cycle_slots.py`, stream OFF), and the flicker discriminator (bend vs break);
  - secondary: artefact bursts on the animal channels with NO floor event at the same time (contact or movement, not the
    environment), and staging r@1min, always reported with and without the EMG notch because of C3.

| trial | what | prior / prediction |
|---|---|---|
| **T8** | counterbalance arm for the tether | may not even need a tether change if the arm can take the existing tether; fewer bend-type flickers and movement bursts, electrical metrics unchanged |
| **T9** | counterbalance arm for the whole slip ring + tether | as T8, plus less torque on the slip ring |
| **T10** | new type of slip ring | on 07-15, deliberately twisting B1's slip ring barely moved a good pair (CV 9 %), so rotation itself was not the problem. Look for less contact wear over days. Options: [[headstage-shielding-faraday-foil#Commutators the field uses]] |
| **T11** | slip ring made as the tether (one cable from the head to the ring, one connector less) | fewer junctions, so fewer contact faults; same rules as T10 |

**Rules for T10 and T11:**
- build to the 06-28 plug map (**green → ground bus**, the defect that once left the animals floating);
- DMM-verify per [[grounding-reference-noise-concepts]] §5 BEFORE powering.

**Not on the list, but worth weighing later:** digitising at the head (a head-mounted headstage plus an SPI commutator). It removes
the 36 cm analog run, which Intan's "under 10 cm" rule assumes. It is a big change: weight on the head and a new commutator.

## Rules for every trial

- **ONE CHANGE AT A TIME.** On 09-30, Entry 2 changed the tape and the multitap together, and we still do not know which of the two
  removed port A's 120 Hz.
- **NO TRIAL WHILE A CONSOLE RUN RECORDS OR POST-PROCESSES** (recording is global; `record_block.py` refuses).
- **NO ROOM-LIGHT SWITCHING WITH MICE** (use the covered test lamp).
- **NOTHING GROUNDED MAY TOUCH THE ANIMAL, THE IMPLANT, THE HEADSTAGE GND, THE BOARD PADS, OR ANYTHING THE MOUSE CAN TOUCH.**
- **ONE GROUND POINT** (the XDAQ chassis lug), one wire per shield, and no second path (a shield touching the SPI connector shell,
  the board, or another shield at its far end makes a loop).
- **NEVER NOTCH 60 Hz TO CALL A TRIAL A SUCCESS.** The analysis runs on the raw file (the Monitor's notch is display-only anyway).
- **WRITE THE PREDICTION AND THE DECISION RULE BEFORE THE SESSION** (trial sheet below).

## Session 1, as commands (P5 + T1 + T2, about 2.5 h)

From `~/sleep-recording-skim/eeg-emg-analysis` on e10. T1's A' block doubles as T2's A (direct cable, foil floating).

```bash
D=~/radix/noise-tests/2026-10-03; PY=/opt/neurosurveillance/venv/bin/python3; mkdir -p $D/out
$PY qc/record_block.py $D S1-A0_baseline 10 --note "as is: direct USB + ferrite, foil floating"
# T1: close Allego, check allegoserver is gone, isolator in, relaunch, check lsusb -t = 480M
$PY qc/record_block.py $D T1-B_isolator 10 --note "USB isolator FIT1019, lamp x5 at 6-8 min"
# T1: same steps back to the direct cable (5000M)
$PY qc/record_block.py $D T1-A2_direct 10 --note "direct USB again = T2-A"
# T2: foil to the chassis lug, one wire
$PY qc/record_block.py $D T2-B_foil-chassis 10 --note "foil bonded to the XDAQ chassis GND lug"
# T2: unclip the wire
$PY qc/record_block.py $D T2-A2_foil-floating 10 --note "foil floating again"
```

Then the analysis (each block, then the two comparisons):

```bash
for b in $D/*_data.xdat; do B=${b%_data.xdat}; n=$(basename $B); python3 qc/noise_scan.py $B 30 300 $D/out/$n.json > $D/out/$n.scan.txt; python3 -m qc.allchip_scan_file $B $D/out/${n}_allchip.csv; done
python3 qc/baseline_compare.py $D/out/S1-A0*.json $D/out/T1-B*.json $D/out/T1-A2*.json
python3 qc/baseline_compare.py $D/out/T1-A2*.json $D/out/T2-B*.json $D/out/T2-A2*.json
```

## Trial sheet (fill in on the day)

| trial | date | blocks | prediction (written before) | decision rule | result | verdict |
|---|---|---|---|---|---|---|
| T1 USB isolator | | S1-A0, T1-B, T1-A2 | floor broadband ~x2 up, mains same, animals' EEG same | broadband or EMG_hf >= x1.25 vs both A blocks | | |
| T2 foil → chassis | | T1-A2, T2-B, T2-A2 | floor60 down; EMG60 down only if the mains enters at the board | floor60 >= x1.10, EMG60 >= x1.2 | | |
| T3 tether shield | | | open-EMG probes down | probes >= x1.15 | | |
| T4 box | | | | | | |
| T5 box grounded | | | | | | |
| T6 shield → box | | | | | | |
| T7 Faraday cage | | | | | | |
| T8-T11 | | | (pre-register in Phase 3) | | | |

## Still open

- P2: is the amplifier ground tied to the chassis inside the Gen-1?
- P3: are sites /3-/16 really wire-free? (The tether shield is on no pad, Andrea 10-02.)
- T3/T6: how to get the shield across the slip ring's rotating side.
- Dummy loads were declined for now (Andrea, 10-01). Until they happen, the floors are the only mouse-independent meter.
- Every geometry change in this plan moves the chip floors, so the floor guard (audit C1) cannot be judged across trials. Keep the
  per-input floor table for every block. It is also the data the C1 re-derivation needs.

Related: [[2026-09-30-xdaq-noise-series]] · [[2026-10-02-noise-series-method-audit]] · [[headstage-shielding-faraday-foil]] ·
[[grounding-reference-noise-concepts]] · [[positive-control-known-signal-injection]] · [[impedance-sweep-register]]
