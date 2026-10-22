---
tags: [procedure, eeg, allego, recording, console, runbook, recovery, startup]
created: 2026-09-13
status: active
---

# Starting everything after a restart, a crash, or a screen that went black

> [!abstract] TL;DR
> **Almost nothing needs starting.** The console, the NAS mount and the network come back by
> themselves. The only thing a human ever launches is the **Allego GUI**.
>
> ```bash
> ~/sleep-recording-skim/eeg-recorder/deploy/rig-check.sh
> ```
>
> Green all the way down ⇒ open **<http://127.0.0.1:8600>** and set up your run. Anything red
> tells you the one command that fixes it. The check changes nothing and is safe to run while a
> recording is in progress.

## 1. What starts itself, and what you start

| | who starts it | survives a desktop crash? | survives a reboot? |
|---|---|---|---|
| `tailscaled` (network to the NAS) | systemd, at boot | **yes** | yes |
| `eeg-recorder` (the console at :8600) | systemd, at boot | **yes** | yes |
| `mnt-skimnas` (the NAS share) | systemd, on first access | **yes** | yes |
| `neurosurveillance-session`, Frigate | systemd / Docker, at boot | yes | yes |
| **the Allego GUI** | **a human, every time** | **no** | **no** |

The three things a recording depends on are **system** services. They are not part of your
desktop session, so logging out, a GUI crash, a RustDesk restart or a remote-desktop disconnect
does not touch them. **A recording in progress keeps recording through all of those.**

Allego is the exception: it is a desktop application, and when the session goes, it goes. There is
no service for it and it is not automated on purpose — it is the piece that talks to amplifiers
with animals attached.

## 2. 🔴 "The PC crashed" is usually not what happened

This confusion has cost real time, so check it before acting:

```bash
uptime -s          # the last time this machine actually booted
```

If that date is old, **the machine never went down** — only your view of it did.

> [!example] 2026-09-13, the case this page was written for
> The screen went black and the session appeared dead, so the PC was rebooted — or so it seemed.
> The log said otherwise:
>
> ```
> 15:04:52  skimlab : TTY=pts/0 ; COMMAND=/usr/bin/systemctl restart rustdesk
> 15:04:52  Session 51119 logged out ... Removed session 51119
> 15:04:52  Started rustdesk.service - RustDesk
> ```
>
> A RustDesk restart drops the desktop session and builds a new one. From the far end that is
> indistinguishable from a machine rebooting. `uptime -s` said **2026-08-14** — four weeks earlier.
> The console had been running the whole time and had never missed a request.

Why it matters: if you think the machine rebooted you will go looking for services to restart, and
restarting `eeg-recorder` during a live recording is a thing to avoid doing for no reason.

| what you saw | what to run | what it means |
|---|---|---|
| screen black / remote desktop dead | `uptime -s` | old date ⇒ session only. Log back in, nothing else to do |
| everything looks new after a power cut | `uptime -s` | today's date ⇒ a real boot, go to section 3 |
| Allego window gone, machine fine | `pgrep -f /opt/allego/allego` | nothing ⇒ relaunch it, section 4 |

## 3. After a real reboot

```bash
~/sleep-recording-skim/eeg-recorder/deploy/rig-check.sh
```

It reports, in order: the host, the three services, the console, the rig, the NAS, the disk, any run
in flight, and the Allego process. Each red line carries its own fix. Expect this:

```
=== services (these survive a desktop crash) ===
tailscaled                   active (enabled at boot)
eeg-recorder                 active (enabled at boot)
mnt-skimnas.automount        active (enabled at boot)

=== the console ===
web page                     http://127.0.0.1:8600  (HTTP 200)
allego                       reachable | XDAQ_ONE_REC | 1000.0 Hz | rec R_OFF
nas                          mounted, sentinel ok, 1389 GB free
local disk                   758 GB free, 161 h at 3.77 GB/h
active run                   none
waiting to upload            none

READY. Open http://127.0.0.1:8600
```

Nothing on that list needs a human when it is green. If a service really is down:

```bash
sudo systemctl start eeg-recorder
```

The NAS mount needs no command at all — it is an `.automount` and attaches on first access. It also
detaches itself after 600 s idle, so **"not mounted" is the normal resting state and not a fault**.

## 4. Launching Allego — the one manual step

Launch it from the desktop as usual, then:

> [!warning] Use `--disable-gpu`
> Allego crashes in the Intel Mesa driver on this machine. On 2026-08-24 that killed a run and
> produced a 6.5 GB log storm. Launching with `--disable-gpu` is the fix, and it is the thing most
> easily forgotten on a hurried relaunch. `rig-check.sh` warns when the running process lacks it.
>
> ```bash
> /opt/allego/allego --disable-gpu
> ```

> [!danger] CHECK THE MODE AND THE SAMPLING RATE EVERY TIME
> A freshly launched Allego can come up in **`SMARTBOX_PRO` at 30 kHz**. This rig records
> **`XDAQ_ONE_REC` at 1000 Hz**. Recording in the wrong mode produces a file that looks fine, is
> enormous, and that this project's analysis cannot read as a sleep recording — and nothing later
> in the chain notices. `rig-check.sh` fails loudly on this; the console header shows it too.

🛑 **Never `pkill -f /opt/allego/allego`** — the pattern matches your own shell and kills it.

## 5. Was a recording running when it happened?

```bash
curl -s 127.0.0.1:8600/api/state | python3 -m json.tool | grep -A3 active_run
```

- **A desktop crash does not stop a recording.** Allego dying *does*, because it owns the hardware.
- **The console re-arms itself on restart.** Anything caught mid-flight is rewound to the last state
  it can act from — `STARTING`→`SCHEDULED`, `STOPPING`→`RECORDING`, `UPLOADING`→`UPLOAD_PENDING` —
  and schedules are re-read from the database, so a scheduled run outlives any restart.
- **Runs waiting in `UPLOAD_PENDING` are not broken.** They drain in order when the NAS answers.
- The raw file on disk is whatever Allego wrote before it stopped. If Allego died mid-recording the
  file is short but valid; check it with bytes on disk, never by trusting the app's own state.

Full rules: [[pipeline-architecture]] §3.5.

## 6. When something is actually wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| `rig-check.sh`: console HTTP 000 | service down or crashed | `sudo systemctl restart eeg-recorder`, then `journalctl -u eeg-recorder -n 50` |
| `allego NOT REACHABLE` | the GUI is not open | launch it (section 4); the console cannot start it for you |
| `SMARTBOX_PRO` or `30000.0 Hz` | fresh Allego defaults | fix in the GUI **before** recording — see the danger box above |
| `nas NOT USABLE` | share unreachable or sentinel missing | `systemctl start mnt-skimnas.mount`; recording still works, uploads queue |
| page loads but shows stale numbers | browser cached an old page | hard reload (Ctrl+Shift+R) |
| the desktop keeps dropping | RustDesk / HDMI switch | the fix (a forced `video=HDMI-A-1:1920x1080@60e` kernel line) is in [[2026-07-15]] |

## 7. Related

- [[eeg-recording-console]] — how to set up and run a recording once you are in
- [[pipeline-architecture]] — every program, what fires it, every failsafe
- [[skim-nas-smb-and-upload]] — the mount, its guards, and how uploads are verified
- [[pre-flight-connection-screen]] — still gates any recording whose timepoint cannot be repeated
