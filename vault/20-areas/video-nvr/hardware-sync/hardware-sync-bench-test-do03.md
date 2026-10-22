---
type: procedure
area: video-nvr
status: planned
status-note: "active"
tags:
  - procedure
  - hardware-sync
  - gpio
  - bench-test
  - beginner
created: 2026-06-29
---

# Hardware sync, first bench test: prove DO 03 (pin 22) is the recording gate — beginner walkthrough

> [!abstract] What this page is
> A hand-holding, no-electronics-background walkthrough for the **first** hardware-sync step now that the **DB25 breakout** and the **8-channel USB logic analyzer** have arrived. Goal: confirm that one specific XDAQ pin turns ON when Allego records and OFF when it stops, cleanly. **No Raspberry Pi is connected in this test.** Once this passes, the wiring in [[wiring-guide]] / [[hardware-sync-setup]] is safe to build.
> Created 2026-06-29.

---

## 0. What we're trying to prove today (in plain words)

We want the video system to know *exactly* when the EEG starts and stops recording. The XDAQ box can tell us that on one of the pins of its big **DB25** connector (the 25-pin trapezoid socket on the back): pin **22**, called **DO 03**. The plan is that this pin sits at **0 volts ("OFF") when not recording** and jumps to **3.3 volts ("ON") for the whole recording**, then back to 0 when you stop.

Before trusting it, we watch that pin with the **logic analyzer** and check three things:
1. **Idle** (not recording) → pin stays flat at 0 V (OFF), *with no random blips*.
2. **Recording** → pin jumps to ~3.3 V (ON) and stays there.
3. **Stop** → pin drops cleanly back to 0 V.

That's it. If those three are true, the gate works and we can wire it to the Pis later.

> [!info] Why the logic analyzer and not just a multimeter
> A multimeter shows an *average* voltage, so it can hide short blips. The XDAQ's other candidate pin (`DAQ_ON`, pin 13) is known to emit tiny ~0.5-second pulses while idle, which would falsely trigger the system. The logic analyzer draws the signal over time, so we can *see* whether pin 22 is truly flat when idle. This is why the analyzer is a "mandatory" tool here.

---

## 1. What you're holding (the new parts)

- **DB25 breakout board** — a small board with a 25-pin connector on one side and a row of **numbered screw terminals** on the other. You plug it onto the XDAQ's DB25, and now every pin is an easy-to-reach labeled screw terminal instead of a tiny pin. Each terminal is labeled with its pin number (1–25).
- **8-channel USB logic analyzer** — a little box with a USB cable on one end and a set of thin **probe wires** on the other (usually labeled CH0–CH7 plus one or more **GND**). It plugs into the PC's USB and "watches" up to 8 wires at once, drawing each one as a HIGH/LOW (on/off) line over time on screen. Think of it as a chart recorder for digital on/off signals.

> [!tip] Which one did you get?
> Most cheap "8-channel 24 MHz USB logic analyzers" are **Saleae clones (Cypress FX2LP chip)** → use the free **PulseView** software (sigrok). If you bought a *genuine* Saleae Logic 8, use **Saleae Logic 2** instead — the steps are the same idea, only the app differs. This guide leads with PulseView.

---

## 2. Safety (read once, it's short)

- **No Raspberry Pi in this test.** We only touch the XDAQ, the breakout, and the logic analyzer. The Pi has no protection on its pins, so we keep it out entirely until this passes.
- The signal we're measuring is **3.3 V**, which is harmless to you and safe for the logic analyzer (its inputs handle 3.3–5 V fine).
- **Don't let two screw-terminal wires touch each other** while powered (that's a "short"). Keep the bare wire ends apart.
- When attaching the breakout to the XDAQ, the XDAQ can stay on or off — it doesn't matter for plugging in the breakout (we're not changing any wiring it depends on). If unsure, plug the breakout on with the XDAQ off, then power it on.

---

## 3. Install the logic-analyzer software (PulseView)

