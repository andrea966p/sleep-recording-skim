---
type: reference
area: allego
status: active
created: 2026-10-28
summary: "Radiens 4 (Allego/Videre 4.1.2): what free Standard and paid Pro give an XDAQ EEG/EMG/LFP lab, what the installers really gate, the Python package change, and the reply to NeuroNexus about the Legacy-to-Pro gift"
tags: [allego, radiens, licence, vendor]
---

# Radiens 4: Standard vs Pro, our perpetual licence, and the reply to NeuroNexus

> [!abstract] TL;DR
> - Allego 4.1.2 and Videre 4.1.2 are free to download, but they need a Radiens ID sign-in. Every account starts on **Standard**.
> - Standard already covers what our rig uses: XDAQ control, impedance, recording and streaming, the live Monitor, live PSD, signal metrics, LFP band power and spectrogram, read/export, and the Python API.
> - Pro costs **$2,000 per year** (academic, Radiens Platform) and is a subscription. When it lapses, the software reverts to Standard.
> - Pro adds things we do not use (advanced spectral, PSTH, HD Snapshot, manual curation, NWB/FAIR metadata, study-level metrics). It also adds "headless" and "batch" pipelines, and that is the one ambiguous point for our unattended Python-driven recordings.
> - Curate no longer exists as an app. It is now a workflow inside Videre.
> - Our Python client `radiens` 4.0.0 belongs to Allego 3.x. Moving to Allego 4 means rewriting the console scripts against the new `radiens-core` (Python ≥ 3.12).
> - Nothing is installed: e10 still runs `allego 3.11.3-1218` and `curate 1.9.1-1192`. The `.deb` files were only unpacked and read.

## Sources

- Installers in `~/Downloads`: `allego_4.1.2_amd64.deb` and `videre_4.1.2_amd64.deb`, both version `4.1.2-1455`, built 2026-10-24. I unpacked them and read the protobufs, the bundled `allegoserver` binary and the Electron renderer bundle. Nothing was installed.
- https://radiens.ai/pricing, cross-checked by a second fetch on 2026-10-28. Also https://radiens.ai/resources/docs/radiens, https://radiens.ai/products/curate, https://radiens.ai/products/script and https://radiens.ai/terms (marked interim).
- Release notes at https://github.com/NeuroNexus/allego-v4-releases/releases and https://github.com/NeuroNexus/videre-v4-releases/releases.
- PyPI: https://pypi.org/pypi/radiens/json and https://pypi.org/pypi/radiens-core/json. radiens-core docs: https://neuronexus.github.io/radienspy/radiens-core/

## What our rig needs, by tier

> [!info] Legend
> 🟢 settled by the docs or the code · 🟡 uncertain · 🟠 to ask NeuroNexus · 🔴 not applicable to us

| Status | Our need | Tier | Evidence |
|---|---|---|---|
| 🟢 | XDAQ control (record mode) | Standard | Pricing page: "XDAQ control — 1,024+ channels". The installer gates the acquisition mode on the feature `instr.xdaq` (`XDAQ_CORE_REC` → `instr.xdaq`), and the server refuses with "Restart refused: not licensed for this instrument". So the account must actually carry `instr.xdaq`. |
| 🟢 | Impedance sweep | Standard | "In-workflow impedance measurement". Feature key `allego.impedance`. |
| 🟢 | Live Monitor, live PSD, signal-quality readout | Standard | Pricing page. |
| 🟢 | Python API (start/stop, status, impedance, signals) | Standard | "Free Python & API". RadiensPy is "free at every tier" (products/script). |
| 🟠 | Unattended, scripted 24-72 h runs | Standard or Pro? | Pro lists "Headless, scriptable command set" and "Batch & headless pipelines". No page defines "headless". |
| 🟡 | Simple filters vs filter chains | Standard / Pro | Multi-stage chains are Pro (`automation.dsp_chains`). Single IIR and preset filters look like Standard. |
| 🟢 | LFP band power, PSD, spectrogram (offline) | Standard | Pricing page, LFP section. |
| 🟢 | Read, manage and export recordings | Standard | "Read, manage & export". NWB export is listed as Standard on the Curate page but as "tier-gated" in the Videre notes, so the sources disagree. We export CSV anyway. |
| 🔴 | Spike sorting, PSTH, raster, manual curation, probe models, implant planning | Standard or Pro | We record no spikes. |
| 🔴 | HD Snapshot, journal figure export, FAIR metadata, study-level metrics | Pro | Not used. |
| 🟠 | Gen-1 XDAQ Core on Allego 4 and Ubuntu 24.04 | ? | The 4.1.x notes fix several XDAQ bugs and require new firmware for Gen2. Gen1 is not named. System requirements list Ubuntu up to 22.04. |
| 🟠 | Offline or unattended licence on the rig | ? | The installer has an offline-licence path tied to a hardware UUID (`GetOfflineLicenseStatus`, "Successfully verified offline installation"). The docs do not describe it. |
| 🟠 | `.xdat` compatibility from 3.x to 4.x | ? | No release note mentions a format change. Videre 4 still opens XDAT. |

