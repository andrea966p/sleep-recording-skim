---
tags: [procedure, eeg, xdat, allego, storage, data-management, analysis]
created: 2026-09-11
status: active
---

# Stripping an XDAT recording down to the channels that were actually wired

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The recording hardware saves every input it has, whether or not anything is
> plugged into it. For eight mice with two electrodes each, that means 16 useful channels out of 262
> — about 94% of every file is a recording of nothing. This tool writes a second copy containing
> only the channels that were really connected, and proves the copy is identical to the original
> before anyone relies on it.
>
> **Why it exists.** A day of recording is 90 GB. Almost all of it is empty. Keeping only what was
> wired makes it possible to store recordings off the rig, back them up, and hand them to a
> collaborator at all.
>
> **How to read this page.** Section 1 is how to run it. Section 2 is the one thing you give up by
> stripping, which is scientific rather than technical and matters more than anything else here.
> Section 3 is for anyone modifying the tool. Background: [[01-infrastructure/system-overview]].

## 1. Running it

    cd ~/sleep-recording-skim/eeg-emg-analysis
    PYTHONPATH=. /opt/neurosurveillance/venv/bin/python3 -m convert.strip_channels \
        <recording-base-name> --keep-selected --dry-run

`--dry-run` writes nothing and prints the channel table, the sizes, and whether a QC bundle exists.
**Read it before dropping `--dry-run`.**

Selection is one of:

| flag | use |
|---|---|
| `--keep-selected` | keep whatever the file's own `is_selected` flags name. Good default |
| `--keep-labels A/1,A/2,A/33,…` | name the sites explicitly. **What the console uses** |
| `--keep-index 0,1,32,…` | raw file indices. Validated hard; see the warning below |
| `--with-gpio` | additionally keep all six aux/din/dout channels |

Output goes to `{STRIPPED_ROOT}` — a **sibling** of `{RAW_ROOT}`, never inside it, so stripped twins
stay out of `radix-archive.sh`'s `ls -1 "$SRC"` and out of every pipeline glob.

Typical result: **262 channels → 16, a 93.2% reduction.** A 75 GB twenty-hour run becomes ~5.8 GB.

> [!danger] A KEEP LIST WRITTEN AS INDICES IS NOT PORTABLE BETWEEN RECORDINGS ON THIS RIG
> `allego_0__uid0904-08-55-25` has **134 channels**, ports of 32, and uses sites `/18`–`/23`. The
> usual index list `[0,1,32,33,64,…,225]` applied to it would read **aux channels instead of
> electrodes** and run off the end of the file. Neither failure announces itself.
>
> **Always express a selection as site labels.** The tool resolves labels against each file's own
> `biointerface_map` and refuses on any miss. `--keep-index` is validated and refused rather than
> clamped, but `--keep-labels` is the form to use.

## 2. 🔴 What stripping costs you, permanently

> [!danger] STRIPPING DELETES THIS PROJECT'S ONLY MEASURE OF WHETHER A CHANNEL WAS CONNECTED
> `core/criteria.py` judges every channel against **wire-free amplifier inputs recorded in the same
> file** — sites `/3`–`/16` and `/35`–`/48` in a two-role cohort. Those are exactly the channels the
> strip removes. Afterwards `compute_features` exits with *"N expected sites are not in this file's
> biointerface_map"*.
>
> Demonstrated 2026-09-11: the original runs, the stripped copy refuses on 112 missing floor sites.
> This is intended behaviour and a good failure — it is loud rather than silent.

⇒ **The QC bundle is a precondition of stripping, not a follow-up.** Compute it first, and ship it
with the stripped copy:

    PYTHONPATH=. /opt/neurosurveillance/venv/bin/python3 cards/ladder.py <base> \
        --cohort <id> --cache {CACHE_ROOT}/<base>.npz

That `.npz` holds per-epoch measurements for every animal **and every floor site**, and is the only
surviving record of the floor. `--dry-run` prints `QC BUNDLE: MISSING` in capitals when there is
none, and `eeg-recorder`'s post-processing chain **refuses to strip without one** by default.

**The stripped file is a convenience copy. The original plus its QC bundle is the record of truth.
Nothing here ever deletes an original** — that is a human decision, taken after reading the manifest.

> [!quote] Paper-ready
> Recordings are stored in full and additionally retained as channel-reduced copies containing only
> the electrode sites in use. Each reduced copy is verified bit-exact against its source across
> every retained channel before use, and carries in its metadata the identity of the source file,
> its checksum, and the original index of every retained channel, so that the reduction is fully
> reversible in interpretation. Because the quality-control criterion for this rig is defined
> against unconnected amplifier inputs recorded in the same file, per-epoch quality measurements are
> computed on the complete recording and archived alongside the reduced copy.

## 3. The sidecar contract, for anyone modifying the tool

Three files per recording: `<base>_data.xdat` (float32, interleaved, µV),
`<base>_timestamp.xdat` (int64, one per sample), `<base>.xdat.json`.

**Measured facts the tool depends on** (all verified 2026-09-11, not assumed):

