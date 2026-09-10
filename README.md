# Sleep Recording SKIM

One repository holding the whole working environment for the mouse sleep recording
project: the Obsidian vault, the recording software, the EEG analysis code, and the
Claude Code configuration and memory.

Work on any Ubuntu machine. Pull before you start, push when you stop.

```bash
./skim status          # am I behind? what have I not committed?
./skim pull            # get everyone else's work
./skim push "message"  # commit everything and push
./skim check           # are the Claude Code links intact, is Syncthing really gone
```

**Nothing syncs by itself.** No hook commits, no timer pushes. `skim status` is
read-only and may be called automatically; every verb that writes is typed by a human.

## What is in here

| Directory | What it is |
|---|---|
| `vault/` | The Obsidian vault. Open THIS directory in Obsidian, no other copy. |
| `neurosurveillance/` | Session daemon, Frigate control, React/Tauri frontend. |
| `neurosurveillance-system/` | Older system configuration repo. |
| `eeg-emg-analysis/` | EEG/EMG quality control, criteria engine, per-animal cards. |
| `claude-config/` | Claude Code memory, skills, hooks, CLAUDE.md, settings template. |
| `machine/` | Per-machine setup: `bootstrap.sh`, `check.sh`, systemd unit copies. |

Each of the first four arrived through `git subtree`, so their full histories are in
this repository's log. The standalone repositories they came from are archived.

## A new machine

```bash
git clone git@github.com:andrea966p/sleep-recording-skim.git ~/sleep-recording-skim
cd ~/sleep-recording-skim && ./machine/bootstrap.sh && ./skim check
```

Then open `~/sleep-recording-skim/vault` in Obsidian. See `machine/README.md` for what
each machine needs installed and what stays machine-local.

## The rig only exists on e10ubuntu

Allego, radiens, XDAQ, Docker, Frigate and `~/radix/data` are physically on
`e10ubuntu`. From any other machine, drive them over SSH:

```bash
ssh e10 'docker ps'
ssh e10 -t 'tmux new -As rig'    # anything long running
```

## Two rules that exist because of real damage

1. **Never let a second sync mechanism touch this directory.** Syncthing plus git on
   one folder, with a live `.git` replicated and no versioning, destroyed the vault on
   2026-04-29. Syncthing is retired for this workspace; `./skim check` verifies it.
2. **Never put a runtime-rewritten file in the repo.** Claude Code rewrites
   `settings.json`, which kept the old shared repo permanently dirty, made `git rebase`
   refuse to run, and deadlocked memory sync for 19 days. `settings.json` is copied
   into place by `bootstrap.sh` and is gitignored here.
