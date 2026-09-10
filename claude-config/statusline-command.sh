#!/bin/bash
# ClaudeCodeStatusLine by daniel3303
# https://github.com/daniel3303/ClaudeCodeStatusLine

input=$(cat)

# Colors
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
BOLD_BLUE='\033[1;34m'
BOLD_MAGENTA='\033[1;35m'
BOLD_CYAN='\033[1;36m'
BOLD_WHITE='\033[1;37m'

# Extract data from JSON input
model_name=$(echo "$input" | jq -r '.model.display_name // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')
used_percentage=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
vim_mode=$(echo "$input" | jq -r '.vim.mode // empty')
five_hour_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_day_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
session_name=$(echo "$input" | jq -r '.session_name // empty')

# Git branch
git_branch=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null \
        || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
fi

# Build the status line
output=""

# Session name (if set via /rename)
if [ -n "$session_name" ]; then
    output="${output}$(printf "${BOLD_CYAN}[%s]${RESET} " "$session_name")"
fi

# Model name
if [ -n "$model_name" ]; then
    output="${output}$(printf "${BOLD_MAGENTA}%s${RESET}" "$model_name")"
fi

# Current directory
if [ -n "$cwd" ]; then
    output="${output}$(printf " ${BOLD_BLUE}%s${RESET}" "$cwd")"
fi

# Git branch
if [ -n "$git_branch" ]; then
    output="${output}$(printf " ${BOLD_GREEN}(%s)${RESET}" "$git_branch")"
fi

# Context window usage
if [ -n "$used_percentage" ]; then
    used_int=$(printf '%.0f' "$used_percentage")
    if [ "$used_int" -ge 90 ]; then
        color="$BOLD_RED"
    elif [ "$used_int" -ge 75 ]; then
        color="$BOLD_YELLOW"
    else
        color="${DIM}${WHITE}"
    fi
    output="${output}$(printf " ${color}ctx:%d%%${RESET}" "$used_int")"
fi

# Rate limits
if [ -n "$five_hour_pct" ] || [ -n "$seven_day_pct" ]; then
    rate_str=""
    if [ -n "$five_hour_pct" ]; then
        rate_str="$(printf '5h:%.0f%%' "$five_hour_pct")"
    fi
    if [ -n "$seven_day_pct" ]; then
        [ -n "$rate_str" ] && rate_str="$rate_str "
        rate_str="${rate_str}$(printf '7d:%.0f%%' "$seven_day_pct")"
    fi
    output="${output}$(printf " ${DIM}${WHITE}[%s]${RESET}" "$rate_str")"
fi

# Vim mode
if [ -n "$vim_mode" ]; then
    if [ "$vim_mode" = "INSERT" ]; then
        output="${output}$(printf " ${BOLD_CYAN}[INSERT]${RESET}")"
    else
        output="${output}$(printf " ${BOLD_YELLOW}[NORMAL]${RESET}")"
    fi
fi

printf "%b" "$output"
