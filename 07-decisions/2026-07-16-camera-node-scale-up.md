---
tags: [decision, hardware, scale-up, raspberry-pi, cameras, cost]
date: 2026-07-16
status: approved-pending-validation
decision: "Raspberry Pi 5 1GB ($45) as the camera node for chambers 5-8, buy one first and validate before the second"
supersedes: []
---

# Camera Node Scale-Up, 4 to 8 Cameras (Jul 16 2026)

> [!abstract] TL;DR
> Raspberry Pi 5 prices jumped hard (two hikes, Nov 2025 and Feb 2026, driven by the memory shortage), so I looked at whether an NVIDIA Jetson could replace the Pi and host 6 cameras on one board instead of 2. **The answer is no, and it turns out we don't need it.**
> - **Jetson is OUT.** The Jetson Orin Nano has NO hardware video encoder at all, NVIDIA deleted the encode silicon from that specific module. Encoding our streams would run on the CPU. It also has only 2 camera connectors, not 6. At $249 it is both more expensive and worse than what we already run.
> - **The Pi price hike has a hole in it.** The 1GB Raspberry Pi 5 is $45 and Raspberry Pi EXPLICITLY exempted it from the February increase. Same processor, same speed, only less memory.
> - **Our cameras don't need memory, they need CPU.** Measured live on Pi1 and Pi2: **553 MB peak over 6 hours** on 8GB boards, flat, zero swap. Add the XDAQ sync listener's own 64 MB cap and we land at **617 MB of 1024 MB, 60%**.
> - **Decision: 2x Pi 5 1GB, $90 total, for cameras 4-7. Buy ONE first, validate it for a week, then buy the second.**
> - ⚠️ **The NVR is the real blocker, not the camera nodes.** It already throttled ~78% of the 72h run at peak 101 C with only 4 cameras. Eight cameras doubles its decode load. That gets its own decision doc, this one does NOT solve it.

---

## 1. What I was actually asking

We want to go from 4 chambers to 8. Today that means 2 more Raspberry Pi 5 boards, one per 2 cameras. Pi 5 got expensive, so the question was whether something from NVIDIA's Jetson line could be both cheaper AND denser, 6 cameras on one board.

Two separate questions hiding in there, and they have different answers:
1. Is the Pi still the right camera node? **Yes, more than ever.**
2. Can we put 6 cameras on one node? **We don't want to, see §5.**

## 2. Why the Jetson is out

| Problem | Detail |
|---|---|
| **No hardware encoder** | The Orin Nano module (part P3767) omits NVIDIA's encode engine, called NVENC (NVIDIA ENCoder), and its decoder NVDEC too. This is a deliberate cost-cut by NVIDIA on this module only, the bigger Orin NX and AGX Orin keep it. NVIDIA's own developer forum tells people to fall back to `x264enc`, which is software encoding on the CPU. RidgeRun measured "200 to 250 percent CPU across two pinned cores" for ONE 1080p30 stream. |
| **2 camera ports, not 6** | The dev kit has 2 camera connectors. Six needs a third-party carrier board (Auvidea, Leopard) or an Arducam multiplexer. Multiplexers TIME-SHARE the camera lanes, so 6 connected cameras is NOT 6 simultaneous full-framerate streams. Carrier plus cameras costs more than the Pi it replaces. |
| **Contradicts our own paper** | `06-references/lab-meeting-2026-04-10-speaker-notes.md:130`, our MouseVUER comparison says in print that "a custom AI compute board per camera is overkill for simple H.264 video" and is why their system is "expensive and hard to scale". Buying Jetsons undercuts our own published argument. |

A camera node's entire job is to encode H.264. Buying a board with the encoder deleted, to do encoding, is backwards.

## 3. The hole in the Pi price hike

Raspberry Pi raised prices twice because of the memory shortage, LPDDR4 memory competing with the AI datacenter buildout. Current Pi 5 prices:

| Variant | Price | Note |
|---|---|---|
| **1GB** | **$45** | **PROTECTED from the Feb hike** |
| 2GB | $65 | +$10 |
| 4GB | $85 | +$15 |
| 8GB | $125 | +$30 |
| 16GB | $205 | +$60, ~70% over original launch price |

Raspberry Pi's February announcement names the exemptions directly: "the $35 1GB Raspberry Pi 4 variant, and the $45 1GB Raspberry Pi 5 variant that we launched in December".

