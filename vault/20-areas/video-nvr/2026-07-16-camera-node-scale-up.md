---
tags: [decision, hardware, scale-up, raspberry-pi, cameras, cost]
date: 2026-07-16
status: approved-pending-validation
decision: "Hybrid nodes: keep 2 CSI cameras per existing Pi 5, add 2 USB H.264 cameras (Arducam B0490, IMX462, 940nm) → 4 cams/Pi, 8 cams total, zero new compute. Buy one camera first and validate before the rest."
supersedes: []
---

# Camera Node Scale-Up, 4 to 8 Cameras (Jul 16 2026)

> [!abstract] TL;DR
> We want to go from 4 chambers to 8. Raspberry Pi 5 prices jumped hard (two hikes, Nov 2025 and Feb 2026, memory shortage), so buying two more Pi 5 nodes got expensive. I worked through four options. The winner reuses the two Pis we already own.
> - **CHOSEN, hybrid nodes.** Keep the 2 CSI cameras on each existing Pi 5, ADD 2 USB cameras per Pi, giving 4 cameras per Pi and 8 total. **Zero new compute to buy.** The USB camera must be one that encodes H.264 ONBOARD, so the Pi just passes the stream through instead of re-encoding it. Confirmed part: **Arducam B0490** (Sony IMX462 sensor, **940nm invisible infrared**, native H.264 over USB).
> - **Why 940nm matters and this is not optional.** Dark-phase sleep experiments. An 850nm infrared LED emits a faint VISIBLE red glow, which would contaminate the animals' dark phase and confound the experiment. **USE 940nm ONLY.** The B0490 is 940nm.
> - **Why H.264-onboard matters.** A normal USB webcam outputs MJPEG, which forces the Pi to decode-then-re-encode in software, roughly doubling CPU per camera and risking thermal throttle 24/7. A camera that outputs H.264 itself avoids all of that, go2rtc remuxes it for ~free, same cost as our current CSI cameras.
> - **Cost: ~$200 for 4 USB cameras**, versus ~$240 for two Compute Module 5 nodes or ~$250 for two 8GB Pi 5 boards. And NO new nodes to rack, power, IP, or provision.
> - **Rejected:** NVIDIA Jetson (no hardware encoder, contradicts our own paper), and the first USB camera linked (Arducam B0205, MJPEG-only, 850nm, discontinued, three strikes).
> - ⚠️ **The NVR is the real 8-camera blocker, not the cameras.** It already throttled ~78% of the 72h run at peak 101 C with only 4 cameras. Eight cameras doubles its decode load. **This doc does NOT solve that**, it gets its own decision doc. I chose to buy cameras first anyway (see §7), accepting that risk.

---

## 1. What I was actually asking

Go from 4 chambers to 8. Today each Raspberry Pi 5 runs 2 CSI camera modules. The naive scale-up is 2 more Pis, but Pi 5 prices spiked. So the question became: what is the cheapest way to add 4 more camera feeds that (a) keeps the system stable, (b) stays scientifically valid for dark-phase sleep, and (c) does not make the NVR worse than it already is.

I looked at four options. §2 kills the ones that lost, §3-§5 build up the winner.

## 2. The rejected options

### 2a. NVIDIA Jetson — no

The original idea was a Jetson hosting 6 cameras on one board. Dead on arrival:

| Problem | Detail |
|---|---|
| **No hardware encoder** | The Jetson Orin Nano module (P3767) omits NVIDIA's encode engine (NVENC) AND decoder (NVDEC), a deliberate cost-cut on that module. NVIDIA's own forum says fall back to `x264enc`, software encoding on the CPU. RidgeRun measured "200 to 250 percent CPU across two pinned cores" for ONE 1080p30 stream. A camera node's whole job is to encode, buying one with the encoder deleted is backwards. |
| **2 camera ports, not 6** | Six needs a third-party carrier or an Arducam multiplexer, and multiplexers TIME-SHARE lanes, so 6 connected is not 6 simultaneous full-framerate. Carrier + cameras costs more than the Pi it replaces. |
| **Contradicts our own paper** | `06-references/lab-meeting-2026-04-10-speaker-notes.md:130`, our MouseVUER comparison already argues in print that "a custom AI compute board per camera is overkill for simple H.264 video". |

### 2b. The first USB camera linked (Arducam B0205) — no, three strikes

The B0205 (OV2710 sensor) looked attractive (integrated day/night IR) but fails on three independent counts:
1. **MJPEG/YUY2 only, NO H.264.** Forces a software MJPEG→H.264 transcode on the Pi, roughly doubling CPU per camera, on nodes feeding an NVR already at its thermal wall.
2. **850nm infrared.** Visible red glow, contaminates the dark phase. Wrong for sleep science.
3. **Discontinued.** Arducam's own page marks it `[Discontinued]`, bad for a reproducible publication BOM.

The fix for strikes 1 and 2 turned out to be a different, still-current Arducam part, see §4.

### 2c. Considered but not chosen, in order of closeness

