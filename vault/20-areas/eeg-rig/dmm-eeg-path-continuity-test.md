---
tags: [procedure, eeg, electrodes, multimeter, diagnostics, bench-test]
created: 2026-08-04
status: CLOSED — run and passed fleet-wide 2026-08-04
---

# DMM continuity test on the EEG path — the free tier-1 bench test

> [!success] ✅ CLOSED 2026-08-04. Run on the whole fleet. Everything passed.
> **Do not run this again, and do not re-open the hypotheses it killed.**
>
> | section | result, every board |
> | --- | --- |
> | §4.2 mapping, pad ↔ slip-ring pin | **PASS** — every pad beeps to its own pin, nothing else |
> | §4.3 resistance | **no differential** — 0 to 200 Ω probe chatter on all four pads, EMG controls included |
> | §4.4 360° rotation | **PASS** — beep solid and unbroken |
> | §4.5 short hunt | **PASS** — no bridges |
> | joint inspection | **PASS** — no solder crossing outside its own pad, no cross contamination |
>
> **Killed by this test:** cold solder joint on pad 0 or 1 · the slip ring as a
> statically broken conductor · the fault being per pad rather than per channel
> type (B1 passed on pads 2/3) · board leakage or bridging.
>
> **Two artefacts, both benign, recorded so nobody re-chases them.** A
> **capacitor charge transient** looks like leakage: ~1100 to 1800 that vanishes to
> open, values not repeatable across re-probes, no beep, identical on every pair
> including the pad 2 to pad 3 control. A real short is a steady near zero **with a
> beep that stays on**; short the probes together before each pair to dump the
> charge. And **vias beep** — the small plated dots on the back of the board are
> the traces surfacing, which is expected and useful for tracing a net.
>
> **Photographs were not taken, by choice.**
>
> **What it did not settle.** The rotation was by hand, unloaded, at rest, so the
> slip ring is cleared only of what a static test can see. Within the hour the real
> picture emerged: the contact is **intermittent, fast and reversible**, and the
> electrodes are good. **§6 below is superseded** — step 2, the port swap, was
> discharged incidentally when B1 worked in both port B and port D.
> **Go to [[2026-08-04-movement-dependent-contact]].**

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A multimeter test on the rig side of the slip ring that asks
> one question: *do the two EEG wires actually reach the amplifier board?* It
> touches no animal, needs no anaesthesia, costs nothing, and takes about half
> an hour for the three animals that matter.
>
> **Why it exists.** Three of our animals have perfect EMG and completely dead
> EEG through **the same tether, the same slip ring, the same board, the same
> headstage and the same port**. That pattern looks like a failed EEG implant,
> but a cold solder joint on one pad, or one broken slip-ring wire, produces
> exactly the same pattern. This test tells the two apart. It has a built in
> control, because the EMG pads on the same board are demonstrably working.
>
> **How to read this page.** §1 safety, §2 what you need, §3 the map, §4 the
> test itself, §5 what each result means. Do not skip §1.
>
> Meter reference: [[multimeter-guide]]. Wiring: [[rig-assembly-guide]],
> [[CANONICAL-allego-channel-selection]].

> [!danger] Rule out this test before anyone concludes anything about surgery
> "EMG works, EEG dead, same animal" is **not** proof that the EEG implant
> failed. Until this test is done, the cheapest explanation has not been
> excluded, and **no surgery should be scheduled on the assumption that it has**.
> Intervention hierarchy: [[2026-08-02-run2-preregistration]] §4.

---

## 1. Safety and preconditions — read before touching anything

> [!danger] The animal must be disconnected from the slip ring first
> A multimeter in resistance or continuity mode **injects its own test current**.
> That current must never have a path into an implanted animal. Unplug the
> tether at the slip ring so the animal side is fully isolated, and confirm it
> by eye before the first probe touches anything.

> [!danger] Power off, and the headstage off the board
> 1. **Stop acquisition** in Allego or Open Ephys and **close it**.
> 2. **Power down the XDAQ**, and unplug the SPI cable.
> 3. **Lift the RHD2216 headstage off the C3410 board.**
>
> Reason for 3: with the headstage seated, your probes drive the meter's test
> current straight into the amplifier inputs. The RHD2216 input pins are the most
> ESD sensitive thing on the rig. Take the headstage off, put it on the antistatic
> mat, and probe a bare board.
>
> Continuity and resistance are **power off** tests, always. Only DC volts is
> ever done on a live rail. See [[multimeter-guide]] §5.

