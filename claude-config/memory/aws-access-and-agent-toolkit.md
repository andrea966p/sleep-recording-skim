---
name: aws-access-and-agent-toolkit
description: "AWS access since 2026-09-19: account, profile andrea, region ap-northeast-2; SSO session dies overnight (never for unattended jobs); apt awscli has no `aws login`; harden ~/.aws dirs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 39405dad-26c3-455d-ba64-6dc77c2f4243
  modified: 2026-09-19T07:58:03.133Z
---

AWS access since **2026-09-19**: account 760396521414, CLI profile `andrea`, default region `ap-northeast-2` (Seoul); Agent Toolkit service is us-east-1 only. `aws login --profile andrea` gives a 15-minute STS token plus refresh token; it renews silently mid-session but the SESSION DIES OVERNIGHT, so an unattended job needs its OWN IAM user with a static key, never SSO ([[radix-s3-archive]]).

Details: [[aws-access-and-agent-toolkit]]

🔴 `chmod 700 ~/.aws{,/login,/login/cache,/cli,/cli/cache}` on every new machine (the login cache holds a PLAINTEXT secret key and the CLI creates those dirs 755). 🔴 Ubuntu's apt `awscli` has no `aws login`: use the official installer (`https://awscli.amazonaws.com/v2/install.sh`, user-local). 🔴 `aws login` blocks until the browser sign-in finishes; no `Updated profile ... credentials` line = not logged in. 🔴 The `aws-mcp` entry needs `env.AWS_MCP_PROXY_PROFILES=andrea` or it fails with JSON-RPC -32602. ⚠️ `~/.claude/skills` and `~/CLAUDE.md` are symlinks into the repo, so toolkit updates appear in git diffs.
