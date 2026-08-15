---
name: feedback-sudo-command-style
description: "When asking user to run sudo commands, give bare terminal commands broken into discrete steps — not chained one-liners and not the chat's `!` prefix"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

When you need the user to run a sudo command (because you can't run sudo yourself in this environment):

1. **Do NOT use the `!` chat prefix.** The chat shell can't read an interactive password prompt, so `!sudo ...` fails for them.
2. **Give a bare terminal command** the user copy-pastes into their own terminal outside the chat. They run it, then paste the output back.
3. **Prefer one command per step.** Chained `cmd1 && cmd2 && cmd3` workflows hide partial-success diagnosis — when something fails, the user gets an opaque mid-pipeline error and isn't sure which step failed or what state they're in. Better to walk one step at a time, ask for the output, then send the next step.
4. **State the expected output** for each step ("should print `X`", or "should be empty"), so it's obvious to the user whether the step succeeded.
5. Chained commands are acceptable ONLY when the steps are atomic (e.g., `cp /tmp/x /etc/y && systemctl reload z`) AND the failure mode of each is unambiguous from the combined output.

**Why:** User explicitly said: "i cannot run sudo commands with ! in this chat cause I don't get the interactive bash for the password" + "i think the commands are wrong, or doing everything in one line doesn't work well" (2026-05-21 Phase 0 Netdata install).

**How to apply:** Any time a tool wants sudo, or a procedure has 3+ sequential ops involving root-owned files / services — break it into a numbered list of single commands with expected outputs. Wait for output between steps when each one's outcome materially changes the next.
