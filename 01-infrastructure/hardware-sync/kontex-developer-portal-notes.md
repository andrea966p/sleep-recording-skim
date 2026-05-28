---
tags: [infrastructure, hardware-sync, reference, kontex, libxdaq, driver, thunderbolt]
created: 2026-05-28T00:00:00.000Z
status: complete
source: https://developer.kontex.io/libxdaq-docs/index.html
---

# Kontex Developer Portal — XDAQ Core2 Notes (libxdaq + pylibxdaq + Linux)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A digest of the public Kontex developer-portal documentation (`developer.kontex.io/libxdaq-docs/`) and the related GitHub repos under `github.com/kontex-neuro`, captured 2026-05-28. It records the facts that change how we install and verify the XDAQ Core2 on the Ubuntu acquisition host.
>
> **Why it exists.** The vendor email chain ([[neuronexus-inquiry-email|inquiry & replies]]) closed the wiring questions but punted the Linux/driver questions to Kontex. The developer portal answers most of the device-level questions directly. This note captures them so [[xdaq-core2-manual-reference|the manual reference]] stays focused on the DB25 pinout while host-side software/driver context lives here.
>
> **How to read this page.** The first section is the headline: Core2 is **Thunderbolt-only** — that determines the Ubuntu setup. Then libxdaq architecture (what `thor` vs `ok` device managers are), the pylibxdaq Python smoke test we can run to confirm the Core2 enumerates without launching Allego, and finally a list of sibling Kontex projects that are *not* part of our pipeline but exist as fallbacks. See [[overview|Hardware Sync Overview]] for the big picture.

> [!quote] Paper-ready
> Host-side connectivity to the XDAQ Core2 is provided by KonteX's libxdaq library (C++23, distributed via the Conan package manager), which exposes the Core2's Thunderbolt interface through its `thor` device-manager plugin. Thunderbolt connectivity is reported by the manufacturer at <0.5 ms latency and on the order of GB/s throughput, supporting host-side recording-state polling at sub-millisecond precision.

---

## 1. Core2 = Thunderbolt-only (headline)

From the libxdaq Introduction page:

| XDAQ Model | Interface |
|------------|-----------|
| Core | Opal Kelly USB |
| One | Opal Kelly USB |
| **Core Gen 2** (= our Core2) | **Thunderbolt** |
| One Gen 2 | Thunderbolt |
| All In One | Thunderbolt |

> "The USB interface is powered by Opal Kelly's FrontPanel API, while the Thunderbolt interface is handled by our custom solution." — *libxdaq Introduction*

**Implications for our Ubuntu 24.04 host:**

- **No Opal Kelly USB drivers needed for Core2.** The `60-opalkelly.rules` udev file shipped with Intan-RHX is only for the USB models (Core Gen 1, One Gen 1). Do not install it for Core2.
- **The Core2 driver is the standard Linux `thunderbolt` kernel module + `boltd` authorization daemon.** Connect the cable, then authorize the device:
  ```bash
  boltctl list                    # find the Core2's UUID
  sudo boltctl enroll <uuid>      # authorize permanently
  ```
  Confirm authorized status with `boltctl list` (look for `authorized: yes`).