- **Compute Module 5 node** (CM5 2GB no-eMMC ~$87 + Waveshare PoE IO board ~$44 ≈ $120/node). Genuinely good: same BCM2712 as the Pi 5, 2 CSI ports, our golden go2rtc config applies UNCHANGED, keeps the 2-cameras-per-node blast radius, and its integrated PoE sidesteps the recurring Waveshare PoE HAT PMIC latch-up crashes this lab keeps hitting. The only reason it lost: the hybrid reuses hardware we already own and is cheaper. **If the hybrid fails validation, this is the fallback.**
- **Raspberry Pi 5 1GB node** ($45, explicitly exempted from the Feb price hike, same SoC). Cheapest new-node option, but needs either the crash-prone PoE HAT or mains power at each chamber, and still adds two more boxes to rack and provision.

## 3. Why the hybrid works, the load math

Each existing Pi keeps its 2 CSI cameras and gains 2 USB cameras. The whole thing hinges on the USB camera encoding H.264 itself, so the Pi does NOT re-encode.

Measured live on both production Pis, 2026-07-16, cameras confirmed genuinely streaming (`pi_cam_0` 908k packets / 14.6 GB, `pi_cam_1` 908k packets / 13.5 GB, NVR attached as RTSP consumer):

| Metric | Pi1 | Pi2 |
|---|---|---|
| RAM used, 6h peak (`group=max`) | 553 MB | 545 MB |
| CPU, 6h peak | 11.2% user + 5.5% sys | - |
| Swap I/O | 0 | 0 |

Two CSI cameras cost ~17% CPU and 553 MB, flat, no swap, on 8GB boards.

- **If the USB camera outputs H.264 (our pick):** go2rtc ingests it as an ffmpeg device source with H.264 passthrough (remux, NOT transcode). Added CPU is near-zero, the same near-free path the CSI cameras use. 4 cameras/Pi stays comfortable on both CPU and memory.
- **If the USB camera outputs MJPEG (the B0205, rejected):** the Pi must decode MJPEG then software-encode H.264, roughly 30-40% of total CPU PER 1080p camera. Two of those on top of the 17% CSI load could pin the Pi near 100% and throttle 24/7. This is the single reason the camera choice is load-bearing, not a detail.

## 4. The camera, confirmed from the datasheet

**Arducam B0490** (Amazon `B0CQ4QDCXN`). Verified against Arducam's own datasheet PDF (`B0490_1080P_IMX462_USB_Camera_Datasheet.pdf`), not a store listing:

| Spec | Value | Why it matters |
|---|---|---|
| **Output formats** | **H.264** @ 30fps 1920×1080 / 1280×720 / 640×480 / 640×360; also MJPG, YUY2 | Native onboard H.264 → go2rtc passthrough, ~zero Pi CPU |
| **Sensor** | Sony **IMX462** STARVIS | Best-in-class low-light for this price |
| **Infrared** | **6× 940nm** LEDs + 940@650nm double-pass filter, auto IR-cut | **Invisible IR, does NOT contaminate the dark phase** |
| **Interface** | USB 2.0, UVC, no drivers | H.264 1080p fits USB 2.0 bandwidth easily |

This is the part that flips the USB option from "bad idea" to "best idea": H.264-onboard kills the transcode, 940nm keeps the sleep science clean, IMX462 handles the dark.

> [!quote] Paper-ready
> Chambers 5-8 are covered by USB cameras (Sony IMX462 sensor) that perform on-board H.264 encoding, ingested by go2rtc via stream passthrough with no host-side transcoding; 940nm infrared illumination provides night-vision imaging without introducing visible light into the animals' dark phase.

## 5. The decision

**Buy 1× Arducam B0490 now (~$50). Add it to an existing Pi already running its 2 CSI cameras, wire it into go2rtc as an H.264-passthrough stream, and run a 7-day validation. If it holds, buy the remaining 3 and provision chambers 5-8.**

Total ~$200 for 4 USB cameras, zero new compute, versus ~$240 (two CM5 nodes) or ~$250 (two Pi 5 8GB boards).

Why buy ONE first: two things about the USB path are unproven IN THIS LAB, (a) whether go2rtc cleanly ingests this camera's UVC H.264 as a stable 24/7 passthrough, and (b) whether a Pi comfortably holds 3 then 4 simultaneous camera feeds. $50 removes both doubts before committing ~$200. This lab validates before it commits.

### Validation criteria for the trial camera

Add the trial B0490 to an existing 2-CSI Pi (so the Pi runs 3 cameras during the test). Trial passes only if ALL hold over a 7-day run:

| Check | Pass condition | How |
|---|---|---|
| No transcode | go2rtc uses H.264 **passthrough**, not ffmpeg transcode | go2rtc `/api/streams`, confirm codec passthrough, no `libx264` process |
| CPU headroom | Pi CPU stays **< 50%** peak with 3 cameras | Netdata `system.cpu`, `group=max`, 7d |
| Memory headroom | RAM used stays **< 1 GB** peak | Netdata `system.ram`, `group=max` |
| No swap | Swap I/O **stays 0** | Netdata `mem.swapio` |
| Stream continuity | No go2rtc restarts, packet counts monotonic, no watchdog stalls | go2rtc API + `neurosurveillance/watchdog/{cam}/stall` |
| Thermal | Pi stays **< 80 C**, no throttle | `vcgencmd measure_temp` / `get_throttled` |
| Night image usable | 940nm illumination gives a scorable image in full dark | eyeball a night clip in Frigate |

