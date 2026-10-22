"""Custom wireless headmount for the Pinnacle 8474-HR 4-ch (2 EEG + 2 independent), in SKULL coordinates.

Units mm, origin = bregma, x = ML (+ right), y = AP (+ anterior), flat skull. Electrode pins protrude from
the PCB underside at their stereotaxic sites; the 2x4 socket sits on top. 2-layer board, routed by hand
below and checked for clearance automatically (CLEAR mm). Edit parameters and re-run:
    /usr/bin/python3 -I headmount_drawing.py
"""
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Rectangle

OUT = Path(__file__).with_name("2026-10-19-custom-headmount-concept")

# ---------------- parameters ----------------
BL = 4.2                       # bregma-lambda (reference value; scale AP to the measured value)
EEG_ML = 1.27                  # Iwasaki 2021: pins at ML +/-1.27
EEG_POST_Y = -BL + 0.3         # posterior pair "just anterior to the lambdoid sutures" (0.3 assumed)
EEG_ANT_Y = EEG_POST_Y + 5.03  # anterior pair 5.03 mm anterior
PONS_Y = -5.4                  # Schott et al. 2023: pons burr hole AP -5.4 (ML 0.9)
LFP_T = (0.8, PONS_Y)          # LFP target pin
LFP_R = (1.8, PONS_Y)          # LFP reference pin, 1.0 mm lateral (placement to confirm with ahyeon)
PONS_DV = 4.5
PITCH = 1.27                   # socket pitch, ASSUMED
SOCK_C, SOCK_WH = (0.0, -1.4), (5.4, 2.9)
BOARD = (-3.2, 3.2, -6.0, 1.8) # x0, x1, y0, y1
ELEC_PAD, SOCK_PAD, EMG_PAD = 0.80, 0.75, 0.60   # pad diameters
TRACE, CLEAR = 0.15, 0.15

COLOR = {"EEG 1": "#0072B2", "EEG 2": "#56B4E9", "COMMON": "#000000", "GND": "#D55E00",
         "LFP +": "#009E73", "LFP −": "#7FC97F", "EMG A": "#CC79A7", "EMG B": "#8E44AD"}

# socket columns L->R (Pinnacle 4-ch standard: one pair per column); (front pin, back pin)
COLS = [("GND", "COMMON"), ("EEG 1", "EEG 2"), ("LFP +", "LFP −"), ("EMG A", "EMG B")]
SOCK = {}
for i, (f, b) in enumerate(COLS):
    x = SOCK_C[0] + (i - 1.5) * PITCH
    SOCK[f], SOCK[b] = (x, SOCK_C[1] + PITCH / 2), (x, SOCK_C[1] - PITCH / 2)

ELEC = {  # net: (x, y, site)
    "EEG 1": (-EEG_ML, EEG_ANT_Y, "frontal L"),
    "EEG 2": (EEG_ML, EEG_ANT_Y, "frontal R"),
    "COMMON": (-EEG_ML, EEG_POST_Y, "parietal L"),
    "GND": (EEG_ML, EEG_POST_Y, "parietal R"),
    "LFP +": (*LFP_T, "pons target"),
    "LFP −": (*LFP_R, "pons reference"),
}
EMG = {"EMG A": (2.75, -3.4), "EMG B": (2.75, -4.3)}

# routes: net -> (layer, waypoints); start = socket pin, end = electrode / EMG pad
ROUTES = {
    "EEG 1": ("top", [SOCK["EEG 1"], (-0.635, 0.4), (-1.27, 0.95), ELEC["EEG 1"][:2]]),
    "COMMON": ("top", [SOCK["COMMON"], (-1.905, -3.3), ELEC["COMMON"][:2]]),
    "LFP −": ("bottom", [SOCK["LFP −"], (1.27, -2.67), (1.95, -3.3), (1.95, -5.0), ELEC["LFP −"][:2]]),
    "LFP +": ("top", [SOCK["LFP +"], (0.635, -2.6)]),  # placeholder, replaced below
    "EMG A": ("top", [SOCK["EMG A"], (2.75, -1.4), EMG["EMG A"]]),
    "EMG B": ("top", [SOCK["EMG B"], (2.2, -2.4), (2.2, -3.9), EMG["EMG B"]]),
    "EEG 2": ("bottom", [SOCK["EEG 2"], (0.0, -1.4), (0.0, 0.4), (1.27, 0.95), ELEC["EEG 2"][:2]]),
    "GND": ("bottom", [SOCK["GND"], (-2.85, -1.4), (-2.85, -3.0), (0.3, -3.0), (0.3, -3.5), ELEC["GND"][:2]]),
}
# LFP + (front pin) must pass the back row: drop through the gap between LFP and EMG columns on TOP,
# then run down at x = 0.55 to the target pin.  LFP - (back pin) goes on the bottom layer.
ROUTES["LFP +"] = ("top", [SOCK["LFP +"], (1.27, -1.4), (1.27, -2.67), (0.55, -3.1), (0.55, -5.0), LFP_T])
ROUTES["LFP −"] = ("bottom", [SOCK["LFP −"], (0.635, -2.6), (1.95, -3.3), (1.95, -5.0), LFP_R])