- **Allego/Radiens must then see the device** through libxdaq's `thor` manager (`libthor_device_manager.so`). What's still unclear: does Allego require any extra steps (group membership, `udev` rules for the Thunderbolt char devices, headless boltd setup) — this is the open question we routed to **KC Kong (`KC@kontex.io`)** in the [[neuronexus-inquiry-email#New inquiry — KC Kong @ Kontex (draft 2026-05-28)|round-3 email]].

Throughput / latency (per `kontex.io/xdaq` product page): "**measured transfer speed on the order of GB/s and latency <0.5 ms**" — citable for paper methods.

---

## 2. libxdaq architecture

`libxdaq` is the C++ library every Kontex-side tool (Allego, XDAQ-RHX, XDAQ-OE, ThorVision, pylibxdaq) sits on top of. C++23, distributed as Conan packages, dynamically loads `.so` device-manager plugins.

**Tested Linux toolchain** (libxdaq-dist README): **Ubuntu 24.04 + GCC 14.2.0**. Our host matches.

**Device managers** (one shared library per interface family):

| Manager Name | Interface | Linux File |
|--------------|-----------|------------|
| `ok` | Opal Kelly USB (Core, One) | `libok_device_manager.so` |
| **`thor`** | **Thunderbolt (Core2, One Gen2, AIO)** | **`libthor_device_manager.so`** |

**Distribution.** Not on Conan Center — use the Kontex local Conan index:

```bash
# One-time setup
pip install --user conan
conan profile detect
git clone https://github.com/kontex-neuro/kontex-conan.git
conan remote add --force kontex-neuro ./kontex-conan
```

Then reference in a `conanfile.txt`:

```ini
[requires]
libxdaq/0.5.2
```

Packages in the index: `libxdaq`, `libxdaqnp` (Neuropixels), `libxvc` (ThorVision), `xdaqmetadata`.

**C++ API shape (`xdaq::` namespace).** Register-level — no named `DAQ_ON` / `DI 03` symbols; those mappings live in Allego/Radiens. Core surface (see [[https://developer.kontex.io/libxdaq-docs/device.html|libxdaq Device API]]):

- `set_register(addr, value, mask)` / `set_register_sync(...)` / `send_registers()`
- `get_register(addr)` / `get_register_sync(addr)` / `read_registers()`
- `trigger(addr, bit)` — fire a one-shot bit in a register
- `write(addr, length, data)` / `read(addr, length, data)`
- `start_read_stream(addr, on_receive, chunk_size)` — async DataStream w/ callback
- `get_status()` / `get_info()` → JSON

**Device Manager (`xdaq::DeviceManager`)** loaded with `xdaq::get_device_manager(path)`. Provides `list_devices()` (JSON), `get_device_options()` (JSON schema), `create_device(config_json)`.

> [!info] What this does NOT give us
> Register addresses for `DAQ_ON`, `DO 03`, `DI 03` etc. are **not in the libxdaq docs** — those are owned by the Allego/Radiens firmware layer. Practical implication: **libxdaq is not a path to bypass Allego for the recording-gate read**. Use it for device-presence smoke tests and as a backup acquisition layer, not as a `radiens_poller.py` replacement.

---

## 3. pylibxdaq — Python smoke test for Ubuntu setup

`pylibxdaq` (GitHub: `kontex-neuro/pylibxdaq`, master branch) is the Python binding for libxdaq. Useful to us as a **device-detection smoke test** — confirms Thunderbolt + `thor` manager work end-to-end without launching Allego.

> [!example] One-liner verification once libxdaq is installed
> ```bash
> python -c "from pylibxdaq.device import list_devices; \
>            [print(d.serial_number, d.api_version, d.info) for d in list_devices()]"
> ```
> Expected: the Core2's serial number + API version + an `info` dict. Empty list = Thunderbolt authorization or `thor` manager not loadable; check `boltctl list` and that `libthor_device_manager.so` is on the manager search path.

Full Python API mirrors the C++ one — `manager.create_device(json.dumps({"id": 0}))` → `device.set_register(addr, val)`, `device.trigger(addr, bit)`, `device.start_read_stream(addr, cb)`, `device.get_status()`. See `tests/test_device_api.py` and `tests/test_scan_devices.py` in the repo for canonical usage.

`DeviceInfo.with_mode("rhd").create()` switches a discovered device into a recording mode before opening — relevant only if we ever drive the Core2 outside Allego.

---

## 4. Sibling Kontex projects — fallbacks, not the pipeline

Documented here so they're discoverable, **not** changes to our stack.

| Project | What it is | Relevance to us |
|---------|------------|-----------------|
| **XDAQ-RHX** (`kontex-neuro/Intan-RHX`) | Kontex fork of Intan RHX recording GUI w/ XDAQ support | Jeffrey noted `DAQ_ON` behaves cleanly in **XDAQ-RHX** but emits ~0.5 s idle pulses in **Allego** when streaming is off. RHX is a possible diagnostic GUI if Allego's "Gated" mode misbehaves. Linux binary in releases. |
| **ThorVision** + `libxvc` + `xdaqmetadata` | Kontex's own video-acquisition stack with built-in XDAQ metadata sync | Alternative to our Frigate + go2rtc pipeline. Not pursued — Frigate stack is instrumented + stable. Worth knowing about if hardware sync hits an architectural wall. |
| **XDAQ-OE** (`kontex-neuro/XDAQ-OE`) | OpenEphys plugin (Intan headstages over XDAQ) | Not relevant — we are not on OpenEphys. |
| **XDAQ-Neuropixels** (`kontex-neuro/XDAQ-Neuropixels`) | OpenEphys plugin for Neuropixels via XDAQ | Not relevant — we don't run Neuropixels. |

---

## 5. Still open — for KC Kong

Reasons to wait for Kontex's reply rather than acting on the above:

- Whether **Allego on Ubuntu 24.04** has any extra requirement beyond standard `boltd` enrollment (group, polkit rule, headless workflow).
- Confirmed kernel range for the `thunderbolt` module + boltd version pairing Kontex tests against.
- Whether `libthor_device_manager.so` is bundled with the Allego installer or must be pulled from `kontex-conan` separately.
- Whether **DB25 `DO 03` (pin 22) "Gated" mode** is documented in any developer-portal page (we found it via Jeffrey, not via the public docs).

These are part of the [[neuronexus-inquiry-email#New inquiry — KC Kong @ Kontex (draft 2026-05-28)|round-3 inquiry to KC Kong]] — sent 2026-05-28.

---

## Related

- [[overview|Hardware Sync Overview]]
- [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]] — DB25 pinout / electrical specs (manual)
- [[neuronexus-inquiry-email|NeuroNexus / Kontex inquiry chain]] — Jeffrey rounds 1+2, Andrea round-3 to Jeffrey + KC Kong
- [[wiring-guide|Wiring Guide]]
- [[references-and-justification|Design Justification & References]]
- [[gpio-sync-service|GPIO Sync Service]] — Pi-side listener
- [[radiens-api-reference|Radiens API Reference]] — Allego/Radiens host-side API (sits on top of libxdaq)

## Sources

- libxdaq docs: <https://developer.kontex.io/libxdaq-docs/index.html>
- libxdaq-dist (deprecated repo w/ Linux x64 binary + tested-toolchain table): <https://github.com/kontex-neuro/libxdaq-dist>
- kontex-conan (current Conan index): <https://github.com/kontex-neuro/kontex-conan>
- pylibxdaq (Python bindings, master branch): <https://github.com/kontex-neuro/pylibxdaq>
- XDAQ-Compatible-Softwares: <https://github.com/kontex-neuro/XDAQ-Compatible-Softwares>
- Intan-RHX (XDAQ-RHX): <https://github.com/kontex-neuro/Intan-RHX>
- XDAQ product page (Thunderbolt latency/throughput claim): <https://www.kontex.io/xdaq>