The 1GB Pi 5 is the SAME BCM2712 processor at the SAME clock. It uses single-rank LPDDR4X. The only difference from our existing boards is memory quantity. **Only the memory got expensive, and memory is the one thing our camera nodes barely use.**

## 4. The measurements, this is the load-bearing part

I queried Netdata live on both production Pis on 2026-07-16. First I confirmed the cameras were genuinely streaming and not idle, because measuring an idle Pi would make this whole recommendation worthless:

- `pi_cam_0`: 908,079 packets, 14.6 GB transferred
- `pi_cam_1`: 908,243 packets, 13.5 GB transferred
- NVR at `192.168.0.50` attached as an RTSP consumer on both streams

Real, sustained load. Then the numbers, using 6-hour MAXIMUM rather than average, so this is the worst case and not a lucky sample:

| Metric | Pi1 | Pi2 |
|---|---|---|
| RAM used, 6h peak | **553 MB** | **545 MB** |
| RAM used, current | 555 MB | 515 MB |
| Page cache | 667 MB | 654 MB |
| CPU, 6h peak | 11.2% user + 5.5% system | - |
| Swap I/O | **0** | - |

Peak equals current, so the working set is FLAT. No memory leak, no slow growth, no swap pressure. Both boards are 8GB and using about 7% of it.

### Does the XDAQ sync listener fit too?

This was the open question, since hardware sync isn't deployed yet and so isn't in the measurement above. It fits, and our own spec already said so before I asked:

`01-infrastructure/hardware-sync/gpio-sync-service.md:52` caps the service at **`MemoryMax=64M`** and **`CPUQuota=10%`**. That cap was written 2026-04-13, months before this question came up, so it's an independent estimate rather than one fitted to the answer. The listener is interrupt-driven, it blocks in `gate_line.event_wait(sec=1)` and does nothing until a signal edge arrives, and edges only happen twice per session (recording start, recording stop). It does NOT poll.

### The projection for a 1GB board

```
  553 MB   measured 6h peak (go2rtc + 2x rpicam-vid + Netdata + OS)
+  64 MB   gpio-sync hard cap from its own systemd unit
---------
  617 MB   of 1024 MB  =  60%
~ 400 MB   left for page cache
```

Page cache is elastic, it shrinks under pressure and it is not a requirement. The Pi writes no video to disk, it streams, so cache pressure is genuinely low. 400 MB is comfortable.

CPU does not change at all, it's the same silicon at the same clock.

## 5. Why 2 cameras per node is right anyway, not a compromise

Even if a 6-camera node existed and were cheap, I don't want it. Two cameras per node means **one board failing takes out 2 chambers, not 6**. For a 72-hour live-animal run that's the difference between losing a quarter of an experiment and losing most of it. The Pi is the cheap part, the animals and the surgery time are not. Density is a cost saving that buys a bigger blast radius, and we already know from the Waveshare PoE HAT PMIC latch-up crashes that these nodes DO fail in the field.

## 6. The decision

**Buy 1x Raspberry Pi 5 1GB ($45) now. Run it at 2 cameras plus the gpio-sync listener for a week. If it holds the 617 MB projection under real load, buy the second ($45).**

Total $90 for cameras 4-7, versus $250 for two 8GB boards or $500+ for Jetsons.

Why buy one first rather than both: the 617 MB figure is a projection built on an 8GB board's behaviour plus a spec's memory cap. It's a good projection, but this lab validates before it commits, and $45 to remove the last doubt is cheap. If it fails, we're out $45 and we buy 2GB boards at $65 instead, which still beats every alternative.

### Validation criteria for the trial board

The trial passes only if ALL of these hold over a 7-day run with 2 cameras streaming and gpio-sync active:

| Check | Pass condition | How |
|---|---|---|
| Memory headroom | RAM used stays **< 750 MB** peak | Netdata `system.ram`, `group=max` over 7d |
| No swap | Swap I/O **stays at 0** | Netdata `mem.swapio` |
| No OOM kills | Zero out-of-memory events | `journalctl -k \| grep -i "out of memory"` |
| Stream continuity | No go2rtc restarts, no stalls | `neurosurveillance/watchdog/{cam}/stall`, go2rtc API packet counts monotonic |
| CPU headroom | CPU stays **< 40%** peak | Netdata `system.cpu`, `group=max` |
| Sync listener alive | gpio-sync service never hits its 64M cap | `systemctl status gpio-sync`, `MemoryMax` pressure |

