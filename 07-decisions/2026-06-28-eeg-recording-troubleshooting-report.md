---
tags:
  - report
  - eeg
  - emg
  - headstage
  - grounding
  - troubleshooting
  - for-professor
created: 2026-06-28
status: draft
audience: professor
---

# EEG recording — everything that went wrong and how we fixed it (so far)

*Draft for the professor. Written informally, in my own words — I'll clean it up before sending. Covers the EEG/EMG recording rig only (the headstage, grounding, slip-ring/colors). The video-sync and the video-NVR side are separate stories — I can write those up too if you want.*

Rig, start to end: mouse dura electrodes → tether cable → slip ring (rotary) → C3410 adapter board → Intan RHD2216 headstage → SAdpt HDMI↔SPI bridge → XDAQ controller → Allego on the Ubuntu PC.

---

## TL;DR — where we are right now

- **Headstage detection: SOLVED.** It wasn't broken hardware — it was the wrong "mode" in Allego. Two days lost chasing a hardware fault that didn't exist.
- **The signal "railing" (all channels slammed to the rail): SOLVED.** The real cause was that **the animal itself had no ground** — nothing carried ground *into* the mouse, so it floated. Once I tied the animal to ground, the railing collapsed and I got a clean channel (SNR ~12).
- **Slip-ring colors were mismatched** — the ground wire was swapped onto a dead line. The slip ring is resin-potted so I can't re-pin it → **building a new one** to a corrected color→pad map, and **reinforcing the ground wire** while I'm at it.
- **One headstage (the second one) still won't show up** — that one looks like a real SPI fault. Need a socket-swap test at the rig to know if it's the headstage or the adapter.
- **Our recording setup matches the Tsukuba method** (bipolar EEG off two left-hemisphere pins + neck EMG, no cerebellum reference screw) — checked it against your lab's published protocol.

---

## 1. First hurdle: getting the PC to even see the XDAQ (around 2026-05-29)

Before any headstage, the XDAQ controller itself had to talk to Ubuntu.

- **Problem:** the box is a **Gen-1 XDAQ Core** (Opal Kelly USB inside — `lsusb` shows `151f:0130`). Not the Thunderbolt "Core2" the older notes assumed. Linux saw the USB device but Allego couldn't open it.
- **Cause:** the USB device node was read-only for normal users; Allego needs write access to push the FPGA bitfile.
- **What worked:** one udev rule giving the `plugdev` group write access (`/etc/udev/rules.d/60-opalkelly.rules`), reload, replug. No root, no Thunderbolt, no extra driver install — Allego already ships the Opal Kelly FrontPanel library. After that the device came up healthy (30 kHz, connected), just with no headstage attached yet.
- Side note: a bad USB-C cable had it falling back to USB 2.0 speeds at first — a good cable gave full USB 3.0.

Status: **resolved.**

---

## 2. The headstage wouldn't show up — and I wasted two days on it (2026-06-18 → 06-19)

This is the painful one.

