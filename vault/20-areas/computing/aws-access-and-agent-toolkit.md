---
type: reference
area: computing
status: active
created: 2026-10-22
summary: "AWS access since 2026-09-19: account, SSO profile, region, why SSO cannot run unattended jobs, and the traps on a new machine"
tags: [aws, computing, credentials]
---

# AWS access and the Agent Toolkit

> [!abstract] TL;DR
> The lab has AWS access since **2026-09-19**. Account `760396521414`, SSO role
> `AWSReservedSSO_AdministratorAccess`, CLI profile `andrea`, default region `ap-northeast-2` (Seoul).
> Interactive work uses the SSO profile. **Unattended jobs never use SSO**: the nightly S3 archive runs as its
> own IAM user, see [[radix-s3-archive]]. Promoted into the vault 2026-10-22 from the workspace memory file
> `aws-access-and-agent-toolkit` (saved 2026-09-19). The account number is also in [[backup-architecture]].

## How login behaves

- `aws login --profile andrea` opens a browser, then issues a **15-minute** STS token plus a refresh token.
  The CLI renews silently within a session, but the session itself expires: the 2026-09-19 17:16 KST login
  was dead by 2026-09-20 12:00. Fine mid-task, useless for anything unattended.
- 🔴 `aws login` blocks until the browser sign-in finishes and only then prints `Updated profile ... credentials`.
  No success line means not logged in. A stale attempt keeps holding its callback port, so a second
  `aws login` silently does nothing until the first is killed.
- The short `expiresAt` in `~/.aws/login/cache/*.json` is not the session length. Browser re-auth is needed
  again after 90 days. The Agent Toolkit service itself is us-east-1 only, whatever the profile region.

## Traps on every new machine

- 🔴 **The login cache holds the plaintext secret key, session token and refresh token.** The file is `600`
  but the CLI creates `~/.aws/login`, `~/.aws/login/cache`, `~/.aws/cli`, `~/.aws/cli/cache` as `755` and
  `~/.aws/cli/cache/session.db` as `644`. Verified 2026-09-19 and fixed on the ThinkPad:
  `chmod 700 ~/.aws ~/.aws/login ~/.aws/login/cache ~/.aws/cli ~/.aws/cli/cache`. Re-check on each new machine.
- 🔴 **Ubuntu's apt `awscli` has no `aws login` and no `aws configure agent-toolkit`.** `/usr/bin/aws` was
  2.31.35 from apt and `aws --version` worked, so AWS's own setup doc concluded "already installed" and step 3
  died with `argument command: Found invalid choice 'login'`. Fix: run the official installer
  (`https://awscli.amazonaws.com/v2/install.sh`, user-local to `~/.local/bin`, GPG-verified) and rely on PATH order.
- 🔴 The generated `aws-mcp` MCP entry falls back to the `default` profile, so it needs
  `env.AWS_MCP_PROXY_PROFILES=andrea` or the server fails with `JSON-RPC error: -32602`
  (set in `~/.claude.json` and `~/.gemini/settings.json`).
- `~/.claude/skills` and `~/CLAUDE.md` are symlinks into the git repo, so the toolkit's 23 skills (4 MB) and its
  rules block landed in `claude-config/` and were pushed to all four machines (commit `5b973ac`).
  Vendor content is updated by `aws agent-toolkit`, not by hand: expect it in diffs ([[multi-machine-workflow]]).

## e10

e10 has no passwordless sudo, so the AWS CLI there is user-local (`/home/skimlab/.local/bin/aws`) and scheduling
is cron, not systemd. Profile `radix-backup` (IAM user `radix-s3-backup`, explicit Deny on delete) is the only
profile on e10; the SSO profile `andrea` is not configured there (checked 2026-10-22: "config profile could not
be found").
