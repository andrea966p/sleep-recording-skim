# claude-config

Claude Code's shared brain for this workspace: memory, skills, hooks, `CLAUDE.md`,
the status line, and a settings template.

Wire a machine to it with `../machine/bootstrap.sh`, verify with `../machine/check.sh`.

## settings.json is NOT here, on purpose

`settings.template.json` is copied to `~/.claude/settings.json` by `bootstrap.sh`. The
live file is gitignored and never comes back into the repo.

Claude Code rewrites `settings.json` while it runs: it has flipped `"model"` by itself,
and it writes an `autoMode.environment` block full of machine-specific absolute paths.
When that file lived inside the shared repo, the working tree was permanently dirty,
`git rebase` refused to start, and the old sync script could neither push nor pull. That
went unnoticed from 2026-08-22 to 2026-09-10: 19 days during which every session on the
second machine read three-week-old memory.

## What replaced sync.sh

`sync.sh`, `bootstrap.sh` and `check.sh` came from the old `claude-portable` repo and were
deleted when it was absorbed here. Nothing commits or pushes automatically any more.
Use `../skim` by hand.
