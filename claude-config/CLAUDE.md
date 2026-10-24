# CLAUDE.md

Guidance for Claude Code in the SKIM sleep lab workspace (repo `sleep-recording-skim`).

## Where knowledge lives

The Obsidian vault `vault/` is the single source of truth: start at `vault/HOME.md`, and
follow `vault/CLAUDE.md` for where notes go, the frontmatter schema and the accuracy rules.
Claude memory (`claude-config/memory/`) holds behaviour rules and pointers into the vault,
not facts. `./skim lint` checks the vault (read-only).

## The rig host (checked 2026-10-22)

- **Host:** `e10ubuntu`, user `skimlab`, LAN `192.168.0.50`, Tailscale `100.82.250.62`
- **Hardware:** ASUS NUC with Intel Core Ultra 5 125H, 30 GiB RAM, 1.9 TB NVMe
- **OS:** Ubuntu 24.04.5 LTS, kernel `7.0.0-28-generic` (7.0.0-31 blocklists the Intel GPU
  in Chromium, which Allego needs: see the Allego hub in the vault)
- **Runs:** the EEG rig (XDAQ, Allego/Radiens), the recording console
  (`http://127.0.0.1:8600`), and the video NVR stack (Frigate under `/srv/frigate`,
  Mosquitto, the session daemon in `/opt/neurosurveillance`). The cameras are
  disconnected since 2026-08-04; the video area is active and will resume.
- **Constraints:** stability first (LTS packages, Docker images pinned by SHA and held with
  `apt-mark`), validate every step, record version numbers for publication.
- Node.js via **nvm** (`lts/*`).

## Working from a machine other than e10ubuntu

The rig, the NVR, Allego/Radiens, Docker, Frigate and the EEG data all live on
`e10ubuntu` (Tailscale `100.82.250.62`). Only that machine can run those commands.

Five machines share this workspace: `e10ubuntu` (the rig), the **SKIM office workstation**
(`/home/skim`, added 2026-09-16), the **ThinkPad** (`thinkpadubuntu`, user `andrea`, live on
the workflow 2026-09-19), **`kaist-bilab-win`** (Windows, Git Bash, for EthoVision and Office,
added 2026-10-24; from e10: `ssh andrea@100.88.120.75`), and the office PC
(`Andrea-KAIST-PC-ubuntu`, still on the old tree). The table in `vault/20-areas/computing/multi-machine-workflow.md` has the paths; the older
`multi-machine-work-setup.md` beside it also lists each machine's memory slug.

To drive the ThinkPad from here: `tailscale ssh andrea@thinkpadubuntu '<command>'`. It has
no sshd, so ordinary `ssh` will not reach it. 🛑 Do not enable Tailscale SSH on `e10ubuntu`
— it hijacks port 22 for tailnet peers and breaks the laptops' key based `ssh e10`.

From any machine that is not `e10ubuntu`, run rig commands over SSH instead:

```bash
ssh e10 'docker ps'
ssh e10 'vainfo'
```

For anything long running, use tmux so an SSH drop does not kill it:

```bash
ssh e10 -t 'tmux new -As rig'
```

tmux was MISSING on `e10ubuntu` until 2026-08-19 even though this line had promised it since
2026-08-16, so anything long running started that way before then died with the connection.
Installed now: `tmux 3.4` on e10ubuntu, `3.6` on the ThinkPad.

The whole workspace is ONE git repository, `sleep-recording-skim`, cloned on every
machine: the Obsidian vault, the recording software, the analysis code and this Claude
configuration. Vault files are local everywhere, so they need no SSH.

Sync is MANUAL and is one command:

```bash
./skim status          # am I behind? what have I not committed?
./skim pull            # before you start editing
./skim push "message"  # when you stop
```

Nothing commits or pushes by itself. `skim status` is read-only and runs at session
start; every writing verb is typed by a human.

> [!warning] Syncthing is RETIRED for this workspace
> Syncthing and git both syncing one directory, with a live `.git` replicated and no
> file versioning, destroyed the vault on 2026-04-29. `./skim check` fails if Syncthing
> is ever pointed back at this repository. **Gone from every machine** as of 2026-09-19.

> [!tip] A machine can pass every check and still be unable to push
> `machine/check.sh` and `./skim status` do not look at the git identity, and `./skim push`
> commits before it pushes. On a new machine set
> `git config --global user.name "andrea966p"` and
> `git config --global user.email "andrea96p@kaist.ac.kr"`.

> [!tip] On a new machine, `bootstrap.sh` success is not the whole story
> It KEEPS an existing `~/.claude/settings.json` and only prints `KEPT ... differs from
> the template`. Diff it: a machine that used Claude Code before this repo can end up with
> no hooks and therefore no `skim status` at SessionStart. See `machine/README.md`.

Full setup and the workspace rules: `vault/20-areas/computing/multi-machine-workflow.md`
and `machine/README.md`.

<!-- BEGIN AWS Agent Toolkit rules -->

# AWS Guidance

- Where these AWS rules conflict with the project's own instructions, the
  project's instructions take precedence.
- Prefer the AWS MCP Server for AWS interactions — it provides sandboxed
  execution, observability, and audit logging. If unavailable, use the
  AWS CLI directly.
- Before starting a task, check whether a relevant AWS skill is available.
  Load the skill with `retrieve_skill` and prefer its guidance over
  general knowledge.
- When uncertain about specific AWS details (API parameters, permissions,
  limits, error codes), verify against documentation rather than guessing.
  State uncertainty explicitly if you cannot confirm.
- When creating infrastructure, prefer infrastructure-as-code (AWS CDK or
  CloudFormation) over direct CLI commands.
- When working with infrastructure, follow AWS Well-Architected Framework
  principles.
- Do not use em dashes in AWS resource names or descriptions. Use
  hyphens instead.

## Secret Safety

- MUST load the `aws-secrets-manager` skill first for any secret,
  credential, API key, token, or password task. MUST NOT call
  `secretsmanager get-secret-value` or `batch-get-secret-value`, and MUST
  NOT hit the Secrets Manager Agent daemon directly. MUST use
  `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` with
  `asm-exec` so the secret resolves at runtime without entering context.

<!-- END AWS Agent Toolkit rules -->