def pads():
    """(net, x, y, radius) for every through-hole pad (present on both layers)."""
    out = [(n, x, y, SOCK_PAD / 2) for n, (x, y) in SOCK.items()]
    out += [(n, x, y, ELEC_PAD / 2) for n, (x, y, _) in ELEC.items()]
    out += [(n, x, y, EMG_PAD / 2) for n, (x, y) in EMG.items()]
    return out


def seg_pt(p, a, b):
    p, a, b = map(np.asarray, (p, a, b))
    t = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-12), 0, 1)
    return float(np.linalg.norm(p - (a + t * (b - a))))


def seg_seg(a, b, c, d):
    def ccw(p, q, r):
        return (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0])
    if ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d):
        return 0.0
    return min(seg_pt(a, c, d), seg_pt(b, c, d), seg_pt(c, a, b), seg_pt(d, a, b))


def check():
    """Return clearance violations (copper edge to copper edge < CLEAR)."""
    bad, segs = [], []
    for net, (layer, pts) in ROUTES.items():
        segs += [(net, layer, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    for net, layer, a, b in segs:
        for pnet, x, y, r in pads():
            if pnet != net and seg_pt((x, y), a, b) - r - TRACE / 2 < CLEAR:
                bad.append(f"{net} ({layer}) too close to pad {pnet}")
        for edge in (BOARD[0], BOARD[1]):
            if min(abs(a[0] - edge), abs(b[0] - edge)) < TRACE / 2 + 0.2:
                bad.append(f"{net} too close to board edge")
    for (n1, l1, a, b), (n2, l2, c, d) in combinations(segs, 2):
        if n1 != n2 and l1 == l2 and seg_seg(a, b, c, d) - TRACE < CLEAR:
            bad.append(f"{n1} vs {n2} on {l1}")
    for (n1, x1, y1, r1), (n2, x2, y2, r2) in combinations(pads(), 2):
        if np.hypot(x1 - x2, y1 - y2) - r1 - r2 < CLEAR:
            bad.append(f"pads {n1} / {n2} overlap")
    return sorted(set(bad))


def skull(ax):
    ax.add_patch(Ellipse((0, -2.2), 11.0, 17.5, fc="#f4efe6", ec="#b9ad97", lw=1.2, zorder=0))
    xs = np.linspace(-4.8, 4.8, 60)
    ax.plot(xs, 0.12 * xs ** 2, color="#c9bfae", lw=1, zorder=1)            # coronal suture
    ax.plot(xs, -BL + 0.10 * xs ** 2, color="#c9bfae", lw=1, zorder=1)      # lambdoid suture
    ax.plot([0, 0], [5.5, -10.5], color="#c9bfae", lw=1, zorder=1)          # sagittal suture
    for y, t in ((0, "bregma"), (-BL, "lambda")):
        ax.plot([-5.6, -3.35], [y, y], color="#8a7a5c", lw=0.8, ls=(0, (3, 2)), zorder=1)
        ax.text(-5.7, y, t, ha="right", va="center", fontsize=9, color="#8a7a5c")
    ax.text(0, -9.2, "interparietal bone (cerebellum below)", ha="center", fontsize=8.5, color="#8a7a5c")


def top_view(ax):
    skull(ax)
    x0, x1, y0, y1 = BOARD
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.5",
                                fc="#1b5e35", ec="#0b2e18", lw=1.5, zorder=2))
    # bregma / lambda marks drawn ON the board as silkscreen crosses
    for y in (0, -BL):
        ax.plot(0, y, marker="+", ms=11, mew=1.4, color="white", zorder=3)
    for net, (layer, pts) in ROUTES.items():
        xs, ys = zip(*pts)
        if layer == "bottom":
            ax.plot(xs, ys, color="white", lw=4.2, zorder=3, solid_capstyle="round")
            ax.plot(xs, ys, color=COLOR[net], lw=2.6, ls=(0, (2.2, 1.2)), zorder=4)
        else:
            ax.plot(xs, ys, color=COLOR[net], lw=3.0, zorder=5, solid_capstyle="round", solid_joinstyle="round")
    for net, x, y, r in pads():
        ax.add_patch(Circle((x, y), r, fc="#e2c16b", ec=COLOR[net], lw=2.2, zorder=7))
        ax.add_patch(Circle((x, y), r * 0.45, fc="white", ec="none", zorder=8))
    sw, sh = SOCK_WH   # socket body outline only (pads stay visible)
    ax.add_patch(Rectangle((SOCK_C[0] - sw / 2, SOCK_C[1] - sh / 2), sw, sh, fc="none", ec="white",
                           lw=1.3, ls=(0, (4, 2)), zorder=9))
    # labels: fixed slots outside the board, leader to the pad
    slots = {"EEG 1": (-4.1, 1.13, "right"), "COMMON": (-4.1, -2.8, "right"),
             "EEG 2": (4.1, 1.13, "left"), "GND": (4.1, -5.0, "left"),
             "EMG A": (4.1, -3.4, "left"), "EMG B": (4.1, -4.3, "left"),
             "LFP −": (4.1, -5.85, "left"), "LFP +": (-4.1, -5.4, "right")}
    where = {**{n: (x, y) for n, (x, y, _) in ELEC.items()}, **EMG}
    sites = {n: s for n, (_, _, s) in ELEC.items()}
    for net, (tx, ty, ha) in slots.items():
        label = f"{net}  ({sites[net]})" if net in sites else f"{net}  (EMG wire pad)"
        ax.annotate(label, where[net], (tx, ty), ha=ha, va="center", fontsize=9.5, fontweight="bold",
                    color=COLOR[net] if net not in ("EEG 2", "LFP −") else "#333",
                    arrowprops=dict(arrowstyle="-", lw=1.0, color="#555", shrinkA=2, shrinkB=4,
                                    connectionstyle="angle,angleA=0,angleB=90,rad=0" if net == "GND" else "arc3"),
                    zorder=10)
    # dimensions
    ax.annotate("", (x1 + 0.25, y1), (x1 + 0.25, y0), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(x1 + 0.35, -2.3, f"{y1 - y0:.1f} mm AP", rotation=90, fontsize=8.5, va="bottom")
    ax.annotate("", (x0, y0 - 0.4), (x1, y0 - 0.4), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(0, y0 - 0.6, f"{x1 - x0:.1f} mm ML", ha="center", va="top", fontsize=8.5)
    ax.annotate("", (-5.2, -6.6), (-5.2, -8.4), arrowprops=dict(arrowstyle="-|>", lw=1.4))
    ax.text(-5.2, -8.6, "anterior ↑", ha="center", va="top", fontsize=8.5)
    ax.set_xlim(-9.6, 9.6)
    ax.set_ylim(-10.0, 4.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Top view on the skull, to scale (mm from bregma)", fontsize=11.5, loc="left")
    ax.legend(handles=[Line2D([], [], color="#444", lw=3, label="top-layer trace"),
                       Line2D([], [], color="#444", lw=2.6, ls=(0, (2.2, 1.2)), label="bottom-layer trace"),
                       Line2D([], [], marker="o", ls="", mfc="#e2c16b", mec="#444", ms=9,
                              label="plated hole (pin or wire)"),
                       Line2D([], [], color="#888", lw=1.3, ls=(0, (4, 2)), label="socket outline (white, dashed)")],
              loc="lower right", fontsize=8.5, frameon=False)


def side_view(ax):
    ax.axhline(0, color="#b9ad97", lw=3, zorder=1)
    ax.add_patch(Rectangle((BOARD[2], 0.3), BOARD[3] - BOARD[2], 0.6, fc="#1b5e35", zorder=2))
    ax.add_patch(Rectangle((SOCK_C[1] - SOCK_WH[1] / 2, 0.9), SOCK_WH[1], 2.0, fc="#262626", zorder=2))
    ax.text(SOCK_C[1], 1.9, "socket", color="white", ha="center", va="center", fontsize=8)
    for y, c in ((EEG_ANT_Y, COLOR["EEG 1"]), (EEG_POST_Y, COLOR["COMMON"])):
        ax.plot([y, y], [0.3, -0.35], color=c, lw=2.8, zorder=3)
    ax.plot([PONS_Y] * 2, [0.3, -PONS_DV], color=COLOR["LFP +"], lw=2.8, zorder=3)
    ax.plot(PONS_Y, -PONS_DV, "o", color=COLOR["LFP +"], ms=6, zorder=4)
    ax.text(PONS_Y + 0.35, -PONS_DV, f"LFP target + reference tips\n(both at DV ≈ {PONS_DV})", ha="right",
            va="center", fontsize=8)
    ax.text(0.2, -0.6, "EEG / COMMON / GND pins\nend at the dura", ha="center", va="top", fontsize=8)
    ax.text(BOARD[3] + 0.3, 0.12, "skull", fontsize=8, color="#8a7a5c", va="bottom")
    ax.set_xlim(BOARD[3] + 0.6, BOARD[2] - 0.6)
    ax.set_ylim(-5.3, 3.3)
    ax.set_aspect("equal")
    ax.set_xlabel("AP (mm from bregma)   ← anterior", fontsize=8.5)
    ax.set_ylabel("DV (mm)", fontsize=8.5)
    ax.tick_params(labelsize=8)
    ax.set_title("Side view, to scale (sagittal)", fontsize=11.5, loc="left")


def table(ax):
    rows = [["CH1", "EEG 1 − COMMON", "frontal L − parietal L (Tsukuba bipolar EEG)"],
            ["CH2", "EEG 2 − COMMON", "frontal R − parietal L (optional 2nd EEG)"],
            ["CH3", "LFP + − LFP −", "pons target − pons reference (independent)"],
            ["CH4", "EMG A − EMG B", "nuchal pair (independent)"],
            ["GND", "ground", "parietal R"]]
    t = ax.table(cellText=rows, colLabels=["", "Pins", "Electrodes"], loc="upper left", cellLoc="left",
                 colLoc="left", colWidths=[0.1, 0.3, 0.6])
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.5)
    for (r, _), c in t.get_celld().items():
        c.set_edgecolor("#c8c8c8")
        if r == 0:
            c.set_facecolor("#e8edf6")
            c.set_text_props(fontweight="bold")
    ax.axis("off")
    ax.set_title("Channels (Pinnacle 4-ch standard configuration, catalog p.10)", fontsize=11.5, loc="left")


violations = check()
fig = plt.figure(figsize=(16, 9.6), dpi=140)
fig.suptitle("Custom wireless headmount for Pinnacle 8474-HR 4-ch: electrode pins at stereotaxic sites (concept)",
             fontsize=13.5, fontweight="bold", x=0.015, ha="left")
top_view(fig.add_axes([0.02, 0.11, 0.55, 0.82]))
table(fig.add_axes([0.58, 0.62, 0.40, 0.27]))
side_view(fig.add_axes([0.6, 0.15, 0.37, 0.38]))
status = "clearance check: PASS" if not violations else f"clearance check: {len(violations)} issue(s)"
fig.text(0.015, 0.012,
         f"{status} (trace {TRACE} mm, clearance ≥ {CLEAR} mm, pads Ø{ELEC_PAD}/{SOCK_PAD}/{EMG_PAD} mm).  "
         "Sources: Iwasaki et al. 2021 STAR Protoc 2:100982 (pins ML ±1.27, pairs 5.03 mm apart, posterior pair just "
         "anterior to lambda, no cerebellar screw);\n"
         "Schott et al. 2023 Nat Commun (pons AP −5.4, ML 0.9); bregma–lambda ≈ 4.2 mm (Paxinos & Franklin reference; "
         "varies with sex, weight, age: scale AP to the measured value).\nAssumed: socket pitch 1.27 mm and outline; posterior pins 0.3 mm anterior to lambda; LFP reference 1 mm lateral "
         "of target; socket column order per Pinnacle's drawing.",
         fontsize=7.8, va="bottom")
fig.savefig(OUT.with_suffix(".png"))
fig.savefig(OUT.with_suffix(".svg"))
print(status)
for v in violations:
    print("  ", v)
