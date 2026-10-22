---
type: procedure
area: video-nvr
status: active
tags:
  - procedure
  - raspberry-pi
  - go2rtc
  - camera
  - framing
created: '2026-06-19'
scope: 'Pi1 (pi_cam_0, pi_cam_1); Pi2 off'
---
# Camera Per-Partition Framing via rpicam-vid `--roi`

> [!abstract] TL;DR — for non-technical readers
> **What this is.** How we crop each Pi camera so it frames **one chamber/partition** instead of catching the neighbors. Done digitally with `rpicam-vid --roi` (a sensor crop/zoom) inside the go2rtc exec string — no camera move, no new mount.
>
> **Why it exists.** With one camera per partition, the stock wide lens also captured the adjacent chambers on the left/right edges. The ROI crop boxes the view onto the target chamber. See the [[golden-go2rtc-config|golden go2rtc config]] for the base settings.
>
> **How to read this page.** §1 = current live-test state. §2 = how to tune. §3 = pending steps before this becomes golden. Big picture: [[nvr-system-overview]].

> [!warning] STATUS: live test on Pi1 / pi_cam_0 only — NOT yet golden
> A non-golden `--roi` was applied directly to the running `/opt/go2rtc/go2rtc.yaml` on Pi1 for evaluation. The vault [[golden-go2rtc-config|golden config]] is **unchanged**. Promote only after the lens swap + tuning (§3).

## 0. Mechanism
`rpicam-vid --roi x,y,w,h` crops a normalized (0–1) sub-region of the sensor, then scales it back to the encode size (`--width 1024 --height 768`). It trims the neighbors without moving the camera. If the crop region's aspect ≠ 4:3, the image stretches — match the chamber shape or change output size to avoid it.

## 1. Current live-test state (2026-06-19)
- **Pi1 `pi_cam_0`:** `--roi 0.18,0.04,0.64,0.92` inserted before `--output -` in the exec string. go2rtc restarted. Result: framing tightened onto the center chamber; **minor leftover** — thin sliver of left-neighbor (blue tape top-left, chamber bit bottom-left).
- **Pi1 `pi_cam_1`:** untouched (no ROI yet).
- **Pi2:** powered off.
- **Backup on Pi1:** `/opt/go2rtc/go2rtc.yaml.bak.20260619` — revert with `sudo cp` of the `.bak` + `sudo systemctl restart go2rtc.service`.
- **Lens:** still **fisheye/wide** — barrel distortion visible. User swapping to a **non-fisheye lens after lunch** → ROI numbers will change after the swap.

## 2. How to tune (live)
Edit only the target camera's line (sudo, on the Pi), restart, eyeball at `http://192.168.0.11:1984`:
```bash
# adjust the four numbers, pi_cam_0 only
sudo sed -i '/pi_cam_0:/ s/--roi [0-9.,]* /--roi <x>,<y>,<w>,<h> /' /opt/go2rtc/go2rtc.yaml
sudo systemctl restart go2rtc.service
```
- More left trim → raise `x`, lower `w`. Center vertically → tweak `y`/`h`.
- `--roi` flag name: if a build rejects it, `rpicam-vid --help | grep -i roi` for the exact option.

## 3. Pending before golden (after lunch)
1. **Swap to non-fisheye lens** on Pi1 cameras, refocus (manual lens ring) at the live view.
2. **Re-tune `--roi`** for the new lens (current values are fisheye-specific) on `pi_cam_0`.
3. **Apply matching ROI to `pi_cam_1`** for its partition.
4. **Decide aspect:** keep 1024×768 (slight stretch if crop is square) vs switch output to square — square changes **Frigate detect resolution + bitrate** (update [[golden-go2rtc-config|golden config]] + Frigate config + StoragePanel notes).
5. **Promote to golden:** update the golden go2rtc config doc (v5.3), note Syncthing sync to PC2, repeat on **Pi2** when powered on.

## Related
- [[golden-go2rtc-config|Golden go2rtc Config]] · [[golden-systemd-service|systemd service]]
- [[production-values|Production Values]]
