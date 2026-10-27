---
type: reference
area: rig-expansion
status: active
created: 2026-10-26
summary: "What the Sirenia 3.3.5 installer itself says about our Pinnacle questions (cameras, TTL, timestamps, dongles, 8474 range, files, licences), read statically from a partial download; answers to check against Pinnacle's written reply."
tags: [pinnacle, sirenia, wireless, video-sync, ttl, vendor]
---
# Sirenia 3.3.5 installer: what the files answer (static read, 2026-10-26)

> [!abstract] TL;DR
> - From Claude Code, 2026-10-26. I unpacked Andrea's download of `Sirenia_3_3_5.zip` (one 7-Zip SFX wrapping an NSIS
>   installer, "Pinnacle Technology DE LLC", 3.3.5.0, changelog dated 2026-10-19) and four agents read it statically, then a
>   fifth tried to refute their key claims. Nothing was run. Round 1 used a partial download (61 %); round 2, the same
>   evening, read the complete installer, including `Acquisition.exe` and `Sleep.exe`, and was skeptic-checked again.
> - **Wireless timestamps come from the PC clock, not the head unit.** Each sample's time is sample count x 1/rate, steered
>   by a phase-locked loop to the PC clock (or to a Master Clock pod if one is chosen). The head unit's packet counter is
>   only used to find lost packets. So a TTL Plus pulse and an 8474 sample meet only through PC arrival time, with USB and
>   Bluetooth jitter in between. No path in the code times samples from the head unit's own clock.
> - **The 8474 has no TTL** in the code (no TTL members, no TTL command), so no licence can add one. TTL pods (9085 TTL Plus,
>   Master Clock pod, 8401, 8206-HR) are separate devices. Pulses become annotations.
> - **Cameras:** any Windows camera (Qt Multimedia), HTTP MJPEG IP cameras (added 3.3.0) and a hidden "gateway" MJPEG type.
>   No RTSP and no H.264. Frames are stamped with the PC clock when Sirenia processes them, minus 0.04 s; the camera's own
>   timestamps are ignored. Video is licensed by camera count ("Video Recording 1" to "8").
> - **8474 is supported** since 3.1.2 (one driver for 8274 and 8474). One BT5 dongle carries one head unit; no limit on
>   dongles per PC was found in the library.
> - **Top risk for the custom unit:** the 14-bit, ±465 µV scaling is chosen from the model string the unit reports, and
>   there is no user override. See [[#Input range depends on the model string]].
> - **Licences (round 2):** recording from the wireless units and pods, TTL input and all exports need no licence. Video is
>   capped by the "Video Recording N" licence (up to 8 cameras). In `Sleep.exe`, opening files, hand scoring, video playback
>   and export need no licence; the licences "Sleep Analysis", "Sleep Pro" and "EVERYTHING" each unlock the same analysis
>   set (auto scoring, bouts, spectra, hypnogram).
> - **Round 3 (2026-10-27), Morelia API and firmware:** the model-string risk is confirmed in Pinnacle's own Python API too,
>   which accepts only exact names like `8474HR-SE4`. Every packet carries a head-unit clock tick nobody reads, a possible
>   route to drift correction in our own decoder. Pinnacle's `pypvfs` should read `.pvfs` on Linux.
> - Gaps: lost packets become NaN in the native file (up to 20 packets, about 1.2 s at 512 Hz). EDF export is always EDF+C,
>   so gaps only show if we choose a fill value.

## How this was done
- Source: `~/Downloads/Sirenia_3_3_5.c_CIa_x4.zip.part` on the office PC, 165 of about 270 MB, stalled 2026-10-26 17:30.
  The outer 7z uses LZMA2 + x86 BCJ; the inner NSIS installer is non-solid deflate, so every file before the cut is whole.
  The NSIS file list (all files, with sizes) is complete.
- Four analysts (licensing, video + TTL, wireless hardware, data + export) read `Acquisition/PinnacleLib.dll`
  (38.5 MB, about 20,300 exported C++ symbols), `Pvfs.dll`, `PinnacleBase.dll`, `Diagnostic/Diagnostic.exe` and
  `CHANGELOG.txt` with `objdump`, `strings` and `pefile`. A skeptic then re-derived the nine claims that matter for the
  purchase from the disassembly, and the hardware analyst answered the skeptic's corrections.
- Round 2 (same evening): the complete download (`Sirenia_3_3_5.zip`, sha256 `57a2232f...0633cd`, now in
  `~/Downloads/Organized/Archives/`) gave all 517 files. `PinnacleLib.dll` is byte-identical to the partial copy, so round
  1 stands. The same four analysts read `Acquisition.exe` and `Sleep.exe`; the skeptic re-checked seven new claims.
- Tags below: **confirmed** = seen directly in the binary or changelog; **inferred** = read from code structure, not
  seen end to end; **not found**.
- The app is native Qt 6.7 C++ (MinGW), with FFmpeg 6, OpenCV 4.5.5, libvpx, Intel oneMKL and FTDI D2XX. No .NET.
  Four app folders ship (`Acquisition`, `Sleep`, `Seizure`, `FSCV`) with identical libraries, plus `Diagnostic`.
- No manual, help file, Python package or Linux build is in the installer. `CHANGELOG.txt` is the only document.

## Answers, by the questions we sent on 2026-10-26
See [[2026-10-25-pinnacle-software-video-pc-questions-email]] for the questions.

### A. Software packages and licences
| Question | What the files say | Tag |
|---|---|---|
| What does the video licence add | Licence products "Video Recording 1" to "Video Recording 8"; the splash screen says "Synchronized Video" when any is present. Adding a camera beyond the licence shows "This would exceed your license for %1 cameras"; with none, "Video Capture is not licensed at the moment". So the licence is per number of cameras, at most 8 (checked per experiment window). | confirmed |
| Per PC, per camera or per instance | Keys are stored per Windows user in a local settings database. No machine fingerprint, online activation or seat count found. Whether one key may go on several PCs is a contract question (EULA), not a code one. | inferred |
| Camera kit "Sirenia licence key" | Part numbers 9021, 9035 and 9000-K30 appear nowhere in the files. Most likely a "Video Recording N" key. | inferred, ask |
| Sleep Pro | With no licence, `Sleep.exe` opens `.pvfs` and EDF files, scores epochs by hand, plays video and exports scores and data. "Sleep Analysis", "Sleep Pro" or "EVERYTHING" each unlock the same 20 analysis actions: cluster and threshold auto scoring, bout, power, spectral plots, heat map, hypnogram, score comparison, coherence, custom scores, plus the statistics view. Power analysis also unlocks with "Feedback Pro" or "Sleep Deprivation". "Sleep Auto Scoring" and "Video Sleep Analysis" are never checked in `Sleep.exe`. Nothing ties scoring to 512 Hz. A hidden beta auto scorer ("REST", 4 s epochs, needs EEG + EMG) calls an external `rest_score.py` that is not shipped. | confirmed (skeptic round 2) |
| Trial | No automatic install-date trial; a trial is a time-limited key from Pinnacle. A normal key keeps working on the installed version after expiry and only blocks newer releases. | confirmed |
| Acquisition, TTL, dongles free? | Yes: no licence check sits in device add, streaming or recording in `Acquisition.exe`; export is not gated either. TTL output used for feedback and stimulus trials needs "Feedback Pro" or "Sleep Deprivation" ("A feedback license is required to run stimulus trials"). No seat, per-PC or "already running" logic. | confirmed (skeptic round 2) |

### B. Video sync and TTL
| Question | What the files say | Tag |
|---|---|---|
| Can a licence give the wireless head unit TTL | No. The 8274/8474 class has no TTL members and its command table has no TTL command. Every TTL-capable class (8401, 8206-HR, 8480, 9085, Master Clock pod) has them. | confirmed |
| Minimum to record our Pi pulses on the EEG timeline | A separate TTL pod, no licence. The 9085 TTL Plus is created with its real class when plugged in and `Acquisition.exe` has no hide or deprecation filter, although changelog 3.0.0 lists "9085 I/O Monitor" as deprecated legacy. Each TTL edge becomes one annotation row in the experiment database, shown on the plot and exported to `*_annotations.tsv`. | confirmed, ask about support |
| TTL aligned by sample counter or arrival time | Arrival time. Every device builds its own sample times by counting samples, steered to one shared clock (the PC clock by default). There is no hardware counter shared between a TTL pod and a wireless unit. | confirmed path, see below |
| Master Clock pod | A "Master Clock" pod stamps its own TTL edges with hardware ticks (0.8 or 3.2 µs, 12.8 ms packets). Adding one makes it the global clock automatically, with no prompt, so the 8474 timeline is then steered to it, but 8474 samples are still placed by Bluetooth arrival. Not in the catalog we read: ask. | confirmed |
| 30 pulses per second for 72 h | No software rate limit: one row per edge, about 108,000 rows per hour, 7.8 million in 72 h. Only the pod's debounce (0 to 255 ms) and edge enables throttle it. One pulse per second is the safer design. | confirmed path, load inferred |
| Cameras per PC, third party cameras | Any Windows camera through Media Foundation (UVC webcams included); IP camera over HTTP MJPEG (changelog 3.3.0), where you enter an IP and Sirenia builds `http://<ip>/mjpeg?...` (no free URL field); a "gateway" option (default `http://127.0.0.1:18080`) that lists cameras from a `/api/v1/catalog` JSON. No RTSP, ONVIF or H.264. Up to 8 cameras, by licence. | confirmed |
| Frame timestamps | PC clock at the moment Sirenia processes the frame, minus a fixed 0.04 s. The camera's own timestamp is never read. Recording is MJPEG passthrough or VP8 inside the native file; export to WebM or AVI. | confirmed |

**Timing details (skeptic-checked).** The per-sample time is count x 1/rate, kept on the PC clock by a loop that tracks
the rate within about ±2 % and snaps only when it is more than max(8 samples, 1.0 s) off. A fixed offset of -0.188 s is
applied at 512 Hz. Losses the packet counter cannot count leave timestamps up to about 1 s early until the loop catches
up, with no NaN. An undocumented network "gateway" path also exists that times samples from the gateway's own nanosecond clock, shared
by everything on that gateway; it is not a product we know of.

**What this means for route B (our cameras + TTL Plus):** the pulse and the EEG sample share a timeline only through the
PC's arrival times, so the error is the difference in USB and Bluetooth latency between the two devices, plus up to about
1 s after a short dropout. That is worse than our wired design (pulse in the EEG file, frame N to sample S), and the
catalog's "within 100 ms" for Pinnacle video is the same kind of PC-clock alignment. A one-time measurement on the bench
would tell us the real jitter.

### C. Head unit (8474-HR-SE4-C)
| Question | What the files say | Tag |
|---|---|---|
| 8474 known | Changelog 3.1.2 "Added: 8474 support"; model strings `8474-SE4`, `8474-SE4R`, `8474HR_SE4R`, `8474-SE3A`, `8474-SE3M`, `8474-SE2D`, `8474-SEA`, `8474-SLA`; settings panel "8274/8474 Settings". The custom `-C` is not in the table; an unknown unit still gets four channels named EEG1 to EEG4. | confirmed |
| Input range | 14-bit, ±465.4 µV (about 0.057 µV per bit) on all four channels, EMG included, but only for units the software parses as HR. See next section. | confirmed constants |
| Rates and filters | 512 Hz is in the HR rate list {1, 128, 256, 512, 1024, 2000}. The 50/60 Hz notch and the low-pass are software filters applied before samples are stored: leave both off. No hardware high-pass or anti-alias corner is in the software. | confirmed |
| Connector drawing, battery | Not in the files. | not found |

#### Input range depends on the model string
Skeptic and hardware analyst agree on this (inferred from the disassembly, the parser read directly):
- Sirenia sets the HR mode (14-bit, ±465 µV) only when the model string the unit reports contains `HR` (or `M2`) with a
  digit right before it and `-` right after it. So `8474HR-SE4...` is HR. The strings `8474-HR-SE4-C`, `8474-SE4` and
  `8474HR_SE4R` do not match that test.
- A unit that is not parsed as HR gets 12-bit scaling (about ±480.8 µV). The 8474 model table is only reached inside the HR
  branch, so a non-HR 8474 (other than SE4R, which has its own handling) would get 3-channel framing with no 4th stream.
- Round 2: `Acquisition.exe` has no model override, no manual model choice and no way to force HR or four channels; the HR
  flag has a single writer, the parser. "Set Custom Gain" only rescales in software and cannot stop clipping.
- What is printed on the quote is not necessarily what the unit reports over Bluetooth, and Pinnacle presumably tests its
  own units in Sirenia. So this is not a fault, it is a question: **ask Pinnacle the exact model string the 8474-HR-SE4-C
  reports and confirm Sirenia 3.3.5 shows four 14-bit channels for it.** Check it again on the first unit we receive.

### D. PC and 16 dongles
| Question | What the files say | Tag |
|---|---|---|
| Dongles per head unit | One, in practice. The dongle firmware (0.4.1) has 4 connection slots and tags every frame with its slot; Sirenia reads the slot, adopts it on connect and ignores data from other slots, so it runs one head unit per dongle. Morelia ignores the slot bits. (Round 1 said "no unit id": wrong, corrected 2026-10-27.) | confirmed (skeptic round 3) |
| Units per PC / per instance | No cap on dongles or devices in the library or in `Acquisition.exe`; each device gets its own I/O thread. A negative static finding: only a 16-dongle test proves it. | not found (skeptic-checked) |
| Dongle USB identity | FTDI chip driven through D2XX, recognised by the description "BT5 Dongle" (Bluetooth 5), 921600 baud, 8N1, 2 ms latency timer, no VID/PID filter (every FTDI device is listed). A "Reprogram FTDI" tool knows 24 Pinnacle product IDs under FTDI's vendor ID 0x0403. No `.inf` or `.sys` driver ships. Probably a full speed FT232R class chip (weak). | confirmed, chip inferred |
| Hubs vs PCIe cards | Not in the code. `Diagnostic.exe` collects USB controller (XHCI, HUB3) and power management logs, a hint that USB disconnects and power saving are known failure modes. | inferred |
| Dropouts | Packets of 244 bytes with a 16-bit counter. Up to 20 counted lost packets are filled with NaN on the sample grid. Losses the counter cannot count (more than 20 packets, a big counter jump, a counter reset after reconnect) leave timestamps up to about 1 s early with no NaN until the clock loop catches up; bigger forward jumps are bridged with NaN up to a cap (about 1000 samples), then become a time jump. Reconnect retries every 1 to 4 s. | confirmed counts, thresholds inferred |
| System requirements | EULA lists Windows 7, 8, 10, 11. RAM, GPU and battery figures not found. | confirmed |
| Python API / Linux | Nothing in the installer; Pinnacle's separate Morelia API covers it, see [[#Round 3: Morelia API and firmware (2026-10-27)]]. A local UDP command port (127.5.5.5:65432) accepts only "Stop Recording" and "Exit Application" while recording; there is no annotate command (round 1 said there was: wrong). Live data can stream out as UDP multicast to 239.255.76.67:8866, one record per sample: stream name (26 characters), then seconds, fraction, value as text. The default "This computer only" setting suggests another PC needs a relay. | confirmed |

### Files
- Native `.pvfs`: one container file holding per-channel float32 sample files and an SQLite `experiment.db3` with
  metadata, annotations and scores. Times are stored as whole seconds plus a fraction. Lost data is NaN. Pinnacle's
  `pypvfs` package (see round 3) should read it on Linux; untested.
- EDF export is always `EDF+C` ("EDF+D" is not in the code); missing data is filled with a chosen value or interpolated;
  annotations and TTL go into an "EDF Annotations" channel. TSV export can leave gaps blank.
- `Sleep.exe` opens EDF files and imports scores from pvfs, edf, db3, txt, csv and tsv. Scoring a third-party EDF is
  plausible but not proven (power analysis is PVFS only per the changelog): test it in the trial.

## Round 3: Morelia API and firmware (2026-10-27)
Sources: Pinnacle's open-source Python API [Morelia](https://github.com/Pinnacle-Technology/Morelia) (BSD-3, released
v1.8.3 on 2026-10-02, cloned and read, nothing run) and the firmware Andrea downloaded from Pinnacle's site
(`8274_0_4_1`, `8274D_0_4_1`, `8401_V3_0_0`, `8401HS_1_0_9`, `m8206HR_SE3_1_0_3`, `m8206HR_SL_1_0_3`, in
`~/Downloads/Organized/Archives/`). The 8274/8274D images are Silicon Labs Gecko bootloader files for an EFR32 Bluetooth
chip, unsigned and unencrypted, version 0.4.1 (2022). They are the legacy 12-bit 3-channel 8274, **not 8474 firmware**,
so everything about the 8474 below is carried over from the 8274 by inference. The skeptic re-checked both reports.

| Topic | What Morelia and the firmware say | Tag |
|---|---|---|
| 8474 in Morelia | Released v1.8.3 supports the 8274-D dongle with legacy 3-channel units only. The unreleased `develop` branch ("8274HR WIP", merged 2026-10-08) decodes "8274HR/M2 and 8474HR/M2" with an allow-list of 8474 models (SE4, SE4R, SE3M, SE2D, SEA, SLA, SE3A). It still assumes 40 samples per packet in its timing code, where a 4-channel HR packet has 30. | confirmed |
| Scaling and packet | Morelia's HR decoder: 2-bit channel tag, signed 14-bit value, 2.42 V / 16384 / 2600 = ±465.4 µV, the same as Sirenia. Same 244-byte payload with the 16-bit counter. One difference: Sirenia flips the sign of channel 3 on non-8474 units; a 4-channel 8474 is not inverted by either. | confirmed |
| Model string | The head unit sends a Model Number read from a field written at the factory (default "8274"); the firmware cannot tell what an 8474-HR-SE4-C holds. Morelia `develop` accepts only exact names such as `8474HR-SE4`: it rejects `8474-HR-SE4-C` and even `8474HR-SE4-C` with a ConnectionError. Sirenia needs digit + `HR` + `-`. So the two programs agree only on the `8474HR-SE4...` form, and Morelia only on the exact listed names. In 0.4.1 the field holds 12 bytes, but both programs accept 13, so a fallback to "8274" is unlikely. | confirmed code, string unknown |
| Head-unit clock tick | Every packet carries the low 16 bits of the head unit's real-time clock (about 30.5 µs ticks, wraps every 2 s, latched once per packet). Neither Sirenia nor Morelia reads it. With the packet counter to unwrap it, our own decoder could use it to correct drift between units, with up to one sample period of jitter. Clock source not pinned; 8474 firmware unknown. | confirmed field, use plausible |
| Linux | Morelia talks to the dongle through pyserial on `/dev/ttyUSB*` at 921600 baud (D2XX never enabled for the 8274D). `install_ubuntu.sh` only installs Python, Qt/X11 libraries, libusb and libftdi; the udev rule only adds the dialout group, no stable per-dongle names. The docs warn that pre-2024 devices may need a firmware change for Linux, and that enabling the Windows VCP driver can break Sirenia access. | confirmed |
| Timestamps in Morelia | PC clock, counted per sample and steered at most ±2 % per update, up to 20 lost packets as NaN ("Sirenia-compatible"). No TTL or sync for wireless. | confirmed |
| 16 dongles | One process per dongle, no device cap; each worker scans with a fixed 15 s timeout. Examples go up to 3 devices. | confirmed |
| Reading `.pvfs` on Linux | Pinnacle's `pypvfs` 1.0.7 (BSD-3, Linux x86-64 wheels, 2026-10-15) documents opening `.pvfs` files and reading channels, `experiment.db3` and video. Docs only, untested. | confirmed from docs |
| Dropouts in firmware | Data goes as unacknowledged notifications; neither the head unit nor the dongle buffers a backlog (the dongle drops packets when more than 5 wait for the UART). Every loss shows as a counter gap. Radio: 1M, then 2M on request; no coded PHY. | confirmed (0.4.1) |
| TTL, battery | No TTL or GPIO event input and no battery reporting in the head-unit firmware. | confirmed (0.4.1) |
| Sample rate | Legacy rate = timer clock / 2^n; if that clock is the ~1 kHz RC oscillator, legacy "512 Hz" is really about 500 Hz. Both programs measure the real rate, so it only matters for our own decoder. | plausible, not proven |

**What this changes.** The model-string risk is now confirmed in two independent programs: ask for the exact string and
make sure it is `8474HR-SE4` (or another listed name), not something with `-C`. The unused head-unit clock tick is the
first route to timing that does not depend on PC arrival time, but only for our own Linux decoder, not inside Sirenia.

## New questions for Pinnacle (from this read)
> [!info] 2026-10-27: Pinnacle's reply to the 2026-10-26 email agrees with this read on PC timestamps, no RTSP and per-camera video licences, and adds a ±78 ms TTL alignment guideline. None of the questions below was asked in that email. [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]

1. What model string does the 8474-HR-SE4-C report, and does Sirenia apply the 14-bit ±465 µV HR scaling to it? What is
   the hardware gain on CH3 (pons LFP) and CH4 (EMG)?
2. Is the 9085 TTL Plus still supported and offered in Sirenia 3.3.5, given "9085 I/O Monitor" is listed as deprecated?
3. What is the Master Clock pod (part number, price), and does it improve TTL to wireless alignment beyond PC arrival time?
4. Is a Raspberry Pi serving MJPEG at `http://<ip>/mjpeg` supported as an IP camera (one Video Recording licence slot each)?
5. What is the "gateway" device with its own clock and camera catalog, and is it a product?
6. In Sirenia 3.3.5, "Sleep Analysis" and "Sleep Pro" unlock the same analysis features. Which one does the 9035 Sleep Pro
   part number deliver, and is there a lower priced "Sleep Analysis" licence?
7. Which USB driver and product ID does the BT5 dongle use, and which driver version do you recommend for 16 dongles?
8. (2026-10-27) What exact bytes does the 8474-HR-SE4-C store as its Model Number? Morelia `develop` accepts only names
   like `8474HR-SE4`; will the custom unit report one of those?
9. (2026-10-27) Each packet carries a 16-bit head-unit clock tick (bytes 14-15) that Sirenia and Morelia do not use. What
   clock drives it, how accurate is it, and does the 8474 firmware keep it?
10. (2026-10-27) Is a Morelia release with 4-channel 8474HR support planned, and can we get the 8474 firmware?
11. (2026-10-27) Does the 8474 report battery voltage anywhere?

## Still open
- [ ] Our Pi 5 cameras stream H.264 only (vault rule); Sirenia takes MJPEG only. Using them as Sirenia cameras needs an
      MJPEG stream, untested.
- [ ] Measure TTL Plus to 8474 jitter on the bench before trusting route B.
- [ ] File Pinnacle's written answers next to these and mark where they differ.
- [ ] Try `pypvfs` on a Sirenia `.pvfs` once we have one (trial or first recording).
- [ ] On the first unit: read Device Information > Model Number with a phone BLE scanner (read only) before connecting it to Sirenia.

Related: [[pinnacle-wireless-plan-status]] · [[2026-10-25-pinnacle-software-video-pc-questions-email]] ·
[[2026-10-16-pinnacle-wireless-16-mice-evaluation]] · [[_rig-expansion-hub]] · [[2026-10-26]]
