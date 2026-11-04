"""One figure style for the 2026-11-05 lab progress meeting deck (every section script imports this).

Colour = treatment, shade = sleep condition: water is the control and always LEFT, SOD1 RIGHT.
Okabe-Ito hues (colour-blind safe). Normal sleep = full colour, sleep deprivation (SD) = light tint
of the same hue, so treatment reads at a glance and condition second.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

WATER, SOD1 = "#0072B2", "#D55E00"            # normal sleep / rested
WATER_SD, SOD1_SD = "#56B4E9", "#F4A261"      # after sleep deprivation
COL = {("water", "NS"): WATER, ("SOD1", "NS"): SOD1, ("water", "SD"): WATER_SD, ("SOD1", "SD"): SOD1_SD}
ORDER = ("water", "SOD1")                     # control left, test right
INK, GRID, CHANCE = "#222222", "#E6E6E6", "#888888"
LIGHT_BG, DARK_BG = "#FFFFFF", "#ECECEC"      # light phase / dark phase shading on time axes

# Slide figures: 13.33 x 7.5 in slide, figures drawn at final size so fonts stay >= 14 pt on screen.
WIDE, HALF, TALL = (12.0, 5.2), (6.0, 5.2), (12.0, 6.2)
DPI = 220

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 15, "axes.titlesize": 16, "axes.labelsize": 15,
    "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 13, "axes.edgecolor": INK,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 1.2,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.dpi": 100,
    "savefig.dpi": DPI, "savefig.bbox": "tight", "savefig.facecolor": "white", "legend.frameon": False,
})


def save(fig, path):
    """PNG for the deck + PDF for print, same stem"""
    fig.savefig(f"{path}.png")
    fig.savefig(f"{path}.pdf")
    plt.close(fig)
