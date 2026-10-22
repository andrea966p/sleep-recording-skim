---
type: hub
area: computing
status: active
created: 2026-10-22
summary: "The machines (e10ubuntu rig, laptops, workstation), Tailscale, the one-repo ./skim workflow, monitoring (Netdata, Uptime Kuma, ntfy), production values and AWS"
---

# Computing hub

## What this is
`e10ubuntu` (Core Ultra 5 125H, user `skimlab`, `192.168.0.50`) runs the rig, Docker and Frigate; the ThinkPad, the SKIM office workstation and the old office PC are the other machines.
All of them share one private git repo, `sleep-recording-skim`, synced by hand with `./skim`, and reach each other over Tailscale.
Monitoring is Netdata plus Uptime Kuma, pushing to ntfy; real addresses and usernames are in [[production-values]].

## Current state
- 2026-10-22: Netdata is v2.12.1 (live `netdata -v`) and alerts go to ntfy; recording-stall and reconciler alerts still go to Slack through `nvr-mqtt-slack.service` [[monitoring-setup]] [[watchdog-slack-bridge]]
- 2026-09-20: deploy scripts push to ntfy through `nvr-notify.sh` instead of Slack [[backup-architecture]]
- 2026-09-19: ThinkPad is on the push/pull workflow; Syncthing is confirmed gone from every machine [[multi-machine-workflow]]
- 2026-09-19: AWS access exists (account, profile, region) [[aws-access-and-agent-toolkit]]
- 2026-09-16: SKIM office workstation joined as the fourth machine [[multi-machine-work-setup]] [[multi-machine-workflow]]
- 2026-09-14: Netdata and Uptime Kuma alerts moved from Slack to ntfy [[monitoring-setup]]
- 2026-09-10: workspace became one git repo synced manually with `./skim` [[multi-machine-work-setup]]

## Start here
- [[multi-machine-workflow]]: the live workflow and machine table
- [[production-values]]: addresses, tailnets, services, hardware (private)
- [[monitoring-setup]]: Netdata, Uptime Kuma and the ntfy switch
- [[nvr-alerts-config]]: the 16 Netdata alert rules
- [[aws-access-and-agent-toolkit]]: AWS login and its traps

## Rules that must not be broken
- Do not enable Tailscale SSH on `e10ubuntu`; it takes over port 22 and breaks the laptops' key-based `ssh e10`. Evidence: [[multi-machine-work-setup]]
- Never restart `tailscaled` over a Tailscale SSH session. Evidence: [[2026-02-09-tailscale-restart-lockout]]
- Never let a second sync system touch the repo. Evidence: [[2026-04-29-syncthing-deletion-and-recovery]]
- `./skim check` and a git identity on every new machine; `KEPT ... differs` from `bootstrap.sh` is not a clean result. Evidence: [[multi-machine-workflow]]
- Read the `apt autoremove` list on the machine you are sitting at. Evidence: [[multi-machine-workflow]]
- The ntfy recipient must be a full `https://ntfy.sh/<topic>` URL; a bare topic fails silently. Evidence: [[monitoring-setup]]
- `nvr-alerts-config` is a golden config: change only after testing. Evidence: [[nvr-alerts-config]]
- SSO never drives unattended jobs; they use their own IAM user. Evidence: [[aws-access-and-agent-toolkit]]
- Never run bare `ntfsfix`; it sets the dirty bit. Evidence: [[usb-hdd-ntfs-dirty-bit]]
- Keep this vault private: [[production-values]] holds real addresses.

## Open items
- The Slack webhook URL was in `nvr-alerts-config` (now redacted) and in git history; the webhook is still live, so consider rotating it [[nvr-alerts-config]]
- Uptime Kuma and Netdata notes still describe Slack in their body text; only banners were added [[monitoring-diagnostics]]
- Office PC `Andrea-KAIST-PC-ubuntu` holds uncommitted work in the old tree and is not on the workflow [[multi-machine-work-setup]]
- The root `CLAUDE.md` still says Ultra 7 and hostname `frigate-server`; the live machine is Ultra 5 125H and `e10ubuntu`

## Everything here
![[area.base]]