**Nothing in this procedure requires touching, moving, or anaesthetising an
animal.** If a step seems to, stop: you have wandered out of tier 1.

**Do not** attempt to "reseat" an electrode or an EMG wire. That is not a thing
that exists after implantation. The only animal side option is a tether change,
which needs isoflurane and ruins a running batch.

---

## 2. What you need

| Item | Note |
| --- | --- |
| Harden 661002 DMM | black probe in `COM`, red in `VΩmA` |
| Magnifier or phone macro | for inspecting the pad 0/1 joints |
| Antistatic mat | for the headstages you lift off |
| The recording sheet in §4.6 | print it or copy it into today's journal |
| Soldering iron + flux | **only if** a joint needs reflowing, §5 |

Meter settings used here:

| Test | Dial | Range |
| --- | --- | --- |
| Continuity, path present or not | **beep `•)))▶|`** (right of `200`, left of `hFE`) | beep |
| Resistance, how good the path is | **Ω** | `200` |
| Short hunting between pads | **beep `•)))▶|`** | beep |

---

## 3. The map — what is being tested, and what the control is

The signal chain, animal on the left:

```
mouse dura electrodes ─► tether ─► [ SLIP RING ] ─► fan-out wires ─► C3410 pads ─► headstage ─► XDAQ
                                        ▲
                              unplug the tether HERE
                        everything to the RIGHT is free to probe
```

The four wired pads on every C3410 board:

| C3410 pad | slip-ring colour | electrode | chip pin | Allego | status |
| --- | --- | --- | --- | --- | --- |
| **0** | red | EEG frontal-L | `in0+` | `/1` EEG | ⬅ **suspect** |
| **1** | black | EEG parietal-L | `in0−` | `/1` EEG | ⬅ **suspect** |
| **2** | yellow | EMG left | `in1+` | `/2` EMG | ✅ **control** |
| **3** | blue | EMG right | `in1−` | `/2` EMG | ✅ **control** |
| `GND` | green | parietal-R dura | animal ground | not recorded | reference |
| `REF` | — | — | — | — | **empty by design** |

> [!important] Pads 2 and 3 are the whole point
> They run through the same board, the same fan-out, the same slip ring, and on
> A1 and D1 they are **proven working** by 27.9 hours of clean EMG. So they tell
> you what a good reading looks like **on this exact rig, today**, with your
> probes and your technique. Any judgement about pads 0 and 1 is made **relative
> to pads 2 and 3**, never against an absolute number.

> [!bug] Do not trust wire colour
> The tether and the slip ring use **different colour conventions**, and the
> current slip ring has a known **green ↔ orange swap** on its own side. Colour
> names are documentation, not evidence. §4.2 below establishes the mapping by
> measurement instead, which is why it comes first.
> Background: [[grounding-reference-noise-concepts]] §3.

### Which animals, and in which order

| Order | Animal | Why it is informative |
| --- | --- | --- |
| **1** | **A1** | EMG perfect (0.087 MΩ), EEG open the entire 27.9 h. Cleanest case in the fleet |
| **2** | **D1** | Same pattern (EMG 0.202 MΩ, EEG open). An independent replication of whatever A1 shows |
| **3** | **B1** | The mirror image: best EEG in the fleet (0.133 MΩ) but **dead EMG**. If the fault is per pad rather than per channel type, B1 should fail on pads 2/3 instead |

Three animals is enough to decide. Do the other five only if these disagree
with each other.

---

## 4. The test

Budget about 10 minutes per animal once you have done the first one.

### 4.1 Set up

1. Acquisition stopped, software closed, **XDAQ powered down**, SPI unplugged.
2. **Unplug the tether at the slip ring.** Confirm by eye. The animal is now
   electrically isolated and stays that way for the whole procedure.
3. Lift the headstage off the C3410 board, onto the antistatic mat.
4. Meter: black in `COM`, red in `VΩmA`, dial to **beep**.
5. **Prove the meter works:** touch the two probes together. It must beep and
   read near `0`. Do this again every time you pick the meter up. A dead battery
   reads "open" on everything and would make a healthy rig look catastrophic.

