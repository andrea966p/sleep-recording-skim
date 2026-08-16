#!/usr/bin/env bash
#
# Commit and push the shared Claude Code config repo (memory, skills, hooks).
#
# WHY THIS EXISTS
#   Every machine holds its own clone of claude-portable, so memory written on
#   one machine is invisible to the others until someone commits, pushes and
#   pulls. That gap is silent and it has already bitten us: e10ubuntu held a
#   stale sync baseline for nine hours on 2026-08-16.
#
#   This runs from a SessionEnd hook, so it happens once per Claude Code
#   session rather than on a timer. Unlike the vault, git here lives on EVERY
#   machine, so two machines can race. Everything below is about surviving that
#   race without ever leaving the repo in a broken state.
#
# SAFETY
#   - Never deletes, never force-pushes, never resets.
#   - flock serialises runs; a second run skips rather than fighting the first.
#   - On rebase conflict it ABORTS the rebase, restores the pre-run state and
#     exits non-zero. It never leaves a half-finished rebase behind.
#   - settings.json is NEVER auto-committed. Claude Code rewrites that file at
#     runtime (e.g. flipping "model"), and it is shared, so an unattended commit
#     would silently change the model on every other machine.
#   - Network calls are wrapped in `timeout` so a dead network cannot hang the
#     end of a session.
#
# USAGE
#   sync.sh          commit tracked changes (except settings.json), pull, push
#   sync.sh --status what would happen, changes nothing
#
# Vault doc: 01-infrastructure/multi-machine-work-setup.md

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="main"
REMOTE="origin"
LOCKFILE="${XDG_CACHE_HOME:-$HOME/.cache}/claude-portable-sync.lock"
LOGFILE="${XDG_CACHE_HOME:-$HOME/.cache}/claude-portable-sync.log"
NET_TIMEOUT=25

# Paths that may be auto-committed. settings.json is deliberately absent.
PATHSPEC=(
    'memory'
    'skills'
    'hooks'
    'project-skills'
    'agent-skills'
    'CLAUDE.md'
    'skills-lock.json'
    'statusline-command.sh'
    'sync.sh'
    'bootstrap.sh'
    'check.sh'
    'README.md'
)

mkdir -p "$(dirname "$LOGFILE")"
log() { printf '[claude-portable-sync %s] %s\n' "$(date '+%F %T')" "$*" >>"$LOGFILE"; }
say() { printf '%s\n' "$*"; }

cd "$REPO" || { say "ERROR: cannot cd to $REPO"; exit 1; }

if [[ "${1:-}" == "--status" ]]; then
    say "repo:    $REPO"
    say "branch:  $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
    say "log:     $LOGFILE"
    say ""
    say "would commit:"
    for p in "${PATHSPEC[@]}"; do [[ -e "$p" ]] && git status --porcelain -- "$p"; done | sed 's/^/  /'
    say ""
    say "held back (never auto-committed):"
    git status --porcelain -- settings.json | sed 's/^/  /' || true
    exit 0
fi

# Serialise. If another run holds the lock, this session's changes will be
# picked up by that run or the next one, so skipping is safe.
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    log "another run holds the lock, skipping"
    exit 0
fi

if [[ ! -d "$REPO/.git" ]]; then
    log "ERROR: $REPO is not a git repository"
    say "ERROR: $REPO is not a git repository"
    exit 1
fi

# A detached HEAD or a feature branch is not ours to push. Bail out loudly.
current="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [[ "$current" != "$BRANCH" ]]; then
    log "on branch '$current', not '$BRANCH' — doing nothing"
    say "claude-portable: on branch '$current', not '$BRANCH'. Nothing done."
    exit 0
fi

# Git identity is per machine and is easy to forget on a new one.
if ! git config user.email >/dev/null; then
    log "ERROR: git user.email is not set in $REPO"
    say "claude-portable: git identity not set. Run:"
    say "  git -C $REPO config user.name  'your name'"
    say "  git -C $REPO config user.email 'your@email'"
    exit 1
fi

# Remember where we started so a failed rebase can be undone exactly.
start_commit="$(git rev-parse HEAD)"

# `git add` aborts on a pathspec that matches nothing, which would silently skip
# the whole commit if any entry above is ever removed from the repo. Narrow the
# list to what actually exists so one missing path cannot stop the sync.
EXISTING=()
for p in "${PATHSPEC[@]}"; do
    [[ -e "$p" ]] && EXISTING+=("$p")
done
if [[ ${#EXISTING[@]} -eq 0 ]]; then
    log "ERROR: none of the tracked paths exist in $REPO"
    say "claude-portable: none of the tracked paths exist in $REPO. Nothing done."
    exit 1
fi

# 1. Commit local work, if any. Only the allowed paths.
if [[ -n "$(git status --porcelain -- "${EXISTING[@]}")" ]]; then
    if ! git add -- "${EXISTING[@]}" 2>>"$LOGFILE"; then
        log "ERROR: git add failed, nothing committed"
        say "claude-portable: git add failed, nothing committed. See $LOGFILE"
        exit 1
    fi
    host="$(hostname -s 2>/dev/null || hostname)"
    if git commit -q -m "sync from ${host}: $(date '+%F %T')" \
        -m "Automatic commit from the Claude Code SessionEnd hook (sync.sh)."; then
        log "committed local changes on $host"
    else
        log "nothing staged after add, continuing"
    fi
else
    log "no local changes to commit"
fi

held="$(git status --porcelain -- settings.json)"
[[ -n "$held" ]] && log "settings.json modified but held back: $held"

# 2. Fetch. If the network is down there is nothing more to do, and that is fine
#    — the commit above is safe locally and the next session will push it.
if ! timeout "$NET_TIMEOUT" git fetch -q "$REMOTE" "$BRANCH" 2>>"$LOGFILE"; then
    log "fetch failed or timed out, leaving local commits for the next run"
    say "claude-portable: fetch failed, changes committed locally but not pushed."
    exit 0
fi

# 3. Rebase onto the remote only if we are actually behind.
behind="$(git rev-list --count HEAD.."$REMOTE/$BRANCH" 2>/dev/null || echo 0)"
if [[ "$behind" -gt 0 ]]; then
    if ! git rebase -q "$REMOTE/$BRANCH" 2>>"$LOGFILE"; then
        git rebase --abort 2>/dev/null
        # --abort restores HEAD, but be certain we are exactly where we started.
        if [[ "$(git rev-parse HEAD)" != "$start_commit" ]]; then
            log "WARNING: HEAD moved despite rebase --abort (was $start_commit, now $(git rev-parse HEAD))"
        fi
        log "REBASE CONFLICT against $REMOTE/$BRANCH — aborted, nothing pushed"
        say "claude-portable: CONFLICT with $REMOTE/$BRANCH. Rebase aborted, nothing pushed."
        say "  Resolve by hand:  cd $REPO && git pull --rebase"
        exit 1
    fi
    log "rebased onto $REMOTE/$BRANCH ($behind commit(s))"
fi

# 4. Push only if we have something the remote does not.
ahead="$(git rev-list --count "$REMOTE/$BRANCH"..HEAD 2>/dev/null || echo 0)"
if [[ "$ahead" -eq 0 ]]; then
    log "nothing to push, up to date"
    exit 0
fi

if timeout "$NET_TIMEOUT" git push -q "$REMOTE" "$BRANCH" 2>>"$LOGFILE"; then
    log "pushed $ahead commit(s) to $REMOTE/$BRANCH"
else
    log "push failed, $ahead commit(s) still local"
    say "claude-portable: push failed, $ahead commit(s) committed locally but not pushed."
    exit 1
fi
