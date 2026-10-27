---
type: reference
area: rig-expansion
status: done
created: 2026-10-25
summary: "Email draft for the professor to send to Pinnacle: Sirenia free vs paid modules, video sync and TTL Plus, Sleep Pro, the custom 8474-HR-SE4-C head unit, and the one-PC plan for 16 dongles."
tags: [pinnacle, wireless, vendor, email, video-sync, ttl, pc]
---
# Pinnacle: software, video sync, TTL and PC questions (email draft, 2026-10-25)

> [!abstract] TL;DR
> - From Claude Code, 2026-10-25: I read Pinnacle's 2026 catalog (pp. 10, 25, 29, 30), the Sirenia page and the store
>   before writing this. There is no "standard vs pro" Sirenia. There is one **free Sirenia Acquisition** plus paid modules
>   bought one by one: **Synchronized Video (9021)**, **Sleep Pro (9035)**, Seizure Pro, Feedback Pro, X-Y Tracking.
> - **No software module gives the wireless head unit a TTL input or output.** External pulses enter Sirenia through a
>   separate USB box, the **TTL Plus (9085-N)**, which the catalog says works "for wireless or tethered systems".
>   "TTL functionality" is listed under the FREE acquisition package. So on paper: our own cameras + Pi pulses + TTL Plus
>   needs no video licence. What the catalog does NOT say is how well a TTL Plus event lines up with Bluetooth samples. That
>   is the key question in the email.
> - Pinnacle's own video: max **4 cameras per PC**, 640 x 480, 30 fps, frame timestamps, "within 100 ms" / "± one video
>   frame". 16 mice with Pinnacle cameras = several PCs or several cages per camera.
> - **Sleep Pro** = cluster + threshold auto scoring, hypnograms, spectra, bout analysis. Free Sleep Basic = manual scoring
>   and video playback. 30-day free trial exists: ask for it before paying.
> - The email (below) is written for the professor to send to sales@pinnaclet.com. No dashes in the body except inside
>   part numbers. Delete any question the 8474-HR-SE4-C quote already answers.

## What Pinnacle publishes (read 2026-10-25)

