#!/usr/bin/env bash
#
# Wire this machine's Claude Code installation to the Sleep Recording SKIM workspace.
#
# Usage:  ./machine/bootstrap.sh            (from anywhere inside the workspace)
#
# WHAT IT DOES
#   Replaces a handful of per-machine Claude Code paths with symlinks into
#   claude-config/, so every machine shares one copy of the memory, skills and
#   hooks. Claude Code keys its per-project memory directory on a slug derived
#   from the workspace's ABSOLUTE PATH, so the slug differs between machines with
#   different usernames (-home-skimlab-sleep-recording-skim on e10ubuntu,
#   -home-andrea-sleep-recording-skim on the ThinkPad). Symlinking each machine's
#   OWN slug directory at the one shared memory/ is what makes that difference
#   stop mattering.
#
#   settings.json is the exception and is deliberately COPIED, never symlinked.
#   Claude Code rewrites that file at runtime (it has flipped "model" by itself,
#   and it writes machine-specific absolute paths into it). A runtime-rewritten
#   file inside the repo keeps the working tree permanently dirty, which makes
#   `git rebase` refuse to run - that is precisely how the old claude-portable
#   sync deadlocked for 19 days in 2026. Copying breaks that link for good.
#
# SAFETY
#   This script NEVER deletes. Anything already at a target path is MOVED to
#   <target>.pre-bootstrap. If such a backup already exists it aborts rather than
#   overwrite it.

set -euo pipefail

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$WORKSPACE/claude-config"

if [[ ! -d "$CONFIG" ]]; then
    echo "ERROR: no claude-config/ in $WORKSPACE" >&2
    exit 2
fi

# Claude Code derives the slug from the NATIVE path. Under Git Bash on Windows that is
# C:\Users\..., not /c/Users/..., so convert first (cygpath exists only there).
NATIVE="$WORKSPACE"
command -v cygpath >/dev/null 2>&1 && NATIVE="$(cygpath -w "$WORKSPACE")"
SLUG="$(printf '%s' "$NATIVE" | sed 's/[^a-zA-Z0-9]/-/g')"

# Git Bash's ln -s silently makes a COPY unless told otherwise, which would leave this
# machine with its own private memory/. nativestrict makes it fail instead.
command -v cygpath >/dev/null 2>&1 && export MSYS=winsymlinks:nativestrict

echo "workspace: $WORKSPACE"
echo "slug:      $SLUG"
echo

link() {
    local target="$1" source="$2"

    if [[ ! -e "$source" ]]; then
        echo "SKIP  $target  (no $source in repo)"
        return 0
    fi
    if [[ -L "$target" && "$(readlink -f "$target")" == "$(readlink -f "$source")" ]]; then
        echo "OK    $target"
        return 0
    fi

    mkdir -p "$(dirname "$target")"

    if [[ -e "$target" || -L "$target" ]]; then
        if [[ -e "$target.pre-bootstrap" ]]; then
            echo "ABORT $target: a backup already exists at $target.pre-bootstrap" >&2
            echo "      Resolve it by hand, then re-run. Nothing was deleted." >&2
            exit 1
        fi
        mv "$target" "$target.pre-bootstrap"
        echo "SAVED $target -> $target.pre-bootstrap"
    fi

    ln -s "$source" "$target"
    echo "LINK  $target -> $source"
}

link "$HOME/.claude/projects/$SLUG/memory"  "$CONFIG/memory"
link "$HOME/.claude/skills"                 "$CONFIG/skills"
link "$HOME/.claude/hooks"                  "$CONFIG/hooks"
link "$HOME/.claude/statusline-command.sh"  "$CONFIG/statusline-command.sh"
link "$HOME/CLAUDE.md"                      "$CONFIG/CLAUDE.md"
link "$WORKSPACE/.claude/skills"            "$CONFIG/project-skills"
link "$WORKSPACE/.agents/skills"            "$CONFIG/agent-skills"
link "$WORKSPACE/skills-lock.json"          "$CONFIG/skills-lock.json"

# settings.json: copy, never link. See the header.
TEMPLATE="$CONFIG/settings.template.json"
LIVE="$HOME/.claude/settings.json"
if [[ ! -f "$TEMPLATE" ]]; then
    echo "SKIP  $LIVE  (no settings.template.json in repo)"
elif [[ -L "$LIVE" ]]; then
    echo "FIX   $LIVE is a symlink from the old setup - replacing with a real copy"
    mv "$LIVE" "$LIVE.pre-bootstrap-symlink"
    cp "$TEMPLATE" "$LIVE"
    echo "COPY  $TEMPLATE -> $LIVE"
elif [[ ! -f "$LIVE" ]]; then
    mkdir -p "$(dirname "$LIVE")"
    cp "$TEMPLATE" "$LIVE"
    echo "COPY  $TEMPLATE -> $LIVE"
elif diff -q "$TEMPLATE" "$LIVE" >/dev/null 2>&1; then
    echo "OK    $LIVE matches the template"
else
    echo "KEPT  $LIVE differs from the template (machine-specific, as expected)"
    echo "      review with:  diff $TEMPLATE $LIVE"
fi

# settings.local.json: the per-project permission allow-list. Copied, never linked, for
# the same reason as settings.json - Claude Code appends to it every time you approve a
# new command, so a symlink into the repo would keep the tree permanently dirty.
LOCAL_TEMPLATE="$CONFIG/settings.local.template.json"
LOCAL_LIVE="$WORKSPACE/.claude/settings.local.json"
if [[ ! -f "$LOCAL_TEMPLATE" ]]; then
    echo "SKIP  $LOCAL_LIVE  (no settings.local.template.json in repo)"
elif [[ ! -f "$LOCAL_LIVE" ]]; then
    mkdir -p "$(dirname "$LOCAL_LIVE")"
    cp "$LOCAL_TEMPLATE" "$LOCAL_LIVE"
    echo "COPY  $LOCAL_TEMPLATE -> $LOCAL_LIVE"
else
    echo "KEPT  $LOCAL_LIVE (already present; merge by hand if the template has newer rules)"
fi


echo
echo "Done. Verify with: $WORKSPACE/machine/check.sh"