### 4.2 Establish the mapping by measurement, not by colour

Do **not** assume which socket contact belongs to which pad. Find out.

1. Put one probe on **C3410 pad 2** (a known good EMG pad).
2. Touch the other probe to **each contact of the slip-ring socket in turn**,
   the one the tether plugs into.
3. Exactly one contact should beep. **Write down which one.** That is the socket
   contact for pad 2.
4. Repeat for **pad 3**, then for **pad 0**, then for **pad 1**.

Record it as you go:

| pad                | socket contact that beeps | beeped? |
| ------------------ | ------------------------- | ------- |
| 2 (EMG L, control) |                           | yes     |
| 3 (EMG R, control) |                           | yes     |
| 0 (EEG frontal)    |                           | yes     |
| 1 (EEG parietal)   |                           | yes     |

> [!tip] This step alone may end the investigation
> If pad 0 or pad 1 beeps to **no contact at all**, while pads 2 and 3 each find
> one cleanly, you have found the fault, on the rig side, for free, and it is
> repairable at the bench. Go to §5.

### 4.3 Measure the quality of each path, not just its presence

The beeper hides the difference between a good joint and a marginal one. Switch
the dial to **Ω, `200` range**, and repeat the four measurements, this time
recording the number.

| pad | resistance to its socket contact | verdict |
| --- | --- | --- |
| 2 (control) | ____ Ω | |
| 3 (control) | ____ Ω | |
| 0 | ____ Ω | |
| 1 | ____ Ω | |

Expect a **few ohms at most**, dominated by probe and lead resistance. What
matters is that pads 0 and 1 sit **in the same range as pads 2 and 3**. A pad
reading tens of ohms while its neighbours read single digits is a marginal
joint, even though it beeps.

### 4.4 ⭐ The rotation test — the one most likely to find our fault

**Do not skip this.** Our failure is *intermittent*: contact has been observed
flipping state 522 times in half a second. A slip-ring contact that opens as the
ring turns produces exactly that, and a static probe never sees it.

1. Meter on **beep**.
2. Probe **C3410 pad 0** and its socket contact, and hold both steady.
3. **Slowly rotate the slip ring through a full 360°**, taking about ten seconds.
4. The beep must stay **solid and unbroken** for the entire rotation.
5. Repeat for **pad 1**, then for **pads 2 and 3** as the control.

| pad | beep solid through 360°? | angle where it dropped, if any |
| --- | --- | --- |
| 2 (control) | ☐ | |
| 3 (control) | ☐ | |
| 0 | ☐ | |
| 1 | ☐ | |

**Any flicker is a positive finding**, even a single one. Note the approximate
angle. If pads 0 and 1 flicker where 2 and 3 do not, the slip ring is the fault
and the implants are exonerated.

While you are there, do the **wiggle test** from [[multimeter-guide]] §3b: with
the beep held on a pad, gently flex the fan-out wire right at the solder joint.
Flicker means a cold joint.

### 4.5 Short hunting — the opposite failure

An open path is not the only way to lose EEG. A bridge kills it too, and our
boards have shown bridges and icicles before.

Meter on **beep**. None of these may beep:

| probe A | probe B | must |
| --- | --- | --- |
| pad 0 | pad 1 | **NOT** beep (a bridge shorts the EEG pair into silence) |
| pad 0 | `GND` | **NOT** beep |
| pad 1 | `GND` | **NOT** beep |
| pad 0 | pad 2 | **NOT** beep |
| pad 1 | pad 3 | **NOT** beep |
| `REF` | anything | **NOT** beep — `REF` is empty by design |

> [!note] A climbing number with no beep is normal
> On the resistance ranges, a reading that climbs and then settles to `1` with
> **no beep** is a decoupling capacitor charging through the meter, not a short.
> A real short is a steady near `0` **with a beep that stays on**.
> [[multimeter-guide]] §1.

Finally, **inspect pads 0 and 1 under magnification** and compare them side by
side against pads 2 and 3. You are looking for a dull, cracked or balled joint,
an icicle, or a wire sitting on top of the pad rather than wetted into it.
**Photograph all four pads** before touching anything with an iron.