| Item | Part, US list price | What it does | Source |
|---|---|---|---|
| Sirenia Acquisition | free, any number of PCs | records all Pinnacle hardware, schedule recording, export, "TTL functionality"; includes Sleep Basic (manual scoring, "playback of EEG/EMG data with synchronized video") | catalog p.29, [Sirenia page](https://www.pinnaclet.com/sirenia.html) |
| Synchronized Video | 9021, price not on the store | unlocks video recording synced to EEG/EMG by frame-by-frame timestamping, "± one video frame, up to 30 frames per second", "within 100 milliseconds"; up to 4 cameras per video system | catalog p.25, p.29 |
| USB camera kit | 9000-K30, $1,387.38 | 640 x 480, 30 fps, IR, USB; "includes … one Sirenia® license key" (which licence: ask) | catalog p.25, store |
| TTL Plus | 9085-N(-K), from $411.02 | 4 I/O, 5 V digital in/out or 10-bit analog up to 2000 Hz, "TTL signal integration for wireless or tethered systems" | catalog p.25, store |
| Sleep Pro | 9035-K-E, $2,362.50 | cluster + threshold + manual scoring, hypnograms, spectral plots, bout analysis, imports third-party EDF | catalog p.30, store |
| Licensing of paid modules | | "installed on multiple computers but limited to one computer running the program at a time", one year of free upgrades, 30-day trial via sales@pinnaclet.com | catalog p.29-30 |
| Python API | free | "Compatible with Windows, IOS, and Linux" | catalog p.31 |
| 4-channel wireless battery | | 256 Hz 6 d, 512 Hz 5 d, 1024 Hz 3 d, 2000 Hz 1 d; "can vary based on Bluetooth® environment" | catalog p.10 |

Prices are the US store on 2026-10-25; the Korean price comes through the quote.

## The three video routes (my reading, to confirm with Pinnacle)

| Route | Buy | Pros | Unknown |
|---|---|---|---|
| A. Pinnacle cameras in Sirenia | Synchronized Video licence(s) + 9000-K30 cameras | turnkey, video and EEG in one file viewer, Sleep Basic plays it back | 4 cameras per PC; software timestamps only; 640 x 480 |
| B. Our cameras + TTL Plus | TTL Plus (~$411), no video licence | keeps our Pi camera system, pulse per frame lands in the Sirenia file | how TTL Plus events align with Bluetooth samples; max pulse rate over 72 h |
| C. Our own Linux recorder via the Python API | nothing | no Windows, our own sync | we lose Sirenia; timestamps and gap handling are ours to build |

Route B is the one closest to our sync design (pulse into the EEG file, frame N to sample S), but it is only as good as
Sirenia's alignment of two USB devices. Questions 5 to 9 are there to find that out.

---

## Email draft

**To:** sales@pinnaclet.com (cc VIVO Solutions, info@vivosolutions.co.kr, if the order goes through them)

**Subject:** Custom 8474-HR-SE4-C for 16 mice: software, video synchronization, TTL and PC questions before ordering

> Dear Pinnacle team,
>
> I am the principal investigator of the SKIM sleep lab at KAIST (Daejeon, Korea). We are preparing to order the custom
> four channel wireless head unit 8474-HR-SE4-C for mouse sleep studies: 12 units before the end of 2026 and 4 more in
> January 2027, so 16 mice recording at the same time. Each mouse carries two cortical EEG channels, a bipolar LFP pair in
> the pons (about 4.5 mm deep) and nuchal EMG, and recordings last 48 to 72 hours. Before we finalize the order, could you
> please answer the questions below in writing? Short answers are perfectly fine.
>
> **A. Software packages**
>
> 1. From your 2026 catalog we understand that the free Sirenia Acquisition records all 16 head units, includes Sleep
>    Basic for manual scoring and has TTL functionality, and that Synchronized Video (9021) and Sleep Pro (9035) are paid
>    modules. Is this correct? Is there any other paid module that matters for wireless sleep recordings?
> 2. What exactly does the Synchronized Video licence add to the free software? Is it licensed per PC, per camera or per
>    running instance? The 9000-K30 camera kit includes "one Sirenia license key": is that a Synchronized Video licence?
> 3. Sleep Pro: has the cluster and threshold scoring been validated on mouse data from the wireless units at 512 Hz?
>    Can the licence run on a separate analysis PC while the acquisition PC keeps recording? Could we have the 30 day
>    trial before we decide?
> 4. Can Sirenia export each head unit to EDF with the gaps marked, so we can also score in our own software?
>
> **B. Video synchronization and TTL**
>
> We already have our own video system (Raspberry Pi cameras, 30 frames per second), and each camera can send a TTL pulse
> for every captured frame or once per second. We would like to keep using it. Since the wireless head unit has no TTL
> input, we want to understand what is technically required to record these pulses in the same timeline as the EEG:
> can we do it with the free Sirenia Acquisition alone, does it need a TTL Plus (9085-N), and does it need the
> Synchronized Video licence or any other paid module? Please tell us the minimum that is strictly necessary.
>
> 5. Does any software licence (for example Synchronized Video) let the wireless head units send or receive a TTL pulse,
>    or is the TTL Plus always needed to bring an external pulse into the recording?
> 6. With one TTL Plus and 16 wireless units on the same PC: are TTL events placed on the same timeline as each head
>    unit's samples? Is that alignment based on the head unit's sample counter or on the time the data arrive at the PC?
>    What accuracy should we expect over 72 hours, and how far do the head units drift from each other?
> 7. Does the TTL Plus work with the free Sirenia Acquisition alone? How many TTL Plus units can one PC run, and can an
>    input log 30 pulses per second continuously for 72 hours?
> 8. Synchronized Video supports up to four cameras per PC. For 16 mice, would that mean four PCs, or can one camera
>    cover several cages? Does the licence accept third party USB (UVC) or network (RTSP) cameras, or only the 9000-K30?
> 9. The catalog gives a video synchronization of "within 100 milliseconds" and "plus or minus one frame". Was this
>    measured with wireless units, given the Bluetooth latency?
>
> **C. Head unit and headmount (8474-HR-SE4-C)**
>
> 10. Please confirm the channel layout: CH1 is EEG1 against COMMON, CH2 is EEG2 against COMMON, CH3 and CH4 are fully
>     independent differential pairs, plus one GROUND, 8 pins in total.
> 11. Is the input range plus or minus 465 µV on all four channels (the catalog prints mV)? Is a wider range possible on
>     CH3, which carries the pons LFP?
> 12. Can the EEG high pass filter be set to 0.5 Hz, or even 0.1 Hz? What is the anti aliasing low pass corner at 512 Hz
>     and at 1024 Hz?
> 13. We will design our own headmount circuit board, which must fit within 6 mm on the mouse skull. Could you send the
>     mechanical drawing of the head unit connector (part number, pitch, male or female, outline, pin 1, and which pins are
>     COMMON and GROUND)?
> 14. The catalog gives 5 days of battery at 512 Hz for the four channel unit. Does that hold with 16 units in one room?
>     Do you recommend the 8276 supplemental battery for 72 hour runs?
> 15. During a radio dropout, does the head unit buffer and resend the data, or is that segment lost? How are gaps shown
>     in the recording and in the EDF export?
>
> **D. Acquisition PC and connecting 16 head units**
>
> Our plan is one Windows 11 PC that we build ourselves: AMD Ryzen 5 class processor, DDR4 memory, an ASUS PRIME B550
> PLUS board, a single slot graphics card with 2 GB of memory, no onboard WiFi or Bluetooth, and a UPS. The 16 dongles
> connect as follows: 4 on the rear USB ports and 3 PCIe x1 USB cards with 4 dongles each, so no more than 4 dongles share
> one USB controller, and every dongle sits on its own 9052 extension cable to keep the radios apart. If 16 units on one PC
> are not stable, we will move 8 of them to a second identical PC. We plan to test the first 12 units for 72 hours in
> December before adding the last 4.
>
> 16. Are 16 head units on one PC and one Sirenia instance supported? What is the largest number you or your customers
>     run on one PC?
> 17. Does each dongle serve exactly one head unit, or can one dongle serve several?
> 18. Do you recommend PCIe USB cards like ours, or powered hubs such as your 9005? If hubs: how many ports does the 9005
>     have, is it a USB 2.0 multi TT hub, and how many dongles per hub do you advise? Is the dongle a full speed or a high
>     speed USB device?
> 19. What minimum distance between dongles, and what maximum distance from dongle to cage, do you recommend? Our cages
>     may sit in a metal rack: will that block the signal, and do you have a recommended cage or lid for wireless units?
> 20. Which PC settings do you recommend for 72 hour runs (USB power saving, Windows Update, power plan)? If we add video,
>     should the cameras run on a separate PC?
> 21. Is your Python API (Morelia) supported on Linux for the 8474 head units and the dongles?
>
> **E. Quote**
>
> 22. Please quote 16 units of 8474-HR-SE4-C (12 now and 4 in January), the matching accessory kits (and tell us how many
>     come with the head units), one TTL Plus, and as options the Synchronized Video licence and Sleep Pro, with delivery
>     to KAIST, lead time, warranty and the expected lifetime of a head unit. We would also be grateful for the user manual
>     and the surgery guide.
>
> Thank you very much for your help.
>
> Best regards,
> [name, title]
> SKIM sleep lab, KAIST

## Sent version, 2026-10-26

> [!success] 2026-10-26: Andrea sent a shortened version (text below, as given by Andrea; sender name left blank in
> the copy). The draft above is kept for the record. Recipient and cc not recorded. Answers go in
> [[pinnacle-wireless-plan-status]].

Not asked in the sent version (ask later if still needed): EDF export with gaps marked (draft Q4), whether the
"within 100 ms" video sync was measured with wireless units (Q9), EEG high-pass 0.5 / 0.1 Hz and anti-alias corner (Q12),
data buffering during radio dropouts and how gaps show (Q15), metal rack / wireless cage, PC settings, video on a separate
PC (Q19-20), and the formal quote with lead time and warranty, manual and surgery guide (Q22).

> Dear Pinnacle team,
> I am [...........] at KAIST (Daejeon, Korea). We are preparing to order the custom four channel wireless head unit 8474-HR-SE4-C for mouse sleep studies: 12 units before the end of 2026 and 4 more in January 2027, so 16 mice recording at the same time.
> Before we finalize the order, could you please answer the questions below in writing? Short answers are perfectly fine.
>
> **A. Software packages**
> From your 2026 catalog we understand that the free Sirenia Acquisition records all 16 head units, includes Sleep Basic for manual scoring and has TTL functionality, and that Synchronized Video (9021) and Sleep Pro (9035) are paid modules.
> - What exactly does the Synchronized Video license add to the free software? Is it licensed per PC, per camera or per running instance? The 9000-K30 camera kit includes "one Sirenia license key": is that a Synchronized Video license?
> - Sleep Pro: has the cluster and threshold scoring been validated on mouse data from the wireless units at 512 Hz? Can the license run on a separate analysis PC while the acquisition PC keeps recording? Could we have the 30 day trial before we decide?
>
> **B. Video synchronization and TTL**
> We already have our own video system (Raspberry Pi cameras, 30 frames per second), and each camera can send a TTL pulse for every captured frame or once per second. We would like to keep using it. Since the wireless head unit has no TTL input, we want to understand what is technically required to record these pulses in the same timeline as the EEG: can we do it with the free Sirenia Acquisition alone, does it need a TTL Plus (9085-N), and does it need the Synchronized Video license or any other paid module? Please tell us the minimum that is strictly necessary.
> - Does any software license (for example Synchronized Video) let the wireless head units send or receive a TTL pulse, or is the TTL Plus always needed to bring an external pulse into the recording?
> - With one TTL Plus and 16 wireless units on the same PC: are TTL events placed on the same timeline as each head unit's samples? Is that alignment based on the head unit's sample counter or on the time the data arrive at the PC? What accuracy should we expect over 72 hours, and how far do the head units drift from each other?
> - How many TTL Plus units can one PC run (in cause TTL units are needed), and can an input log 30 pulses per second continuously for 72 hours?
> - Synchronized Video supports up to four cameras per PC. For 16 mice, would that mean four PCs. Does the license accept third party USB (UVC) or network (RTSP) cameras, or only the 9000-K30?
>
> **C. Head unit and headmount (8474-HR-SE4-C)**
> Please confirm the channel layout: CH1 is EEG1 against COMMON, CH2 is EEG2 against COMMON, CH3 and CH4 are fully independent differential pairs, plus one GROUND, 8 pins in total.
> Is the input range plus or minus 465 µV on all four channels (the catalog prints mV)? Is a wider range possible on CH3 (which will be used for LFP)?
> We are planning to use our own custom headmount circuit board. Could you send the mechanical drawing of the head unit connector (part number, pitch,, outline, pin 1, and which pins are COMMON and GROUND)?
> The catalog gives 5 days of battery at 512 Hz for the four channel unit. Does that hold with 16 units in one room? Do you recommend the 8276 supplemental battery for 72 hour runs?
>
> **D. Acquisition PC and connecting 16 head units**
> Our plan is one Windows 11 PC that we build ourselves: AMD Ryzen 5 class processor, DDR4 memory, an ASUS PRIME B550 PLUS board, a single slot graphics card with 2 GB of memory, no onboard WiFi or Bluetooth. The 16 dongles connect as follows: 4 on the rear USB ports and 3 PCIe x1 USB cards with 4 dongles each, so no more than 4 dongles share one USB controller, and every dongle sits on its own 9052 extension cable to keep the radios apart. If 16 units on one PC are not stable, we will move 8 of them to a second identical PC. We plan to test the first 12 units for 72 hours in December before adding the last 4.
> - Are 16 head units on one PC and one Sirenia instance supported? What is the largest number you or your customers run on one PC?
> - Does each dongle serve exactly one head unit, or can one dongle serve several?
> - Do you recommend PCIe USB cards like ours, or powered hubs such as your 9005? If hubs: how many ports does the 9005 have, is it a USB 2.0 multi TT hub, and how many dongles per hub do you advise? Is the dongle a full speed or a high speed USB device?
> - What minimum distance between dongles, and what maximum distance from dongle to cage, do you recommend?
> - Is your Python API (Morelia) supported on Linux for the 8474 head units and the dongles?

## Before sending (Andrea)
- [ ] Check against the 8474-HR-SE4-C quote: delete questions it already answers (model code, accessory kits, price).
- [ ] Check whether the 2026-10-16 email ([[2026-10-16-pinnacle-wireless-16-mice-evaluation]] §9) was ever sent.
  Questions 10 to 15 and 21 overlap with it.
- [ ] Graphics card: the PC plan says GT 1030 2 GB, Sirenia asks for 1 GB VRAM. Fine for EEG; check again if video goes on this PC.
- [x] File Pinnacle's answers in [[pinnacle-wireless-plan-status]] and the rig-expansion hub. 2026-10-27: [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]

Related: [[pinnacle-wireless-plan-status]] · [[2026-10-20]] · [[2026-10-23]] · [[_rig-expansion-hub]]
