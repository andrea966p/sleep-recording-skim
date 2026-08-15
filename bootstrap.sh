#!/usr/bin/env bash
#
# Wire this machine's Claude Code installation to the shared claude-portable repo.
#
# Usage:  ./bootstrap.sh /path/to/Monitoring_project
#
# WHAT IT DOES
#   Replaces a handful of per-machine Claude Code paths with symlinks into this
#   repo, so every machine shares one copy of the memory, skills, hooks and
#   settings. Claude Code keys its per-project memory directory on a slug derived
#   from the project's absolute path, so the slug differs between machines
#   (different usernames). Symlinking each machine's OWN slug directory at the
#   same shared memory/ is what makes that difference stop mattering.
#
# SAFETY
#   This script NEVER deletes. Anything already at a target path is MOVED to
#   <target>.pre-bootstrap. If such a backup already exists, the script aborts
#   rather than overwrite it. Run it again after resolving the conflict.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-}"

if [[ -z "$PROJECT_DIR" ]]; then
    echo "usage: $0 /path/to/Monitoring_project" >&2
    exit 2
fi
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "ERROR: project dir does not exist: $PROJECT_DIR" >&2
    exit 2
fi
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

# Claude Code's project slug: absolute path with every non-alphanumeric char
# turned into a dash. /home/skimlab/Monitoring_project -> -home-skimlab-Monitoring-project
SLUG="$(printf '%s' "$PROJECT_DIR" | sed 's/[^a-zA-Z0-9]/-/g')"

echo "repo:        $REPO"
echo "project dir: $PROJECT_DIR"
echo "slug:        $SLUG"
echo

link() {
    local target="$1" source="$2"

    if [[ ! -e "$source" ]]; then
        echo "SKIP  $target  (no $source in repo)"
        return 0
    fi

    # Already correctly linked: nothing to do.
    if [[ -L "$target" && "$(readlink -f "$target")" == "$(readlink -f "$source")" ]]; then
        echo "OK    $target -> $source"
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

link "$HOME/.claude/projects/$SLUG/memory"  "$REPO/memory"
link "$HOME/.claude/skills"                 "$REPO/skills"
link "$HOME/.claude/hooks"                  "$REPO/hooks"
link "$HOME/.claude/settings.json"          "$REPO/settings.json"
link "$HOME/.claude/statusline-command.sh"  "$REPO/statusline-command.sh"
link "$HOME/CLAUDE.md"                      "$REPO/CLAUDE.md"
link "$PROJECT_DIR/.claude/skills"          "$REPO/project-skills"
link "$PROJECT_DIR/.agents/skills"          "$REPO/agent-skills"
link "$PROJECT_DIR/skills-lock.json"        "$REPO/skills-lock.json"

echo
echo "Done. Verify with: $REPO/check.sh $PROJECT_DIR"