## What the installers show

- **One backend for everything.** `resources/radix/bin/` ships the `allego`, `curate` and `radiens` command-line binaries. `allegoserver/` bundles `libxdaq_device.so` and the Intan/Opal Kelly bitfiles, so the XDAQ driver is still included.
- **The gating is server-side and per account.**
  - At sign-in the GUI fetches a list of `features`, plus `metered_features` with a quota and the amount used, from `/user/{id}`.
  - Every tab and sub-feature is checked against that list. Examples: `allego.impedance`, `allego.signal_metrics`, `signal_metrics.advanced`, `signal_processing.chains`, `monitor.live_tail` and `curate.*`.
  - Which plan grants which key is not in the installer. Only NeuroNexus can say what "Legacy" maps to.
- **In-app purchase.**
  - The upgrade dialog loads `/plans`, and `/subscribe` takes a plan `lookup_key`.
  - The dialog says changing tiers "is prorated and keeps your renewal date", so Pro is a renewing subscription. The release notes also mention a "Pro+" tier that is on no public page.
  - Seats: a lab admin "can invite a lab member to fill an open seat on your license", and each member signs in with their own email.
- **Telemetry.** Usage analytics are tied to the licence info (user id, email, organisation). Detailed analytics are opt-in, with a consent toggle.
- **Cloud analytics.** `analytics.proto` streams LFP matrices to a cloud service (specparam/FOOOF, buzcode ripple and theta), with a "free-tier budget". This is not needed. 🛑 Do not send rig data to it without Andrea's decision.
- **Old enum unchanged.** The low-level `FeatureLicense` enum (`Feat_RadixAPI`, `Feat_Impedance`, …) is identical in 3.11.3 and 4.1.2.

## Python packages

- **`radiens` 4.0.1 (2026-10-06)**
  - Marked deprecated in favour of `radiens-core`.
  - The client code is byte-identical to 4.0.0.
  - The wheel is missing the gRPC stubs, so a fresh import would likely fail. 🛑 Do not install it.
  - 4.0.0 declares compatibility with Allego 3.10.12, Videre 1.9.0 and Curate 1.9.0.
- **`radiens-core` 0.1.2 (2026-10-23)**
  - The new client. It is MIT-licensed, pre-1.0, needs Python ≥ 3.12, and has a typed pydantic API.
  - It adds `start_recording(*, port=None)` and `stop_recording(*, port=None)`, plus `update_recording_config()` with `split_files_by_port`. These could fix the "recording is global" gap in [[radiens-api-reference]], but that is untested.
  - It also adds a working `restart(*, mode)`, which fails if the account is not licensed for that mode.
  - No tier checks were found in the client except the mode licence. Newer features raise `CapabilityError` on older servers.
- **Upgrade path, if ever chosen.** Install Allego 4 and `radiens-core` in a separate venv. Bench-test with no recording running, then port the console scripts. This is a project, not a patch.

## The NeuroNexus thread

- NeuroNexus (Rosaria) offered Radiens Legacy users the Pro tier "at no additional cost". She asked whether `andrea96p@kaist.ac.kr` is the address tied to our current Radiens subscription.
- The pricing FAQ says: "Perpetual licenses are no longer sold, and every one already sold is honored."
- Pro is otherwise $2,000 per year, so whether the gift is perpetual or one year matters.

