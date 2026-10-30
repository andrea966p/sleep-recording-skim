# Claude Code plugins and skills — this workspace

Snapshot taken 2026-09-14 on `e10ubuntu` (`skimlab`), plugin section updated 2026-10-30.
Two separate systems, two separate install paths — don't conflate them.

## 1. Marketplace plugins (declared in git since 2026-10-30)

The checked-in `.claude/settings.json` lists the marketplaces (`extraKnownMarketplaces`)
and enables the six work plugins below for this repo (`enabledPlugins`). Claude Code
offers to install them on the first trusted session in the repo, so a new machine needs
no per-machine install step. The plugin files themselves still live in
`~/.claude/plugins/`, outside the repo; `machine/bootstrap.sh` does not touch them.

The same file turns off 20 unused science skills for this repo (`skillOverrides`).

| Plugin | Marketplace | Repo |
|---|---|---|
| `rust-analyzer-lsp` | `claude-plugins-official` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| `superpowers` | `claude-plugins-official` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| `caveman` | `caveman` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| `humanizer` | `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `ponytail` | `ponytail` | [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) |
| `agent-skills` | `addy-agent-skills` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) |

### Manual install (only if the first-session prompt was skipped)

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add JuliusBrussee/caveman
claude plugin marketplace add blader/humanizer
claude plugin marketplace add dietrichgebert/ponytail
claude plugin marketplace add addyosmani/agent-skills

claude plugin install rust-analyzer-lsp@claude-plugins-official
claude plugin install superpowers@claude-plugins-official
claude plugin install caveman@caveman
claude plugin install humanizer@humanizer
claude plugin install ponytail@ponytail
claude plugin install agent-skills@addy-agent-skills
```

Verify: `claude` then `/plugin` or ask Claude to list plugins — should show all 6 enabled.

Caveman mode is ON for this workspace. Its SessionStart and UserPromptSubmit hooks come
from the caveman plugin itself. `claude-config/settings.template.json` no longer copies
them into `~/.claude/settings.json` (they ran twice); a machine bootstrapped before
2026-10-30 should drop the `caveman-activate.js` and `caveman-mode-tracker.js` entries
from its own `~/.claude/settings.json`.

### Personal plugins

Plugins only one person uses stay in that user's own `~/.claude`, not in the checked-in
file. To keep one out of this repo, set it to `false` under `enabledPlugins` in the
gitignored `.claude/settings.local.json` on that machine. On `e10ubuntu`,
`savvy-progress@claude-kit` and `filetree@claude-code-filetree` are personal and stay on
by choice (2026-10-30).

## 2. Skills already synced via git (DO NOT reinstall separately)

Two skill sets live inside this repo and ride along with a normal clone + bootstrap —
no extra fetch needed:

- **Personal skills** — `claude-config/skills/` → symlinked to `~/.claude/skills`.
  3 skills: `find-skills`, `llm-council`, `monitoring-diagnostics`.
- **Project/agent skills** — `claude-config/project-skills/` and
  `claude-config/agent-skills/` → symlinked to `$WORKSPACE/.claude/skills` and
  `$WORKSPACE/.agents/skills`. 67 skills, tracked in `skills-lock.json` at the repo
  root, pulled from:
  - [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
  - [orchestra-research/ai-research-skills](https://github.com/orchestra-research/ai-research-skills)
  - [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
  - [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all)

### Install on another machine

```bash
git clone <this-repo-url> sleep-recording-skim
cd sleep-recording-skim
./machine/bootstrap.sh
./machine/check.sh
```

That's it — the skill files are already in git, `bootstrap.sh` just symlinks them
into place. If a skill ever needs to be refreshed from its upstream source, re-fetch
the path listed for it in `skills-lock.json` and update the hash; there's no
installer script for that yet, it's done by hand.

## 3. claude.ai account skills (no install needed, follow the account)

Enabled on the `andrea96p@kaist.ac.kr` account, so they show up automatically in any
session signed into that account — nothing to install per machine:

`import-memory`, `morning`, `learn`, `skill-creator`, `xlsx`, `pptx`, `pdf`.

If a second person needs these, they enable them on their own claude.ai account under
Settings → Capabilities/Skills; account skills aren't shareable via this repo.