- **Symptom:** plug in the headstage, and Allego shows **0 channels on every port**. The log literally says `priSigs=0` — the controller is awake and scanning the SPI bus, but **no chip answers on any port**. Only the onboard inputs/outputs enumerate.
- **What I assumed (in order):** the SAdpt HDMI↔SPI bridge wasn't passing signal → the XDAQ's headstage port was faulty → the headstage was dead on arrival → some firmware/timing lag.
- **Everything I tried:**
  - plugged/unplugged both mice, removed the splitter, went down to a single bare headstage — still 0
  - reseated the HDMI, tried **both SPI cables**, tried **both sockets** on the SAdpt, tried **three different XDAQ ports** — still 0
  - swapped in a **brand-new SAdpt** → still 0 (so it's not the adapter)
  - swapped in a **brand-new spare headstage** → still 0 (so it's not a dead headstage — two of them can't both be dead)
  - full power-cycle, 3-minute boot wait, PC restart — still 0
  - checked **power with the multimeter** at the headstage: **3.56 V** while streaming → power is fine, so "no power" is ruled out. (First reading looked like 3.3 V but that was the cheap meter floating on open leads — ignored it.)
- **What actually fixed it:** the **Allego "system mode" was wrong.** It was set to **SmartBox Pro**, which *connects* and scans and enumerates the onboard I/O — so everything *looks* alive — but it reports `priSigs=0` because it's the wrong headstage profile. The moment I switched to **"XDAQ One (G1) with XR Headstage"** the headstage appeared instantly: 32 channels on Port D, signal streaming.
- **The trap:** the controller is *badged* "XDAQ **Core**", so the obvious-looking dropdown entry "XDAQ Core (G1)…" is the wrong one. The one that actually works is "XDAQ **One** (G1) with XR Headstage." Pick the mode that gives channels, not the one that matches the label on the box.
- **Lesson (the expensive one):** *the controller connecting is NOT the same as the controller being in the right mode.* All that hardware swapping was a false trail — but at least it proved the hardware is healthy. I had escalation emails drafted to NeuroNexus and Kontex; never had to send them.

Status: **resolved — it was never a hardware fault.**

---

## 3. Now the signal looked terrible — every channel slammed to the rail (2026-06-19 → 06-22)

Headstage detected, but the traces were garbage.

- **Symptom:** almost every channel pegged at about **10–12 mV peak-to-peak** and just sitting there saturated, values wandering between reads.
- **Why that number matters:** the amplifier can only "see" a window of about **±5 mV (≈10 mV pk-pk)**. Anything outside that slams against the rail. So 10–12 mV pk-pk everywhere = the inputs are being driven out of range. A clean channel should be tens to a few hundred µV.
- This is the classic **"floating animal"** fingerprint: if the animal isn't tied to the amplifier's ground, its whole voltage drifts out of the window and every channel rails together.

Some of the actual numbers I pulled (2026-06-22, raw, RMS / pk-pk in µV):

| channel | what it is | RMS | pk-pk | verdict |
|---|---|---|---|---|
| D/1 | M1 EEG+ | 111 | 489 | ok |
| D/2 | M1 EEG− | 380 | 2317 | high |
| D/3 | M1 EMG+ | 80 | 464 | ok |
| D/4 | M1 EMG− | 2980 | **11108** | railed |
| D/9 | M2 EEG+ | 2431 | 9408 | railed |
| D/10 | M2 EEG− | 2454 | **11531** | railed |
| D/11 | M2 EMG+ | 2344 | 9023 | railed |
| D/12 | M2 EMG− | 2803 | 10345 | railed |

All four Mouse-2 channels railed = Mouse 2 fully floating. I couldn't even judge the two-mice idea while everything was saturating — judging the signal then would just be judging noise. Ground first, evaluate after.

Status at this point: **diagnosed as a grounding problem, fix pending.**

---

## 4. Adding the grounding busbar (2026-06-23 → 06-26)

First attempt at fixing the ground properly.

- The greens (the ground wires) had been soldered onto **signal pads** — pad 5 and pad 13 — which are amplifier *inputs*, not ground. That alone makes the animal float.
- **Plan:** a small **brass grounding busbar** (a 5-screw bar where all 5 screws are one common piece of brass = one electrical node) used as a clean "star" hub. Move the greens off the signal pads onto the bar, and run one wire from the bar to the board's `GND` pad.
- I soldered a little socket onto the C3410 `GND` pad and a wire from there to the busbar.

But after all that — **still floating, still railing.** 10 of 12 channels still pegged at ~10–12 mV. So the busbar alone didn't fix it. End of that day my prime suspect was a **cold solder joint** on that freshly-soldered GND socket (connected mechanically but not electrically).

---

## 5. The turning point — the cold joint was a red herring; the animal just had no ground (2026-06-27)

This is the day it actually got solved.

- I was at my desk (no XDAQ on hand), so I did pure **multimeter continuity (beep) tests** on the ground chain:
  - **(1a)** board `GND` pad ↔ the soldered GND socket → **beeps** ✅
  - **(1b)** board `GND` pad ↔ the headstage's own ground → **beeps** ✅
  - **(1c)** wiggle everything while probing → stays solid, no flicker ✅
  - and the whole tether/slip-ring/busbar path beeps end to end.
- So **there was no cold joint.** The entire *system-side* ground was solid the whole time.
- **The real cause:** the busbar grounds the **headstage/system** — but **nothing was carrying that ground into the mouse.** No electrode tied the animal's body to ground. So the animal floated, and a bipolar amp with a floating subject rails every channel. The ground was "connected" — just not connected to the *animal*.
- **The fix:** dedicate one dura-contacting skull pin as the animal ground → run the tether **green** wire from that pin → busbar → board `GND`.
- **Result, live, same evening:** connected the green to the animal ground and the **railing collapsed.** A real noise floor appeared (~35 µV), and one channel came up genuinely clean:
  - **ch1: RMS 30 µV, pk-pk 178 µV, SNR ≈ 11.7** — proof a clean signal is reachable now.
  - (The other channels still looked rough, but that's because with a single mouse only 4 electrodes are wired and the rest of the inputs are just floating/open — normal, not bad electrodes.)
- **Bottom line:** the animal (tissue) ground was the whole unlock. The hard problem — floating animal / railing — is **solved.** Everything left after this is bookkeeping (wiring identity, filtering), not physics.

---

## 6. The slip-ring color mismatch (2026-06-27 → 06-28)

With grounding understood, the next problem was that the **wire colors didn't line up** through the slip ring.

- The tether and the slip ring use **different color conventions**, so you can't just match color-to-color — you have to map by the table.
- The killer: a **single swap on the slip ring — green ↔ orange.** That means the tether **green (the animal ground)** no longer lands on the slip-ring line that goes to the ground bus; it lands on a **dead line**. So the animal ground goes nowhere → animal floats → the railing comes straight back. One swapped contact, but because it's the *ground*, it's fatal — you can't fix it in software.
- **Problem:** the slip ring is **resin-potted** — the pins are sealed in, can't re-pin it. → **I have to build a new slip ring** wired correctly.
- While sorting this out I also caught that the **frontal/parietal labels were backwards** in the old notes: the **green** wire is actually the **right-parietal (caudal)** dura pin = the animal ground; the right-**frontal** pin is a different (brown) line.
- **Decision: keep green as the ground.** Once I saw that properly grounding the animal is exactly what killed the railing, there was no reason to second-guess it — green → animal ground stays.

The corrected, definitive map I'm building the new slip ring to (map by slip-ring color, not tether color):

| board pad | slip-ring color | signal |
|---|---|---|
| 0 | red | EEG frontal-L (+) |
| 1 | black | EEG parietal-L (−) |
| 2 | yellow | EMG L (+) |
| 3 | blue | EMG R (−) |
| 4 | brown | dura frontal-R (extra channel) |
| 5 | purple | nothing — dead spare line, don't record it |
| 6 | orange | copper coil = environment-noise reference |
| GND bus | green | dura parietal-R = **animal ground** |
| REF | — | empty (bipolar chip needs no reference) |

EEG = pad 0 − pad 1 (the two left-hemisphere pins). EMG = pad 2 − pad 3. The copper coil on pad 6 is the cable shield (cut at the mouse end so it only picks up room/EM noise) — recorded so I can subtract it later.

---

## 7. Reinforcing the ground wire — what finally made grounding reliable (the latest step)

The ground is the one connection that can't fail, so it had to be mechanically bulletproof — and getting there took a few tries.

- **Why a thick wire at all:** I was worried about **trunking/breaking the thin slip-ring ground wire** if I bolted it straight into the grounding bus. I tried attaching the thin wire to the bus in several delicate ways and **none of them held well.**
- **What worked:** join the thin slip-ring ground wire to a **thicker wire**, locked together with **glue-lined heat-shrink + solder.** That locks the two wires in place and gives something sturdy enough to **clamp firmly into the grounding bus** without worrying about the thin wire snapping.
- **From the bus to the board:** off the **center screw** of the grounding bus, solder a **pin** that fits the **socket** soldered on the adapter board's `GND` pad.
  - **Key trick for a clean joint:** **sandpaper the pin where the solder goes** first — otherwise the solder doesn't take and you get a noisy/flaky connection.
  - Once the pin is soldered to the wire, **cover it in resin or dental cement** → strong and insulated.
- **This is what finally gave a clean, reliable solution to the grounding problem.**

Whole path, end to end: animal dura pin → green → (glue-heatshrink + solder join) thick wire → grounding-bus screw → center screw → sanded + soldered pin (resin/cement covered) → socket → board `GND` pad → headstage ground.

**One mechanical gotcha to fix:** the center screw of the bus carries this wire+pin up to the board's GND socket, and that spot is **right under the 3D-printed headstage support — which presses down hard on the wire.** Fix it one of two ways: **raise the 3D-printed headstage support**, or **attach the ground wire from the *bottom* of the grounding bus instead of the top** so the support doesn't crush it.

*(Sections 7 and 8 aren't in the lab notes yet — I'll write them into the grounding doc.)*

---

## 8. The slip-ring-to-board pin strip is fragile (a problem we still have)

On the adapter-board side of the slip ring, the wires are soldered onto a **pin strip** and resined in the order we decided — **everything except the green ground** (the ground goes to the bus / GND socket separately). That pin strip turned out to be a weak point:

- **It's flimsy.** Plugging and unplugging it into the sockets soldered on the adapter board is genuinely hard — especially in the cramped space of the **sleep-recording room rack shelf** — and the pins **bend and get damaged really easily.**
- **The resin makes it worse:** applying the resin gives off some **heat, which softens the pin strip so it bends while the resin dries.**
- **If we keep this pin strip:** the resin has to be **dried overnight with the pin strip held/clamped onto something straight** so it sets without bending. (Worth considering a sturdier connector instead.)

---

## 9. Did we pick the right recording setup? — yes

I checked our montage against your lab's own published protocol (Iwasaki, Hotta-Hirashima, Funato, Yanagisawa, *STAR Protocols* 2021, IIIS Tsukuba). It matches:

- **EEG = bipolar, between two pins on the LEFT hemisphere** (one frontal, one parietal). That's exactly our pad 0 − pad 1.
- **EMG = two crossed wires in the neck muscle** (bipolar). That's pad 2 − pad 3.
- **No separate reference electrode, no cerebellum screw** — the bipolar pair references itself. That matches our empty `REF`.
- Their surgery numbers, for reference: 4 holes, ML ±1.27 mm, the front pair 5.03 mm ahead of the back pair, epidural (don't go through the skull); left two pins = EEG, right two = anchors.
- The one thing **we add** that the paper doesn't: an **animal ground**. Their analog amplifier grounds itself; our Intan chip genuinely needs the animal tied to ground or it rails (section 5). So adding the ground electrode isn't a deviation — it's required by our hardware.

So no cerebellum screw needed — the no-reference bipolar setup is the validated house method.

---

## 10. Smaller headaches worth noting

- **Sample rate — can't record at 128–256 Hz.** The dropdown's lowest entries are **625** and **1000 Hz** (then up to 30k). So there's a 625 option, but still nothing at 128/256, and 1 kHz is the practical floor for normal acquisition. Plan: **acquire at 1 kHz and down-sample to 256 Hz offline** (with a proper anti-alias filter) — identical data for sleep, smaller files. Also: **switching the mode resets the sample rate**, so I have to re-set it every session.
- **Allego backend crashes** if you reload sensors / select-deselect channels too fast — it spams dozens of garbage "notifications" with nonsense dates. It's the software backend crashing, not the wiring. Fix = restart Allego, re-set mode + electrodes + channels, let it settle.
- **Channel-selection trap:** with the custom sensor map loaded, the channel chips are labeled by *site number*, so you tick **sites 1–8** to get both mice — ticking "1–8" as the raw `D/n` labels silently records the wrong channels and one mouse never streams.
- **Recording file format (XDAT):** figured out the format — it's **float32, already in microvolts** (not int16, no scaling factor needed). Verified by recording a test clip and reading it back; the offline filter pipeline runs on it.
- **Python environment gotcha:** the project's venv has NumPy 2 but a broken SciPy, so the filtering scripts need a **separate analysis environment** (numpy 2.5 + scipy 1.18). The file reader itself is NumPy-only and runs anywhere.

---

## 11. Still open

1. **The second headstage still won't enumerate.** After everything above, the single-mouse headstage on the *second* SAdpt socket still shows 0 channels (`priSigs=0`), and this one looks like a **real SPI signal fault**, not the mode issue. Bench tests found no short and no bent pin, but a signal-contact fault only shows under live clocking. **Decisive test: swap sockets at the rig** — move the dead headstage to the known-good socket and a working headstage to the suspect socket. If the fault follows the headstage → headstage is bad (RMA). If it stays on the socket → that adapter socket/HDMI path is bad. (Haven't done it yet — needs me at the rig.)
2. **Build + verify the new reinforced slip ring**, beep-test the whole ground path, then power up and confirm the railing stays gone. After that: bandpass filter (EEG 0.5–30 Hz, EMG 10–300 Hz) + 50 Hz notch + paired reference, a tap-test to confirm channel identity, then record for real.
3. **Surgery requirement going forward:** every implant must include a real **animal-ground dura/bone pin** wired to one tether pin. This is now a surgical step, not something I can fix later in software.

---

*Related notes in the vault: [[2026-06-19]], [[2026-06-22]], [[2026-06-26]], [[2026-06-27]], [[2026-06-28]] (daily logs); [[first-headstage-connection]], [[grounding-reference-noise-concepts]], [[signal-quality-and-grounding]], [[signal-mapping-guide]], [[tsukuba-sleep-recording-method]], [[intan-headstage-troubleshooting]].*
