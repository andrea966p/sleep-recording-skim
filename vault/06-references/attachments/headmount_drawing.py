"""Concept drawing of the custom 8-pin wireless headmount (Pinnacle 8474-HR 4-channel standard pinout).

Everything is drawn in millimetres. Re-run after Pinnacle sends the connector drawing:
edit PITCH / SOCKET / BOARD below. Outputs PNG + SVG next to this file.
usage: /usr/bin/python3 -I headmount_drawing.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

OUT = Path(__file__).with_name("2026-10-19-custom-headmount-concept")

# ---- dimensions (mm). ASSUMED until Pinnacle's drawing: pitch 1.27, socket body ----
PITCH = 1.27            # inferred: 8 pins on Pinnacle's 5 x 3 mm 8415 board
BOARD = (7.0, 5.6)      # ML x AP; AP must stay <= 6.0
SOCKET = (5.4, 2.9)     # 2x4 female socket body, ML x AP (approximate)
PAD_D, DRILL_D = 0.70, 0.35
PIN_D = 0.55
PAD_Y = 2.15            # pad row distance from centre (front +, back -)

# Pinnacle 4-channel standard configuration (catalog 2026 p.10), long axis ML.
# Each column = one Pinnacle "row": (anterior pin, posterior pin)
COLS = [
    ("COMMON", "GND",    "#222222", "#d62728"),
    ("EEG 1",  "EEG 2",  "#1f5fbf", "#e0b000"),
    ("LFP +",  "LFP −",  "#2ca02c", "#2ca02c"),
    ("EMG A",  "EMG B",  "#6a3d9a", "#6a3d9a"),
]
GOLD, BOARD_C, SOCK_C = "#d9b45a", "#1e6b3c", "#262626"


def top_view(ax):
    w, h = BOARD
    ax.add_patch(FancyBboxPatch((-w / 2, -h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.45",
                                fc=BOARD_C, ec="#0c3a1d", lw=1.5))
    xs = [(i - 1.5) * PITCH for i in range(4)]
    for x, (ant, post, ca, cp) in zip(xs, COLS):
        for y_pin, y_pad, name, col in ((PITCH / 2, PAD_Y, ant, ca), (-PITCH / 2, -PAD_Y, post, cp)):
            ax.plot([x, x], [y_pin, y_pad], color=GOLD, lw=5, solid_capstyle="round", zorder=2)
            ax.add_patch(Circle((x, y_pad), PAD_D / 2, fc=GOLD, ec="#7a5d10", lw=1, zorder=3))
            ax.add_patch(Circle((x, y_pad), DRILL_D / 2, fc="white", ec="none", zorder=4))
            ax.add_patch(Circle((x, y_pad), PAD_D / 2 + 0.12, fc="none", ec=col, lw=2.2, zorder=4))
            ty = y_pad + (0.75 if y_pad > 0 else -0.75)
            ax.text(x, ty, name, rotation=90, ha="center", va="bottom" if y_pad > 0 else "top",
                    fontsize=10, fontweight="bold", color=col)
    sw, sh = SOCKET
    ax.add_patch(Rectangle((-sw / 2, -sh / 2), sw, sh, fc=SOCK_C, ec="black", lw=1.2, zorder=5))
    for x, (_, _, ca, cp) in zip(xs, COLS):
        for y, col in ((PITCH / 2, ca), (-PITCH / 2, cp)):
            ax.add_patch(Circle((x, y), PIN_D / 2, fc="#111", ec=GOLD, lw=2.2, zorder=6))
    # pairs: ring links like Pinnacle's diagram
    for x, (ant, post, ca, cp) in zip(xs, COLS):
        if ant.startswith(("LFP", "EMG")):
            ax.plot([x, x], [PITCH / 2 - 0.3, -PITCH / 2 + 0.3], color=ca, lw=2.5, zorder=7)
    # dimensions
    ax.annotate("", (w / 2 + 0.5, h / 2), (w / 2 + 0.5, -h / 2), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(w / 2 + 0.7, 0, f"{h:.1f} mm AP\n(limit 6.0)", va="center", fontsize=9)
    ax.annotate("", (-w / 2, -h / 2 - 2.9), (w / 2, -h / 2 - 2.9), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(0, -h / 2 - 3.2, f"{w:.1f} mm ML", ha="center", va="top", fontsize=9)
    ax.annotate("", (xs[0], PITCH / 2 + 0.05), (xs[1], PITCH / 2 + 0.05),
                arrowprops=dict(arrowstyle="<->", lw=0.8, color="white"), zorder=8)
    ax.text((xs[0] + xs[1]) / 2, PITCH / 2 + 0.25, f"{PITCH}", color="white", fontsize=7, ha="center", zorder=8)
    # orientation
    ax.annotate("", (-w / 2 - 1.0, 1.8), (-w / 2 - 1.0, -1.8), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.text(-w / 2 - 1.0, 2.0, "ANT", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xlim(-w / 2 - 1.8, w / 2 + 2.3)
    ax.set_ylim(-h / 2 - 4.0, h / 2 + 3.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Top view (to scale), head unit plugs on from above", fontsize=11, loc="left")


def pin_table(ax):
    rows = [
        ["COMMON", "ref. for CH1, CH2", "skull screw (e.g. cerebellum), lead"],
        ["GND", "ground", "skull screw, lead"],
        ["EEG 1", "CH1 = EEG1 − COMMON", "cortical screw, lead"],
        ["EEG 2", "CH2 = EEG2 − COMMON", "2nd cortical screw (or unused)"],
        ["LFP +", "CH3 = LFP+ − LFP−", "pons target wire, through via, down"],
        ["LFP −", "(fully independent pair)", "pons reference wire, through via, down"],
        ["EMG A", "CH4 = EMG A − EMG B", "nuchal wire, exits posterior"],
        ["EMG B", "(fully independent pair)", "nuchal wire, exits posterior"],
    ]
    t = ax.table(cellText=rows, colLabels=["Pin", "Channel", "Electrode / wire"], loc="upper left",
                 cellLoc="left", colLoc="left", colWidths=[0.17, 0.38, 0.45])
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.45)
    for (r, _), c in t.get_celld().items():
        c.set_edgecolor("#bbbbbb")
        if r == 0:
            c.set_facecolor("#e8edf6")
            c.set_text_props(fontweight="bold")
    ax.axis("off")
    ax.set_title("Pin map (Pinnacle 4-channel standard configuration)", fontsize=11, loc="left")


def notes(ax):
    lines = [
        "Verified on Pinnacle (catalog 2026):",
        "• p.10: 4-ch standard = CH1, CH2 vs COMMON; CH3, CH4 differential;",
        "   1 COMMON + 1 GROUND = 8 pins, no spare.",
        "• p.13: headmount socket is FEMALE, openings up;",
        "   leads straight (8415) or bent under (-SM).",
        "• Headmounts page: 8431-SM = 8 pins, 5 x 5 mm, \"2 EEG/1 EMG",
        "   (fully independent)\"; 8415 = 8 pins, 5 x 3 mm.",
        "Assumed (confirm with Pinnacle's drawing or a measured 8415):",
        "• Pitch 1.27 mm; socket body ~5.4 x 2.9 mm; long axis ML.",
        "• Which end is COMMON (mirror image) per Pinnacle's drawing.",
        "• 2-layer FR4 0.6 mm; pads Ø0.70, drill 0.35 mm (36 AWG PFA);",
        "   EMG multistrand may need a larger drill.",
        "Candidate sockets on our shelf (female, 1.27 mm, 2x4):",
        "   Preci-dip 853-87-008-10-001101; Amphenol 20021311-00008T1LF.",
    ]
    ax.text(0, 1, "\n".join(lines), va="top", fontsize=9.5, linespacing=1.45, transform=ax.transAxes)
    ax.axis("off")


fig = plt.figure(figsize=(13, 8.2), dpi=150)
fig.suptitle("Custom 8-pin wireless headmount for 8474-HR 4-ch (2 EEG + 2 independent): concept, not for fabrication",
             fontsize=13, fontweight="bold", x=0.02, ha="left")
top_view(fig.add_axes([0.02, 0.06, 0.42, 0.86]))
pin_table(fig.add_axes([0.47, 0.42, 0.51, 0.48]))
notes(fig.add_axes([0.47, 0.02, 0.51, 0.38]))
fig.savefig(OUT.with_suffix(".png"))
fig.savefig(OUT.with_suffix(".svg"))
print("wrote", OUT.with_suffix(".png"), OUT.with_suffix(".svg"))
