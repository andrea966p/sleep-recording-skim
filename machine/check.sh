#!/usr/bin/env bash
#
# Verify this machine is still wired to the Sleep Recording SKIM workspace.
#
# Usage:  ./machine/check.sh
#
# WHY: some tools rewrite a config file by writing a temp file and renaming it
# over the original, which silently REPLACES a symlink with a regular file. When
# that happens the machine quietly stops sharing that file and drifts. This
# script detects it.

set -uo pipefail

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$WORKSPACE/claude-config"
SLUG="$(printf '%s' "$WORKSPACE" | sed 's/[^a-zA-Z0-9]/-/g')"

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

check "$HOME/.claude/projects/$SLUG/memory"  "$CONFIG/memory"
check "$HOME/.claude/skills"                 "$CONFIG/skills"
check "$HOME/.claude/hooks"                  "$CONFIG/hooks"
check "$HOME/.claude/statusline-command.sh"  "$CONFIG/statusline-command.sh"
check "$HOME/CLAUDE.md"                      "$CONFIG/CLAUDE.md"
check "$WORKSPACE/.claude/skills"            "$CONFIG/project-skills"
check "$WORKSPACE/.agents/skills"            "$CONFIG/agent-skills"
check "$WORKSPACE/skills-lock.json"          "$CONFIG/skills-lock.json"

# settings.json is a COPY on purpose, so a symlink here is the fault, not a pass.
LIVE="$HOME/.claude/settings.json"
if [[ -L "$LIVE" ]]; then
    echo "BROKEN   $LIVE is a symlink into the repo - that is what caused the 2026"
    echo "         sync deadlock. Re-run bootstrap.sh to convert it to a copy."
    fail=1
elif [[ -f "$LIVE" ]]; then
    echo "OK       $LIVE (real file, correct)"
else
    echo "MISSING  $LIVE"
    fail=1
fi

echo
if [[ $fail -eq 0 ]]; then
    echo "All links healthy."
else
    echo "Drift detected. Re-run machine/bootstrap.sh to repair (it backs up, never deletes)."
fi
exit $fail
