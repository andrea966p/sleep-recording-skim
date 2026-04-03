# TEMP: Apply CPU Power Cap (RAPL)
> Delete this note when done.

## Why
CPU baseline is 68–74°C overnight due to uncapped power limit (200W). Any burst touches 75°C → Netdata alert fires. Capping to 20W brings baseline under 70°C.

---

## Step 1 — Apply immediately (takes effect now, lost on reboot)

```bash
echo 20000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

Verify it took:
```bash
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```
Expected output: `20000000`

Check temperature dropped (wait ~2 min):
```bash
sensors | grep "Package id"
```
Expected: under 65°C at idle.

---

## Step 2 — Create the systemd service file

```bash
sudo nano /etc/systemd/system/cpu-power-cap.service
```

Paste this content:

```
[Unit]
Description=Intel RAPL CPU power cap
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 20000000 > /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 3 — Enable and start the service

```bash
sudo systemctl enable --now cpu-power-cap.service
```

Verify it's active:
```bash
systemctl status cpu-power-cap.service
```
Expected: `active (exited)` — that's normal for a oneshot service.

---

## Step 4 — Confirm it survives reboot (optional but recommended)

```bash
sudo reboot
```

After reboot:
```bash
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
sensors | grep "Package id"
```

Both should show 20000000 and temp under 65°C.
