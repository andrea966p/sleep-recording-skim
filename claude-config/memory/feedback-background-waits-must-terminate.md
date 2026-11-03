---
name: feedback-background-waits-must-terminate
description: "Andrea 2026-10-02, again 2026-11-03 (6 h lost overnight): my background wait loops keep hanging (seen often). Every wait must have a deadline, must not match its own command line, must watch an explicit target, and must be stopped once its purpose is served."
metadata:
  type: feedback
---

Andrea, 2026-10-02: two of my background tasks ("Block until recording script exits", "Wait for recording to start") had hung for
~20 h, and "this happens often". **Take care of it.**

**Why they hung (both my design errors):**
- `until ! pgrep -f rec5.py` — `pgrep -f` matches the loop's OWN command line, which contains "rec5.py", so it never ends.
  (Same trap noted 2026-08-21 in [[raw-data-archive-and-recording-automation]] and again with the Allego exit watcher on 10-02.)
- `F=$(ls -t tasks/*.output | head -1); until grep -q started $F` — picked "the newest output file" at launch, i.e. most likely
  ITS OWN, so it waited for text that could never appear.

**How to apply, every time:**
1. **Hard deadline on every wait**: `timeout 900 bash -c '...'` or a counter (`for i in $(seq 1 180)`), and print a line on timeout.
2. **Never `pgrep -f <name>`** in a loop whose own command line contains `<name>`. Use the bracket trick (`pgrep -f "[r]ec5.py"`),
   a PID captured at launch (`while kill -0 $PID`), or a file the target writes.
3. **Watch an explicit target** (the exact task output path / file name), never "the newest file".
4. **Stop helpers when done** (TaskStop) and, before ending a turn that started background helpers, check none is left running
   (`ps -eo pid,etime,args | grep -E "until |sleep"`), leaving only intentional ones (e.g. a RAM watcher with its own end time).

5. **Same for `pkill -f`**: a `pkill -f <pat>` inside a command whose own line contains `<pat>` kills that shell (exit 144). Kill by PID.
6. **Prefer no wait loop at all**: chain steps with `&&` in ONE background command (`a && b && c`), so the harness notifies on exit.

**2026-11-03 repeat, unattended overnight run:** `while pgrep -f 'score.py /home'` hung ~6 h after scoring had finished;
no deadline. Andrea: "wasted 6h ... this should never happen." Before leaving any unattended chain, re-read this rule.

## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🛑 **[BACKGROUND WAITS MUST TERMINATE](feedback-background-waits-must-terminate.md)** (Andrea 10-02: they hang often). Deadline on every loop, no `pgrep -f` that matches itself (use `[r]ec5.py` or a PID), explicit target file, TaskStop when done.
