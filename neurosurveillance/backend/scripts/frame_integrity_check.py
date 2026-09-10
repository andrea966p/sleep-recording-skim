#!/usr/bin/env python3
"""Frame-integrity check for recorded Frigate segments.

WHY THIS EXISTS
---------------
The planned video-EEG alignment does not use any clock. The Raspberry Pi will
emit a hardware sync pulse from its frame-capture callback, so each pulse means
"frame N exists"; the XDAQ digitizes that pulse at sample S alongside the neural
data. Analysis then pairs frame N with sample S and fits a line, and the slope of
that line is the measured camera clock drift.

That scheme relies on exactly one assumption:

    every frame the Pi encodes must survive into the recorded segments,
    so that counting frames in the files reproduces the Pi's own frame numbering.

Frigate records with `-c:v copy`, so it never re-encodes and should preserve every
frame it receives. But frames can still be lost upstream, most plausibly on an RTSP
reconnect when a Pi wobbles. If frames are dropped, frame counting silently shifts
and the alignment is corrupted without any visible error.

This script answers that one question from the recorded files alone, with no extra
hardware. If it reports no drops, frame counting is sound and an in-frame LED marker
is unnecessary. If it reports drops, an LED (or a per-segment checksum in the sync
manifest) is required to detect and repair the breaks.

WHAT IT DOES NOT ANSWER
-----------------------
The effective-fps figure it prints compares the camera against the NVR wall clock.
That is a useful preview, but it is NOT the drift number that matters, which is the
camera against the XDAQ sample clock. Only the Wire 2 pulses can measure that.

USAGE
-----
Recording must have been ON for the window being analysed. Turn it on the way you
normally do, let it run, then point this at the window:

    python3 frame_integrity_check.py --camera pi_cam_3 --minutes 15

All file access goes through `docker exec frigate`, so no sudo is needed even
though the recordings are root-owned on the host.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

CONTAINER = "frigate"
RECORDINGS_ROOT = "/media/frigate/recordings"
FFPROBE = "/usr/lib/ffmpeg/7.0/bin/ffprobe"

# Frigate's record ffmpeg uses `-f segment -segment_time 10`, so a healthy
# segment holds exactly SEGMENT_SECONDS * fps frames.
SEGMENT_SECONDS = 10

# A PTS delta is treated as a gap when it exceeds the nominal frame interval by
# more than this factor. 1.5 catches a single dropped frame (delta 2x nominal)
# while tolerating ordinary encoder jitter.
GAP_FACTOR = 1.5


@dataclass
class Segment:
    """One 10-second recording segment on disk."""

    path: str
    start: datetime          # parsed from the directory + filename (UTC)
    packets: int = 0         # video packets == frames, since Frigate copies the stream
    duration: float = 0.0    # container duration in seconds
    gaps: list = field(default_factory=list)   # (pts_seconds, delta_frames)
    error: str = ""


def docker_exec(args: list[str]) -> str:
    """Run a command inside the Frigate container and return stdout."""
    result = subprocess.run(
        ["docker", "exec", CONTAINER, *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not result.stdout:
        raise RuntimeError(
            f"docker exec {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def list_segments(camera: str, since: datetime) -> list[Segment]:
    """Find every segment for `camera` starting at or after `since`.

    Frigate lays recordings out as recordings/YYYY-MM-DD/HH/{camera}/MM.SS.mp4,
    and those directories are UTC, not local time. The caller is expected to pass
    an aware UTC datetime.
    """
    segments: list[Segment] = []

    # Walk only the hour directories the window can touch, rather than listing the
    # whole retention tree, which can hold days of files.
    hour = since.replace(minute=0, second=0, microsecond=0)
    end = datetime.now(timezone.utc)
    while hour <= end:
        day_dir = hour.strftime("%Y-%m-%d")
        hour_dir = hour.strftime("%H")
        # `|| true` keeps a missing hour directory from looking like a failure:
        # gaps in the tree are normal whenever recording was off.
        listing = docker_exec(
            ["sh", "-c",
             f"ls {RECORDINGS_ROOT}/{day_dir}/{hour_dir}/{camera}/ 2>/dev/null || true"]
        )
        for name in listing.split():
            if not name.endswith(".mp4"):
                continue
            stem = name[:-4]                      # "MM.SS"
            try:
                minute, second = (int(part) for part in stem.split("."))
            except ValueError:
                continue
            start = hour.replace(minute=minute, second=second)
            if start >= since:
                segments.append(
                    Segment(
                        path=f"{RECORDINGS_ROOT}/{day_dir}/{hour_dir}/{camera}/{name}",
                        start=start,
                    )
                )
        hour += timedelta(hours=1)

    segments.sort(key=lambda s: s.start)
    return segments


def probe_counts(segment: Segment) -> None:
    """Fill in packet count and duration. One cheap ffprobe pass per segment."""
    raw = docker_exec(
        [
            FFPROBE, "-v", "error",
            "-select_streams", "v:0",
            "-count_packets",
            "-show_entries", "stream=nb_read_packets,duration",
            "-of", "json",
            segment.path,
        ]
    )
    try:
        streams = json.loads(raw).get("streams", [])
    except json.JSONDecodeError:
        segment.error = "unreadable (ffprobe returned no JSON)"
        return
    if not streams:
        segment.error = "no video stream"
        return
    segment.packets = int(streams[0].get("nb_read_packets", 0) or 0)
    segment.duration = float(streams[0].get("duration", 0.0) or 0.0)


def probe_gaps(segment: Segment, fps: float) -> None:
    """Scan packet timestamps for gaps, which indicate dropped frames.

    Only worth running on segments whose count already looks wrong, since it dumps
    every packet timestamp in the file.
    """
    raw = docker_exec(
        [
            FFPROBE, "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "packet=pts_time",
            "-of", "csv=p=0",
            segment.path,
        ]
    )
    times = []
    for line in raw.splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        try:
            times.append(float(line))
        except ValueError:
            continue

    nominal = 1.0 / fps
    for previous, current in zip(times, times[1:]):
        delta = current - previous
        if delta > nominal * GAP_FACTOR:
            segment.gaps.append((previous, delta / nominal))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether recorded segments contain every frame the Pi sent."
    )
    parser.add_argument("--camera", required=True, help="e.g. pi_cam_3")
    parser.add_argument(
        "--minutes", type=int, default=15,
        help="how far back to analyse (default 15)",
    )
    parser.add_argument(
        "--fps", type=float, default=15.0,
        help="nominal camera framerate (default 15)",
    )
    parser.add_argument(
        "--scan-all", action="store_true",
        help="scan packet timestamps in every segment, not just suspect ones",
    )
    args = parser.parse_args()

    expected_per_segment = int(round(SEGMENT_SECONDS * args.fps))
    since = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)

    print(f"Camera            : {args.camera}")
    print(f"Window            : last {args.minutes} min (since {since:%Y-%m-%d %H:%M:%S} UTC)")
    print(f"Nominal framerate : {args.fps} fps -> {expected_per_segment} frames per {SEGMENT_SECONDS}s segment")
    print()

    segments = list_segments(args.camera, since)
    if not segments:
        print("NO SEGMENTS FOUND.")
        print("Recording was almost certainly OFF for this window. Turn it on, let it")
        print("run for the analysis period, then re-run.")
        return 2

    for segment in segments:
        probe_counts(segment)

    # A short final segment is normal: it is still being written. Exclude it from
    # the count analysis so it does not masquerade as a drop.
    complete = [s for s in segments if not s.error][:-1]
    if not complete:
        print("Only one segment found; need at least two. Increase --minutes.")
        return 2

    suspects = [s for s in complete if s.packets != expected_per_segment]
    to_scan = complete if args.scan_all else suspects
    for segment in to_scan:
        probe_gaps(segment, args.fps)

    total_frames = sum(s.packets for s in complete)
    # Wall span runs from the first segment start to the end of the last complete
    # segment, using the segment filenames, which the NVR stamps at file creation.
    span = (complete[-1].start - complete[0].start).total_seconds() + SEGMENT_SECONDS
    effective_fps = total_frames / span if span else 0.0

    print(f"Segments analysed : {len(complete)} complete "
          f"({len(segments) - len(complete)} excluded: in-progress or unreadable)")
    print(f"Total frames      : {total_frames}")
    print(f"Wall span         : {span:.0f}s")
    print(f"Effective fps     : {effective_fps:.4f}")
    print()

    counts = Counter(s.packets for s in complete)
    print("Frame count distribution per segment:")
    for count in sorted(counts):
        if count == expected_per_segment:
            flag = "  <-- EXPECTED"
        elif count > expected_per_segment:
            # ffmpeg's segment muxer can only cut on a keyframe. With --intra 15
            # (one keyframe per second) a segment that misses its cut point runs
            # on for whole extra GOPs. That is re-partitioning, NOT extra data,
            # and it costs no frames.
            extra = count - expected_per_segment
            flag = f"  <-- LONG (+{extra} frames, keyframe-boundary cut, harmless)"
        else:
            flag = "  <-- SHORT, POSSIBLE FRAME LOSS"
        print(f"  {count:5d} frames : {counts[count]:4d} segments{flag}")
    print()

    all_gaps = [(s, gap) for s in to_scan for gap in s.gaps]
    if all_gaps:
        print(f"TIMESTAMP GAPS DETECTED: {len(all_gaps)}")
        print("Each gap is a run of frames missing from the stream itself.")
        for segment, (pts, size) in all_gaps[:20]:
            missing = int(round(size)) - 1
            print(f"  {segment.path.rsplit('/', 1)[-1]} at pts {pts:7.2f}s "
                  f"-> {size:.1f}x nominal interval (~{missing} frame(s) lost)")
        if len(all_gaps) > 20:
            print(f"  ... and {len(all_gaps) - 20} more")
        print()

    for segment in segments:
        if segment.error:
            print(f"UNREADABLE: {segment.path} ({segment.error})")

    # ---- verdict ----------------------------------------------------------
    # Only SHORT segments can indicate loss. Long segments are the muxer cutting
    # on a later keyframe, which re-partitions frames without losing any, so they
    # must not be netted against shortfalls: 11 long segments cancelling 11 short
    # ones would otherwise read as "clean" while hiding real loss.
    short_frames = sum(expected_per_segment - s.packets
                       for s in complete if s.packets < expected_per_segment)
    long_frames = sum(s.packets - expected_per_segment
                      for s in complete if s.packets > expected_per_segment)
    short_segments = [s for s in complete if s.packets < expected_per_segment]
    lossy = bool(short_segments or all_gaps)
    drift_ppm = (effective_fps - args.fps) / args.fps * 1e6 if args.fps else 0.0
    drift_12h = (effective_fps - args.fps) / args.fps * 12 * 3600 if args.fps else 0.0

    # Drops are rare and bursty, typically tied to an RTSP reconnect, so a short
    # window that happens to contain none proves very little. The wall span also
    # sets the drift resolution: segment filenames carry whole seconds, so the
    # effective-fps figure is only meaningful over hours.
    UNDERPOWERED_SPAN = 30 * 60
    underpowered = span < UNDERPOWERED_SPAN

    print("=" * 68)
    if underpowered:
        print(f"!! SAMPLE TOO SMALL: {len(complete)} segments over {span:.0f}s.")
        print(f"   Anything under {UNDERPOWERED_SPAN // 60} min cannot rule out drops,")
        print("   which are bursty and usually tied to an RTSP reconnect. The")
        print("   effective-fps figure below is also noise at this span, because")
        print("   segment filenames only carry whole seconds.")
        print("   Re-run over a real session (ideally several hours) before")
        print("   treating any verdict here as evidence.")
        print()

    if not lossy:
        print("VERDICT: NO FRAME LOSS.")
        print(f"No short segments, no timestamp gaps, across {len(complete)} segments.")
        if long_frames:
            print(f"{long_frames} frame(s) sit in longer-than-nominal segments, which is the")
            print("segment muxer cutting on a later keyframe. No frames were lost.")
        print()
        if not underpowered:
            print("Frame counting is a VALID timeline. The frame N <-> sample S pairing")
            print("will hold, and an in-frame LED marker is NOT required.")
        else:
            print("PROVISIONAL ONLY: see the sample-size warning above.")
    else:
        print("VERDICT: FRAMES ARE BEING LOST.")
        if short_segments:
            print(f"{short_frames} frame(s) missing across {len(short_segments)} short segment(s).")
        if all_gaps:
            print(f"{len(all_gaps)} timestamp gap(s) detected inside segments.")
        print()
        print("Frame counting alone will silently shift the alignment. Either add a")
        print("self-locating marker in the pixels (LED), or record a per-segment frame")
        print("count in the sync manifest so breaks are detected and repaired offline.")
    print()
    print(f"Camera vs NVR wall clock: {drift_ppm:+.0f} ppm ({drift_12h:+.1f}s over 12h).")
    print("This is a REAL relative-rate measurement (total frames delivered over")
    print("elapsed wall time), but it absorbs any NVR clock error, and the segment")
    print("filenames quantise the span to whole seconds. It is NOT the number that")
    print("matters: real drift is camera vs XDAQ sample clock, and only the Wire 2")
    print("pulses can measure that. Treat this as a calibrated preview.")
    print("=" * 68)

    return 0 if not lossy else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