- **`status.dataset_checksum` is exactly `sha256(data_file ‖ timestamp_file)`.** Verified
  byte-for-byte on two recordings; the reverse order does not match. So it can be recomputed
  correctly rather than left stale.
- `biointerface_map` has 36 keys, **35 of them per-channel arrays** plus the scalar `samp_freq`. The
  count is **discovered, never asserted**, so a future release that adds one is carried rather than
  silently dropped.
- `neighborhoods.site_hood` is keyed by `str(ntv_chan_idx)` of **primary channels only**.
- `sigUnits`, `sensors_by_port`, `sig_proc_spec`, `zcheck_spec`, `port_map`, `digital_out_spec`
  carry **no** per-channel arrays. `sig_proc_spec` is **absent** from some files, so nothing may
  require it.

> [!danger] RENUMBER EXACTLY TWO FIELDS, AND PRESERVE THE REST
> `sys_chan_idx` and `absolute_idx` **address a row of the data record**. Left unchanged in a
> 16-channel file they would claim a channel lives at row 225 of a 16-row record, and any reader
> that seeks by them returns **another channel's bytes**. They are renumbered to `range(k)`.
>
> `ntv_chan_idx`, `ntv_chan_name`, `chan_name`, `port`, `site_num`, `is_selected`, `headstage_id`,
> `probe_id` and all geometry are **identity** and are preserved verbatim. `open_xdat` builds labels
> from `port` + `site_num` alone; renumbering `site_num` would relabel `A/33` as `A/3` and make every
> `CohortSpec` lookup **silently resolve to the wrong mouse**.
>
> The original values are written into `status.dataset_provenance` as `kept_orig_sys_chan_idx`, so
> the renumbering is reversible.

**The gates.** `strip()` raises rather than returning a failure; there is no path that prints success
without gate A passing.

| gate | check |
|---|---|
| A | **bit-exactness** — every kept column compared to the original on the raw `uint32` view (not a tolerance, so NaN and −0.0 cannot slip through), over the whole file by default |
| B | **dropped-`din` evidence** — refuses if a dropped digital input was **not constant**. `din` is where a camera/TTL sync arrives; discarding a live one is unrecoverable |
| C | `file_integrity()` on the output is `INTACT` with the right channel count |
| D | `open_xdat()` returns exactly the expected labels, unchanged `fs` and sample count |
| E | optional Radiens parse probe — **currently unprovable, see below** |

Failure renames the output to `<dst>.REJECTED.<utc>.*` so it can never be mistaken for good data.

> [!info] Gate B applies to `din` only, and that is a correction
> The design originally refused on **any** non-constant dropped GPIO channel. Measurement showed
> that would refuse *every* strip: `aux_1` has 232 distinct values (it is an analog sensor, wandering
> is its normal state) and `dout_2` toggles. Only `din` — a digital input we do not drive — is
> evidence of an external signal worth protecting. `aux` and `dout` are recorded in the report as
> notes.

> [!warning] GATE E IS UNPROVEN ON THIS HOST
> Whether the Radiens reader accepts a stripped file whose `sensors_by_port[port].num_channels`
> still says 64 **cannot be answered here**: `FileSystemClient` needs a Videre hub, and there is no
> Videre binary under `/opt/allego` — only `videre_man.md`. The probe therefore **skips** and records
> the question as open rather than implying a pass. Our own reader (`open_xdat`, gate D) is
> unaffected and does accept it.

## 4. Other properties worth knowing

- **Resumable.** A killed run leaves a `.part`; the next run truncates any torn partial row, re-hashes
  the prefix, and continues. Verified byte-identical to an unresumed run.
- **Idempotent.** A complete, verified output is detected and skipped.
- **Bounded memory.** ~186 MB peak regardless of file size. ⚠️ An earlier version used `np.memmap`
  and reached **9.26 GB peak RSS on a 5.26 GB file** — every touched page is resident. Chunked
  `np.fromfile(offset=)` is both smaller and faster. **Do not reintroduce a whole-file memmap.**
- **`--require-idle`** refuses while a data file under `{RAW_ROOT}` has been touched in the last
  120 s. ⚠️ It deliberately does **not** consult `status.is_live_recording`: a recording that ends
  abnormally never has its sidecar rewritten, so that flag stays `true` forever
  (`allego_0__uid0829-08-34-39` still claims to be live ten days on). The flag is reported separately
  as a **crash marker**.

## 5. Tests

`eeg-emg-analysis/tests/test_strip_channels.py` — 27 checks, **15 of them refusals**, including a
negative control that corrupts one byte of the output and requires the bit-exactness gate to reject
it. Run as a script, not under pytest:

    PYTHONPATH=. ~/eeg-test-venv/bin/python3 tests/test_strip_channels.py

## 6. Related

- [[02-procedures/installation/skim-nas-smb-and-upload]] — where stripped copies go
- [[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] — the QC bundle this depends on
- [[02-procedures/CANONICAL-allego-channel-selection]] — which sites are the wired ones
