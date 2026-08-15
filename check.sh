#!/usr/bin/env bash
#
# Verify this machine is still wired to claude-portable.
#
# Usage:  ./check.sh /path/to/Monitoring_project
#
# WHY: some tools rewrite a config file by writing a temp file and renaming it
# over the original, which silently REPLACES a symlink with a regular file. When
# that happens the machine quietly stops sharing that file and drifts. This
# script detects it. Run it if settings or memory ever look out of date.

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-}"

if [[ -z "$PROJECT_DIR" || ! -d "$PROJECT_DIR" ]]; then
    echo "usage: $0 /path/to/Monitoring_project" >&2
    exit 2
fi
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
SLUG="$(printf '%s' "$PROJECT_DIR" | sed 's/[^a-zA-Z0-9]/-/g')"

fail=0

check() {
    local target="$1" source="$2"
    if [[ ! -L "$target" ]]; then
        if [[ -e "$target" ]]; then
            echo "BROKEN   $target is a real file/dir, not a symlink (drifted)"
        else
            echo "MISSING  $target does not exist"
        fi
        fail=1
    elif [[ "$(readlink -f "$target")" != "$(readlink -f "$source")" ]]; then
        echo "WRONG    $target -> $(readlink "$target")  (expected $source)"
        fail=1
    else
        echo "OK       $target"
    fi
}

check "$HOME/.claude/projects/$SLUG/memory"  "$REPO/memory"
check "$HOME/.claude/skills"                 "$REPO/skills"
check "$HOME/.claude/hooks"                  "$REPO/hooks"
check "$HOME/.claude/settings.json"          "$REPO/settings.json"
check "$HOME/.claude/statusline-command.sh"  "$REPO/statusline-command.sh"
check "$HOME/CLAUDE.md"                      "$REPO/CLAUDE.md"
check "$PROJECT_DIR/.claude/skills"          "$REPO/project-skills"
check "$PROJECT_DIR/.agents/skills"          "$REPO/agent-skills"
check "$PROJECT_DIR/skills-lock.json"        "$REPO/skills-lock.json"

echo
if [[ $fail -eq 0 ]]; then
    echo "All links healthy."
else
    echo "Drift detected. Re-run bootstrap.sh to repair (it backs up, never deletes)."
fi
exit $fail