### 4.6 Recording sheet

Copy this into `04-journal/2026-08/2026-08-04.md`, one block per animal.

```
ANIMAL: ____   board serial/position: ____   time: ____
meter zero check (probes touched): ____ Ω

               socket contact   beep   Ω     360° rotation   wiggle
pad 2 (ctrl)   ____             ☐      ____  ☐               ☐
pad 3 (ctrl)   ____             ☐      ____  ☐               ☐
pad 0 (EEG)    ____             ☐      ____  ☐               ☐
pad 1 (EEG)    ____             ☐      ____  ☐               ☐

shorts: 0-1 ☐none  0-GND ☐none  1-GND ☐none  0-2 ☐none  1-3 ☐none  REF ☐none
joints under magnification: pad0 ____  pad1 ____  pad2 ____  pad3 ____
photos taken: ☐
```

---

## 5. What each outcome means, and what to do next

| What you found | What it means | Next action |
| --- | --- | --- |
| **Pad 0 or 1 does not reach any socket contact**, pads 2 and 3 do | Broken fan-out wire or a failed joint, **rig side** | Reflow the joint; if it still fails, replace that fan-out wire. Re-test, then re-sweep impedance |
| **Pad 0 or 1 reads much higher Ω** than 2 and 3 | Marginal joint | Reflow it. Re-measure. Should drop to match the controls |
| **Beep flickers during rotation** on 0/1 but not 2/3 | ⭐ **The slip ring is the fault.** Implants exonerated | The ring is resin potted and **not re-pinnable**: a new slip ring must be built. Do not compensate at the busbar or tether end |
| **Pad 0 to pad 1 beeps** | Bridge shorting the EEG pair | Clear the bridge, re-inspect under magnification |
| **Anything beeps to `GND`** | Bridge to animal ground | Clear it. This alone would kill the channel |
| **All four pads identical, stable through rotation, no shorts** | The free tier is **exhausted** and the fault is genuinely upstream of the slip ring | Go to §6 |
| **B1 fails on pads 2/3 instead of 0/1** | The fault is **per pad**, not per channel type. Argues for a board and joint problem across the fleet | Inspect and reflow every board's four pads |

After **any** repair, re-run the impedance sweep and log it in
[[impedance-sweep-register]] with a `config-test` context label, so the before
and after are comparable.

## 6. Only if everything above comes back clean

In order, still cheapest first, and **still no surgery**:

1. **Swap the headstage** for a known good one, re-sweep impedance. Rules out
   the amplifier board.
2. **Swap the port** (A ↔ C), re-sweep. Rules out the XDAQ port and the SPI path.
3. **Swap the whole C3410 board** with another animal's, re-sweep. Rules out the
   board itself.
4. Only when 1 to 3 are all clean is the fault provably in the **tether or the
   implant**, and only then is a tier-2 tether change worth arguing for. That
   costs isoflurane and ruins a running batch, so it needs a written reason.

> [!danger] There is no tier-1 test of the tether or the implant
> Both ends of the tether are captive: one is inside the animal. The free tier
> stops at the slip-ring socket, and honestly reporting "the fault is upstream of
> here" is a real result, not a failure of the test.

> [!warning] The multimeter cannot replace an impedance sweep
> This is **DC continuity**, not impedance at 1 kHz. It answers "is this wire
> connected", not "is this electrode good". Do not put an ohm reading from this
> test into the impedance register or a methods section as though it were a
> sweep. Its value is that it sees **both** sides of each bipolar pair, which no
> impedance sweep we can run does. See [[impedance-sweep-register]].

## Related
- [[multimeter-guide]] — the meter itself: dial, jacks, cap-charge artefact
- [[impedance-sweep-register]] — every sweep, and why only half of each pair is measured
- [[CANONICAL-allego-channel-selection]] — the pad map. If any page disagrees, that one wins
- [[rig-assembly-guide]] — the full chain, slip ring to headstage
- [[grounding-reference-noise-concepts]] — the slip-ring colour swap defect
- [[2026-08-02-run2-preregistration]] — the intervention hierarchy this test sits at the bottom of
- [[electrode-failure-and-impedance-literature]] — why the EEG/EMG asymmetry does not by itself prove an implant fault