⚠️ **RUN THE TRIAL WITH NO ANIMALS IN THE CHAMBER.** The USB capture path is unproven, do NOT put it in front of a real experiment until the 7 days pass.

⚠️ **This adds an ffmpeg device source to go2rtc, which the golden config currently forbids** ("no ffmpeg pipes"). That rule was written against ffmpeg TRANSCODE pipes for the CSI cameras, which were unstable. A UVC H.264 PASSTHROUGH is a different animal, but it is still a deviation from the golden config and MUST be proven over the 7 days before it goes near production. If it proves stable, update `golden-go2rtc-config.md` to document the passthrough pattern explicitly.

## 6. The one real tradeoff of the hybrid

**4 cameras per Pi means one board failure darkens 4 chambers, not 2.** For a 72-hour live-animal run that is the difference between losing a quarter of an experiment and losing half. We already know these nodes fail in the field (the Waveshare PoE HAT PMIC latch-up crashes). The CM5-node option (§2c) keeps the blast radius at 2 and is the fallback if this matters more than cost. Chosen the hybrid anyway for cost and hardware reuse, with eyes open.

Secondary: a USB webcam board is mechanically less rigid than a CSI module + lens for a fixed overhead mount, plan the mounting.

## 7. Things I found on the way that are NOT this decision

1. ⚠️ **The NVR is the actual scale-up blocker.** It throttled ~78% of the 72h run, peaked at 101 C, power limit (PL1) capped at 20W, with only 4 cameras. Eight cameras doubles Frigate's decode load. **No camera decision fixes this.** I chose to buy cameras first and deal with the NVR when it throttles (accepted higher risk of the NVR turning out to be the constraint that reshapes everything). Needs its own decision doc, the earlier council leaned toward a proper desktop or small-form-factor machine.
2. **A claim in our paper material is wrong.** `06-references/lab-meeting-2026-04-10-speaker-notes.md:130` says the Pi 5 "offloads H.264 encoding to the Pi's hardware block (essentially free)". The Pi 5 REMOVED the hardware H.264 encoder, `rpicam-vid --codec libav` encodes in software. Our measured ~17% CPU is what makes it fine, so the conclusion survives, but the stated mechanism is false and it sits in our MouseVUER comparison. Fix before publication.
3. **The golden go2rtc config has drifted from production.** `pi_cam_0` runs live with `--roi 0.18,0.04,0.64,0.92`, but `01-infrastructure/raspberry-pi/golden-go2rtc-config.md` v5.2 has no `--roi` flag. Rebuilding a Pi from that doc today would silently lose camera 0's framing. Update the golden config.

## Still open

- [ ] Order 1× Arducam B0490 (~$50), confirm local/KAIST reseller stock and price
- [ ] Wire it into go2rtc on an existing Pi as an H.264-passthrough stream (device source), verify passthrough not transcode
- [ ] Run the 7-day validation, no animals, against the table in §5
- [ ] If pass, order 3 more B0490 and provision chambers 5-8 (mounting, IDs, Frigate config)
- [ ] **Open the NVR thermal decision doc, this is the real blocker**
- [ ] Confirm the existing rig's infrared wavelength, if the current 4 external IR LEDs are 850nm, the old and new chambers will not match, standardize to 940nm
- [ ] Fix the "hardware encode block" claim in the lab meeting speaker notes before publication
- [ ] Update `golden-go2rtc-config.md` with the live `--roi` flag, and (if validation passes) document the USB H.264 passthrough pattern
- [ ] Add Frigate camera entries + retention for the 4 new 1080p feeds (note: 1080p USB vs 1024×768 CSI, mixed resolution, storage math differs)

## Sources

- [Arducam B0490 IMX462 USB camera datasheet (PDF)](https://blog.arducam.com/downloads/datasheet/B0490_1080P_IMX462_USB_Camera_Datasheet.pdf)
- [Raspberry Pi, more memory-driven price rises](https://www.raspberrypi.com/news/more-memory-driven-price-rises/)
- [Raspberry Pi, 1GB Raspberry Pi 5 now available at $45](https://www.raspberrypi.com/news/1gb-raspberry-pi-5-now-available-at-45-and-memory-driven-price-rises/)
- [Waveshare CM5 PoE BASE A wiki](https://www.waveshare.com/wiki/CM5_PoE_BASE_A)
- [RidgeRun, Jetson Orin Nano software encoders](https://developer.ridgerun.com/wiki/index.php/NVIDIA_Jetson_Orin/JetPack_5.0.2/Performance_Tuning/Software_Encoders_For_Jetson_Orin_Nano)

## Related

- [[golden-go2rtc-config]]
- [[golden-boot-config]]
- [[gpio-sync-service]]
- [[2026-07-13-72h-4mouse-recording-audit]] — the thermal evidence for the NVR blocker
- [[lab-meeting-2026-04-10-speaker-notes]] — the MouseVUER comparison