On the XDAQ PC (or whatever PC you'll plug the analyzer into):

```
sudo apt install pulseview sigrok-cli
```

Expect: installs PulseView + sigrok. (If it's already there, apt says so.)

Then plug the logic analyzer into a USB port and open **PulseView** (search "PulseView" in the apps menu, or run `pulseview`).

- In PulseView, top-left, click the **device dropdown** (it may say "Demo device"). Choose **"fx2lafw (generic driver for FX2-based LAs)"** → your analyzer → **Scan/OK**. If it shows up, the analyzer is talking to the PC. 
- If nothing shows: unplug/replug the analyzer, click the dropdown again, hit **scan**. (Driver permission issues are rare on this PC since it already runs the XDAQ; if it fails, tell me and we'll add a udev rule like we did for the XDAQ.)

---

## 4. Attach the breakout and find the two pins we need

1. **Plug the DB25 breakout** onto the XDAQ's rear DB25 connector. It only fits one way. Hand-tighten the two side screws if it has them so it doesn't fall off.
2. On the breakout's screw-terminal side, find terminal **22** and terminal **14** (they're numbered).
   - **22 = DO 03** = the recording gate (the signal we watch).
   - **14 = GND** = ground (the "zero" reference — the analyzer needs this to measure against).
3. Cut two short jumper wires (or use the analyzer's own probe wires if they have a bare/pin end). Strip ~5 mm if needed. Screw **one wire into terminal 22** and **one wire into terminal 14**. Tighten so they don't pull out.

> [!note] How to count DB25 pins if your breakout labels are unclear
> Use the printed numbers on the breakout if it has them. If you ever need to count on the bare connector: looking at the face, one row has 13 pins (1–13), the other has 12 (14–25). The shell usually molds tiny "1", "13", "14", "25" marks at the corners. But the breakout's screw terminals should be labeled — trust those.

---

## 5. Connect the logic analyzer to those two wires

- Connect the analyzer's **CH0** probe to the **terminal-22 wire** (the DO 03 signal).
- Connect the analyzer's **GND** probe to the **terminal-14 wire** (ground).

That's the whole hookup: CH0 watches the gate, GND gives it a reference. The little grabber clips or Dupont ends on the analyzer wires clip onto the bare wire ends. **Double-check CH0 is on 22 and GND is on 14** before moving on (swapping them won't break anything, but you'll get a confusing trace).

> [!warning] Only these two connections
> Nothing else is wired. No Pi, no resistors, no other pins. Just CH0→pin 22 and GND→pin 14.

---

## 6. Set up Allego so pin 22 becomes the recording gate

In Allego on the XDAQ PC:

1. Make sure the XDAQ is detected (mode **"XDAQ One (G1) with XR Headstage"**, as usual — see [[first-headstage-connection]]). A headstage doesn't need to be plugged in for this digital-pin test, but Allego must be connected to the XDAQ.
2. In the **System tab**, turn the **"BNC Breakout Board"** slider **ON**. (This is a *software* toggle in Allego — it has nothing to do with the physical breakout board you just plugged in; confusing name. Turning it on makes the DO 03 / DI channels appear and work.)
3. Find **Digital Out Control** and set it to **"Gated"**. In Gated mode, DO 03 reports "Recording status" — i.e. it follows record start/stop.
4. **Wait ~15–20 seconds** after toggling BNC Breakout Board ON for DO 03 to "populate" (the vendor warns it's slow to appear the first time).

---

## 7. Capture and read the three checks in PulseView

In PulseView:

- Set the **sample rate** to something modest like **1 MHz** and the **number of samples** to a few **M** (so it captures for several seconds). Exact numbers don't matter much; we want a few seconds of recording.
- Optional: name channel CH0 "DO03" by clicking its label.

Now do the three checks:

**Check 1 — Idle (this is the important one):**
1. Make sure Allego is **NOT recording** (and ideally not streaming either, to mimic true idle).
2. In PulseView click **Run** and let it capture ~10–30 seconds.
3. **Expected:** CH0 is a **flat LOW line (0 V) the whole time, with NO blips or pulses.**
4. ✅ Flat = good. ❌ If you see little pulses popping up while idle → the "Gated" mode or "BNC Breakout Board" toggle isn't set right (or you're accidentally on pin 13 `DAQ_ON`). Fix Allego and re-capture. **Do not proceed to wiring until idle is flat.**

**Check 2 — Recording ON:**
1. Click **Run** in PulseView again (start a fresh capture), then within a second or two **start a recording** in Allego (an actual *Record*, not just *Stream*).
2. **Expected:** CH0 **jumps from LOW (0 V) up to HIGH (~3.3 V)** right when recording starts, and **stays HIGH** for the whole recording.

**Check 3 — Stop:**
1. With a capture running, **stop the recording** in Allego.
2. **Expected:** CH0 **drops cleanly back to LOW (0 V)** and stays there.

> [!tip] How HIGH/LOW looks in PulseView
> Each channel is drawn as a line that's either at the bottom (LOW = 0 V = OFF) or top (HIGH = 3.3 V = ON). A clean gate looks like a single tall "step up" at record-start and a "step down" at stop, flat in between. The logic analyzer only cares about on/off, not the exact voltage — but a digital multimeter on pins 22↔14 should read ~0 V idle and ~3.2–3.4 V while recording if you want the exact number for your notes.

---

## 8. What "pass" looks like (write these down)

- Idle: **flat 0 V (LOW), no pulses** over 30 s.
- Recording: **steps to ~3.3 V (HIGH) and holds** for the whole session.
- Stop: **drops cleanly to 0 V (LOW)**.

If all three pass → **the recording gate works**, and the direct-wire plan ([[wiring-guide]]: pin 22 → 220 Ω → Pi GPIO 17, with a 10 kΩ pull-down, star ground to pin 14) is validated and safe to build. Save a PulseView screenshot of the record→stop transition for the methods notes.

For your records, also note the exact DMM voltage while recording (red probe on pin 22, black on pin 14) — expect 3.2–3.4 V.

---

## 9. If something's off (quick troubleshooting)

| What you see | Likely cause | Fix |
|---|---|---|
| Analyzer not detected in PulseView | driver/USB | replug, re-scan; if still nothing, ping me for a udev rule |
| CH0 flat LOW even during recording | "BNC Breakout Board" OFF, or not in "Gated" mode, or you're on the wrong pin | turn BNC Breakout Board ON, set Digital Out Control = Gated, wait 15–20 s, confirm wire is on terminal **22** |
| Little pulses while idle | wire is on **pin 13 (DAQ_ON)** not 22, OR Gated mode not set | move to pin **22**, set Gated mode; idle must be flat |
| CH0 always HIGH | wire maybe on a 3.3 V / power pin, or shorted | recheck it's terminal 22 to GND 14, nothing else touching |
| Recording starts but gate is HIGH only briefly | you used Stream not Record, or mode misread | use **Record**; "Gated" follows recording, not streaming |

---

## 10. After this passes (next steps, not today)

1. Build the star-node fan-out on the breadboard (220 Ω per Pi branch, 10 kΩ pull-down) per [[wiring-guide#Wire 1 DO 03 recording gate → Pi GPIO direct, no divider, star fan-out]].
2. Star-ground each Pi back to DB25 **pin 14**.
3. Deploy the Pi listener service per [[hardware-sync-setup]] Phase 1.
4. End-to-end MQTT test, then the 24 h jitter validation.

But **today's whole job is section 7**: prove pin 22 cleanly goes 0 → 3.3 → 0 around a recording. Nothing more.

## Related
- [[overview]] — why hardware sync, full architecture
- [[wiring-guide]] — the full BOM + pin map + star fan-out (the build after this test passes)
- [[hardware-sync-setup]] — deployment procedure (Pi listener, MQTT, validation)
- [[neuronexus-inquiry-email]] — vendor confirmation that DO 03 (pin 22) is the gate and is 3.3 V
- [[first-headstage-connection]] — getting Allego connected to the XDAQ
