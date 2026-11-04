#!/usr/bin/env python3
"""Cut each Y-maze video to the trial: TRIAL_S from the moment the experimenter's hand has left the
view, with the batch 1 Y-maze encoder (SOP changelog 2026-10-24).

    ymaze_trim.py cut <video_dir> <out_dir>     # reads <out_dir>/hand_out.csv -> <stem>_trial480s.mp4

hand_out.csv: stem,start_s[,source], the start read by eye per video (Andrea). An automatic detector
was tried on 2026-11-04 and cut 0.3-0.6 s early in 4 of 10 NS-SD videos (the hand and the release box
leave through a corner in a few small frames), so the start is set by eye.

cut: accurate seek to start_s, TRIAL_S long, CFR 30 fps, rotation applied, 1080 px, libx264 crf 18
preset slow, no audio. Each output must have exactly TRIAL_S * 30 frames.
"""
import csv
import pathlib
import subprocess
import sys

TRIAL_S = 480
FPS = 30


def cut(vdir, odir):
    for r in csv.DictReader(open(odir / "hand_out.csv")):
        src, out = vdir / f"{r['stem']}.mp4", odir / f"{r['stem']}_trial480s.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(src), "-ss", r["start_s"],
                        "-t", str(TRIAL_S), "-vf", f"fps={FPS},scale=-2:1080", "-c:v", "libx264", "-crf", "18",
                        "-preset", "slow", "-pix_fmt", "yuv420p", "-an", str(out)], check=True)
        n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                "stream=nb_read_frames", "-of", "csv=p=0", str(out)],
                               capture_output=True, text=True, check=True).stdout.strip())
        print(out.name, n, "frames", "OK" if n == TRIAL_S * FPS else "WRONG LENGTH", flush=True)


if __name__ == "__main__":
    cut(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])) if sys.argv[1:2] == ["cut"] else sys.exit(__doc__)
