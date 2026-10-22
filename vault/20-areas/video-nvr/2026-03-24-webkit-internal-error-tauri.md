---
tags: [troubleshooting, incident, tauri, webkit, frontend]
date: 2026-03-24
severity: medium
status: resolved
affected: [neurosurveillance-ui]
---

## Summary
- **Date/Time:** 2026-03-24
- **Severity:** Medium — GUI completely fails to launch
- **Status:** Resolved (WebKitGTK downgrade + apt pin)

## Symptoms
- Running `npm run tauri dev` shows:
  ```
  ERROR: WebKit encountered an internal error. This is a WebKit bug.
  Source/WebKit/WebProcess/Network/WebLoaderStrategy.cpp(618) : void WebKit::WebLoaderStrategy::internallyFailedLoadTimerFired()
  ```
- Environment variable workarounds (`WEBKIT_DISABLE_DMABUF_RENDERER`, `WEBKIT_DISABLE_COMPOSITING_MODE`, `LIBGL_ALWAYS_SOFTWARE`, `WEBKIT_DISABLE_SANDBOX_THIS_IS_DANGEROUS`) have **no effect**

## Root Cause
**WebKitGTK `2.50.4-0ubuntu0.24.04.1` has a bug** where the WebProcess crashes during page loading. The NetworkProcess successfully connects to the dev server (confirmed via debug logs), but the WebProcess fails with `internallyFailedLoadTimerFired()`.

This is a known upstream bug affecting multiple Tauri/WebKit apps (GitButler, Portmaster, RapidRAW). See: [gitbutler#12885](https://github.com/gitbutlerapp/gitbutler/issues/12885)

The bug was introduced when Ubuntu pushed WebKitGTK from `2.44.0-2` to `2.50.4` as a security update.

## Fix Applied

### 1. Downgraded WebKitGTK to `2.44.0-2`
```bash
sudo apt install --allow-downgrades -y \
  libwebkit2gtk-4.1-0=2.44.0-2 \
  libwebkit2gtk-4.1-dev=2.44.0-2 \
  gir1.2-webkit2-4.1=2.44.0-2 \
  libjavascriptcoregtk-4.1-0=2.44.0-2 \
  gir1.2-javascriptcoregtk-4.1=2.44.0-2 \
  libjavascriptcoregtk-4.1-dev=2.44.0-2
```

### 2. Pinned packages to prevent auto-upgrade
Created `/etc/apt/preferences.d/pin-webkitgtk`:
```
Package: libwebkit2gtk-4.1-0 libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1 libjavascriptcoregtk-4.1-0 gir1.2-javascriptcoregtk-4.1 libjavascriptcoregtk-4.1-dev
Pin: version 2.44.0-2
Pin-Priority: 1001
```

## How to Test Upgrade Later
When Ubuntu ships WebKitGTK `2.52+` (which has improved libsoup3 handling):
1. Remove the pin: `sudo rm /etc/apt/preferences.d/pin-webkitgtk`
2. Upgrade: `sudo apt upgrade`
3. Test: `npm run tauri dev`
4. If it breaks, re-apply the downgrade commands above

## What Did NOT Work
- `WEBKIT_DISABLE_DMABUF_RENDERER=1`
- `WEBKIT_DISABLE_COMPOSITING_MODE=1`
- `LIBGL_ALWAYS_SOFTWARE=1`
- `WEBKIT_DISABLE_SANDBOX_THIS_IS_DANGEROUS=1`
- `WEBKIT_FORCE_SANDBOX=0`
- All combinations of the above

These address GPU rendering issues, not the WebProcess/NetworkProcess communication bug in 2.50.4.
