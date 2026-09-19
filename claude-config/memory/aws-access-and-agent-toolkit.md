---
name: aws-access-and-agent-toolkit
description: "AWS access exists as of 2026-09-19 — account, profile, region, and the apt-awscli trap that blocks `aws login`"
metadata: 
  node_type: memory
  type: project
  originSessionId: 39405dad-26c3-455d-ba64-6dc77c2f4243
  modified: 2026-09-19T07:58:03.133Z
---

The lab has AWS access as of **2026-09-19**. AWS Agent Toolkit set up on the
ThinkPad ([[workspace-single-repo-sleep-recording-skim]]).

- Account **760396521414**, SSO role `AWSReservedSSO_AdministratorAccess`, user `andreap`.
- CLI profile **`andrea`**, default region **`ap-northeast-2`** (Seoul).
- `aws login --profile andrea` opens a browser once, then issues a **15-minute**
  STS token plus a **refresh token**, so the CLI renews silently and you never
  hit an expiry mid-task. The short `expiresAt` in
  `~/.aws/login/cache/*.json` is NOT the session length — do not re-login on
  seeing it. Browser re-auth needed again after 90 days. Agent Toolkit service
  itself is **us-east-1 only**, whatever the profile region.

🔴 That same cache file holds the **plaintext secret access key, session token
and refresh token**. The file is `600` but the CLI creates
`~/.aws/login`, `~/.aws/login/cache`, `~/.aws/cli`, `~/.aws/cli/cache` as
**`755`** and `~/.aws/cli/cache/session.db` as **`644`**. Verified 2026-09-19 and
fixed to `700` on the ThinkPad; `chmod` does not disturb a live session. **Check
this on every new machine** — the installer will make them world-listable again.

🔴 **Ubuntu's apt `awscli` has no `aws login` and no `aws configure
agent-toolkit`.** `/usr/bin/aws` was 2.31.35 from apt and `aws --version`
succeeded, so AWS's own setup doc concluded "already installed" and step 3 died
with `argument command: Found invalid choice 'login'`. Fix = run the official
installer (`https://awscli.amazonaws.com/v2/install.sh`, user-local to
`~/.local/bin`, GPG-verified) and rely on PATH order. The apt package is still
installed and shadowed, not removed. **Any new machine will hit this same trap.**

🔴 The generated `aws-mcp` MCP entry falls back to the `default` profile, so it
must carry `env.AWS_MCP_PROXY_PROFILES=andrea` or the server fails to start with
`JSON-RPC error: -32602`. Set in `~/.claude.json` and `~/.gemini/settings.json`.

⚠️ `~/.claude/skills` and `~/CLAUDE.md` are **symlinks into the git repo**, so
the toolkit's 23 skills (4 MB) and its rules block landed in
`claude-config/` and were pushed to all 4 machines (commit `5b973ac`). Vendor
content updated by `aws agent-toolkit`, not by hand — expect it in diffs.