⚠️ **RUN THE TRIAL WITH NO ANIMALS IN THE CHAMBER.** This board is unproven, do NOT put it in the path of a real experiment until the 7 days pass.

## 7. Things I found on the way that are NOT this decision

These are real and need their own tickets, I'm recording them here so they don't get lost:

1. ⚠️ **The NVR is the actual scale-up blocker.** It throttled ~78% of the 72h run, peaked at 101 C, with its power limit (PL1) capped at 20W, and that was with only 4 cameras. Eight cameras doubles Frigate's decode load on a machine already at its thermal ceiling. **No camera-node decision fixes this.** Needs its own decision doc, the earlier council leaned toward a proper desktop or small-form-factor machine.
2. **A claim in our paper material is wrong.** `06-references/lab-meeting-2026-04-10-speaker-notes.md:130` says the Pi 5 "offloads H.264 encoding to the Pi's hardware block (essentially free)". The Pi 5 REMOVED the hardware H.264 encoder, `rpicam-vid --codec libav` encodes in software on the CPU cores. Our measured ~17% CPU is what makes it fine in practice, so the conclusion survives, but the stated mechanism is false and it sits inside our MouseVUER comparison. Fix before publication.
3. **The golden go2rtc config has drifted from production.** `pi_cam_0` is running live with `--roi 0.18,0.04,0.64,0.92`, but `01-infrastructure/raspberry-pi/golden-go2rtc-config.md` v5.2 has no `--roi` flag. **Rebuilding a Pi from that doc today would silently lose camera 0's framing.** Update the golden config.

## Still open

- [ ] Order 1x Raspberry Pi 5 1GB ($45), plus camera module and IR illumination for chambers 5-6
- [ ] Confirm current Korea/KAIST reseller pricing, the $45 is Raspberry Pi's list price and local pricing may differ
- [ ] Run the 7-day validation, no animals
- [ ] If pass, order the second board and provision chambers 7-8
- [ ] **Open the NVR thermal decision doc, this is the real blocker**
- [ ] Fix the "hardware encode block" claim in the lab meeting speaker notes before publication
- [ ] Update `golden-go2rtc-config.md` with the live `--roi` flag
- [ ] Confirm the 4 IR LED illuminators and the power budget scale to 8 chambers, `03-troubleshooting/incidents/boot-config-ssh-lockout.md:58` notes a boot power spike with 2 cameras + 4 IR LEDs already
- [ ] Decide static IPs and hostnames for Pi3 and Pi4, update `00-config/production-values.md`

## Sources

- [Raspberry Pi, more memory-driven price rises](https://www.raspberrypi.com/news/more-memory-driven-price-rises/)
- [Raspberry Pi, 1GB Raspberry Pi 5 now available at $45](https://www.raspberrypi.com/news/1gb-raspberry-pi-5-now-available-at-45-and-memory-driven-price-rises/)
- [Tom's Hardware, Pi 5 price increases as AI shortage bites](https://www.tomshardware.com/raspberry-pi/raspberry-pi-5-price-increases-drastically-as-ai-shortage-bites-16gb-version-now-usd205-second-price-increase-in-three-months-over-70-percent-more-expensive-than-original-msrp)
- [RidgeRun, Jetson Orin Nano software encoders](https://developer.ridgerun.com/wiki/index.php/NVIDIA_Jetson_Orin/JetPack_5.0.2/Performance_Tuning/Software_Encoders_For_Jetson_Orin_Nano)
- [NVIDIA Developer Forums, Jetson Orin Nano encoding](https://forums.developer.nvidia.com/t/jetson-orin-nano-encoding/270474)

## Related

- [[../01-infrastructure/raspberry-pi/golden-go2rtc-config]]
- [[../01-infrastructure/raspberry-pi/golden-boot-config]]
- [[../01-infrastructure/hardware-sync/gpio-sync-service]]
- [[2026-07-13-72h-4mouse-recording-audit]] — the thermal evidence
- [[../06-references/lab-meeting-2026-04-10-speaker-notes]] — the MouseVUER comparison
