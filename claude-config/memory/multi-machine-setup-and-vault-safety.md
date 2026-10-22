---
name: multi-machine-setup-and-vault-safety
description: "Syncthing is RETIRED on every machine (2026-09-19); why the vault died 2026-04-29; apt purge / autoremove lessons. History and detail are in the vault"
metadata:
  type: project
---

❌ **Syncthing is RETIRED on every machine** (e10ubuntu + office PC uninstalled 2026-09-16, ThinkPad verified 2026-09-19). The vault was lost 2026-04-29 because the synced folder had no versioning and a live `.git` was replicated. `./skim check` keeps a tripwire; never point Syncthing at this repo again. Identities are parked in `~/syncthing-config-retired-2026-09-16` on each machine (deleting them makes a reinstall look like a NEW device).

Details: [[multi-machine-work-setup]] (history, sync baseline, claude-portable, NAS and code-folder hazards); live workflow in [[multi-machine-workflow]].

- 🔴 `apt purge` does NOT stop a running daemon (systemd keeps the unit loaded): stop the service BEFORE purging, `pkill -x` if needed.
- 🔴🔴 `sudo apt autoremove` has no fixed blast radius (13 libs on e10, 52 packages incl. the whole NVIDIA stack on the office PC). READ THE AUTOREMOVE LIST ON THE MACHINE YOU ARE SITTING AT, EVERY TIME; purging a stranded driver metapackage can mark the working one auto-removable (fixed with `apt-mark manual nvidia-driver-580-open nvidia-dkms-580-open dkms`).
- 🔑 A command written into a guide is not a validated command (tmux was missing on e10ubuntu until 2026-08-19): see [[feedback_verify_operational_details]].
- ⚠️ The office PC (`Andrea-KAIST-PC-ubuntu`) held uncommitted `neurosurveillance` work with no other copy (not triaged as of 2026-09-16): check before wiping it.
- Retired-era rules, in case Syncthing is ever revived (it should not be): never remove a folder with "delete on disk"; never point it at a directory that already holds another copy (new device = empty dir, RECEIVE ONLY first, verify counts); versioning mandatory; `.git` excluded; cold `tar` snapshot first. The claude-portable-era warnings (do not copy the vault timer pattern; bootstrap manual once per machine) died with claude-portable.