### Draft reply for Andrea to review (not sent)

Rules for this draft: no dashes in emails, Andrea's voice.

> Subject: Re: Radiens Legacy licence and the Pro tier
>
> Dear Rosaria,
>
> Thank you for your reply and for the kind offer. Yes, andrea96p@kaist.ac.kr is the address linked to our Radiens licence.
>
> I am the PhD student who set up the XDAQ in our laboratory. On top of Allego I built our own recording console (scheduling recordings, run series, signal metrics and impedance sweeps through the Python API) and synchronised video acquisition with Raspberry Pi cameras. We record only EEG, EMG and LFP for sleep studies in mice, on a custom tethered system with Intan bipolar headstages and a Gen 1 XDAQ Core, usually 24 to 72 hours unattended.
>
> Before I bring this to our professor, I would like to clarify a few points:
>
> 1. Is the Pro tier you are offering permanent, like our current perpetual licence, or is it limited in time? If it is limited, how long does it last, and what happens at the end of that period?
> 2. If we accept the Pro upgrade, does our perpetual licence stay valid? We would like to be sure we never lose rights we already paid for.
> 3. In the new model, which tier does our perpetual licence (Allego and Curate) correspond to: Standard, Pro or Pro+? If it does not go beyond the free Standard tier, would a refund or a credit for the perpetual licence be possible, so that we simply continue on the free tier with our XDAQ?
> 4. Our recordings run unattended and are started and stopped by our own Python scripts. Does that count as the "headless" or "batch" use listed under Pro, or is it covered by the free Python and API access in Standard?
> 5. How many seats or named users does the licence include? Our rig PC is shared by several lab members, and it sometimes runs without internet access. Is offline use on that PC supported?
> 6. Are Allego 4.1 and the new Python package (radiens_core) supported on a Gen 1 XDAQ Core and on Ubuntu 24.04, and are our existing .xdat recordings fully compatible?
>
> Thank you again for your help. I look forward to your answer.
>
> Best regards,
> Andrea Piazzola

## Still open

- [ ] Andrea: review and send the reply above; record Rosaria's answer here.
- [ ] Decide whether to move the rig to Allego 4 at all. The alternative in [[openephys-gui-setup-xdaq-sleep-eeg]] still stands. 🛑 No install on e10 during a recording.

> [!info] 2026-10-28, later the same day: the "untested" and "cannot talk to it until ported" statements below were overtaken. Per-port recording was bench-tested and works ([[2026-10-28-per-port-recording-bench-test]]), `radiens-core` was installed into `/opt/neurosurveillance/venv` next to `radiens` 4.0.0 (the two cannot be imported together; no code imports the old one), and the console was ported but is not restarted in production yet ([[2026-10-28-per-port-console-port]]). A fresh launch later came up at 30000 Hz with the split off ([[2026-10-28-allegoserver-death-and-fresh-launch-defaults]]).

## Install on e10 (2026-10-28)

- Before the install, the rig was idle (`R_OFF`, `S_OFF`, no active run). The 3.11.3 installer no longer exists, so I archived `/opt/allego`, `/opt/curate` and the configs in `~/allego-3.11.3-rollback/` (1.5 GB) as the only way back.
- Andrea installed `allego` and `videre` `4.1.2-1455` with sudo and held them with `apt-mark hold`. `curate` 1.9.1 is still installed.
- `radiens-core` 0.1.2 is in a separate venv, `~/radiens-core-venv`, on the system Python 3.12.3. The production venv still has `radiens` 4.0.0.
- API check after sign-in, through `radiens-core`:
  - The server reports version `(5, 8, 0)`.
  - Mode is `XDAQ_CORE_REC`, so the account is licensed for XDAQ.
  - Ports A to D show 32 channels each.
  - The measured stream rate is 1.003x wall clock.
  - Recording config: `split_files_by_port=False`, base path `~/radix/data`.
- Fresh-launch defaults are wrong for us. The base sample rate came up at **625 Hz**, not 1000 Hz. Set the rate and channel selection before any recording.
- The EEG console now fails with `RpcException: Invalid authentication. Error code: 16`, because `radiens` 4.0.0 cannot authenticate to Allego 4. It has to be ported to `radiens-core`; this was deferred by Andrea.
