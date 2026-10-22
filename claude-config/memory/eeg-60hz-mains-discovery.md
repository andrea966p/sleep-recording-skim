---
name: eeg-60hz-mains-discovery
description: "2026-07-05: Korea mains is 60 Hz, not 50 Hz; the Allego notch and all vault analysis were at 50 Hz for weeks, so 'bad electrode' weeks were largely 60 Hz hum."
metadata: 
  node_type: memory
  type: project
  originSessionId: f385765f-e351-48d5-99db-fea82c4d69f4
---

**2026-07-05:** South Korea mains = 60 Hz, not 50. The Allego notch and all analysis had been set to 50 Hz for weeks, so the real interference was never filtered; single EEG legs carried ~10 mV of 60 Hz and looked railed/open, which led to the wrong conclusion that 8 mice were badly implanted. Measured: dominant frequency 59.9 Hz on every channel, common-mode 15 to 4900 uV tracking ground quality. One systematic environmental problem, not bad surgeries.

Details: [[60hz-mains-hum-discovery]]

⚠️ The original "notch + pad0-pad1 bipolar difference offline" framing is outdated: the RHD2216 channels are already bipolar on the chip (never subtract EEG from EMG or pads offline). Measure hum as the 55-65 Hz band, not a single 60.00 Hz bin.
