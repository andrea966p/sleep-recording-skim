---
tags: [troubleshooting, incident, tauri, webkit, gpu, frontend]
date: 2026-03-24
severity: medium
status: resolved
affected: [neurosurveillance-ui]
---

## Summary
- **Date/Time:** 2026-03-24
- **Severity:** Medium — GUI completely fails to launch
- **Status:** Resolved (software rendering workaround)

## Symptoms
- Running `npm run tauri dev` shows "WebKit encountered an internal error"
- Setting `WEBKIT_DISABLE_DMABUF_RENDERER=1` alone does not fix it
- Setting `WEBKIT_DISABLE_COMPOSITING_MODE=1` alone does not fix it

## Root Cause
WebKitGTK `2.50.4` attempts GPU-accelerated rendering via multiple paths (DMA-BUF, EGL compositing, hardware GL). On this system:
- **Kernel:** `6.17.0-14-generic` (HWE)
- **GPU:** Intel Meteor Lake-P (xe DRM driver)
- **Display:** X11

Each env var only closes **one** GPU path. WebKit falls through to other GPU paths that also fail with the bleeding-edge xe driver. All three vars must be set together:
- `WEBKIT_DISABLE_DMABUF_RENDERER=1` — disables DMA-BUF renderer
- `WEBKIT_DISABLE_COMPOSITING_MODE=1` — disables compositing
- `LIBGL_ALWAYS_SOFTWARE=1` — forces Mesa llvmpipe software rasterizer (the critical one)

## Fix Applied
1. **Primary (Rust-level):** `src-tauri/src/main.rs` sets all three env vars before WebKit init, guarded by `#[cfg(target_os = "linux")]`
2. **Convenience:** `package.json` has `tauri:dev` and `tauri:build` scripts with vars pre-set

The Rust fix works regardless of launch method (dev, AppImage, deb, CLI). Each var is only set if not already present, allowing user override.

## Performance Impact
Software rendering via llvmpipe is slightly slower for complex CSS animations but negligible for a monitoring dashboard.

## How to Test Removal
After a kernel or WebKitGTK update:
```bash
LIBGL_ALWAYS_SOFTWARE=0 WEBKIT_DISABLE_DMABUF_RENDERER=0 WEBKIT_DISABLE_COMPOSITING_MODE=0 npm run tauri dev
```
If the window opens without error, the workaround can be removed from `main.rs`.
