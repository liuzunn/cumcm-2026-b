# -*- coding: utf-8 -*-
"""
Fig.5  9-point guaranteed coverage certificate (165 x 88 mm)
Archetype: geometry-led
Visual focus: worst-coverage point + 173.2 m margin segment (geometric length)
9 circles at low opacity; union boundary emerges naturally.
Data: b26.search.COVER_9 + 10m-grid independent recomputation
In-figure numbers: 826.8 / 173.2 / 1000 / 9
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle
from _pub import *
from b26 import search

R_DOM = 1800.0
R_COV = 1000.0
COVER = search.COVER_9
WP = (1660.0, -690.0)

def draw(src_dir):
    fig = canvas(88)

    # Main view (leave bottom space for summary)
    MX, MY, MW, MH = 4.0, 16.0, 100.0, 68.0
    a = ax(fig, MX, MY, MW, MH)
    eq(a, (-R_DOM * 1.04, R_DOM * 1.04), (-R_DOM * 1.04, R_DOM * 1.04))

    # Task domain (dark solid)
    a.add_patch(Circle((0, 0), R_DOM, fill=False, edgecolor=C_DARK,
                        lw=LW_THICK, zorder=2))

    # 9 coverage circles (low opacity blue, union emerges)
    for c in COVER:
        a.add_patch(Circle(c, R_COV, fill=True, facecolor=C_BLUE, alpha=0.10,
                            edgecolor="none", zorder=1))
    # Coverage circle boundaries (very thin, only for reference)
    for c in COVER:
        a.add_patch(Circle(c, R_COV, fill=False, edgecolor=C_BLUE, alpha=0.25,
                            lw=LW_THIN, zorder=1))

    # Cover center points
    for c in COVER:
        a.plot(*c, marker="o", ms=3.0, color=C_BLUE,
               markeredgecolor="white", markeredgewidth=0.3, zorder=5)

    # Worst point (red square)
    a.plot(*WP, marker="s", ms=7.0, color=C_RED,
           markeredgecolor=C_DARK, markeredgewidth=0.5, zorder=8)

    # Nearest cover point and distance line (thin)
    dists = [(math.hypot(WP[0]-c[0], WP[1]-c[1]), c) for c in COVER]
    dists.sort()
    nearest_d, nearest_pt = dists[0]
    margin = R_COV - nearest_d
    a.plot([WP[0], nearest_pt[0]], [WP[1], nearest_pt[1]],
           color=C_GRAY, lw=LW_THIN, ls=(0, (2, 2)), zorder=4)

    # Margin segment (red solid, from WP toward 1000m boundary)
    dx = nearest_pt[0] - WP[0]
    dy = nearest_pt[1] - WP[1]
    ux, uy = dx / nearest_d, dy / nearest_d
    seg_end = (WP[0] + ux * margin, WP[1] + uy * margin)
    a.plot([WP[0], seg_end[0]], [WP[1], seg_end[1]],
           color=C_RED, lw=LW_THICK, ls="-", zorder=7)

    # Zoom indicator box in main view
    zh = 250.0
    a.add_patch(MPoly([(WP[0]-zh, WP[1]-zh), (WP[0]+zh, WP[1]-zh),
                        (WP[0]+zh, WP[1]+zh), (WP[0]-zh, WP[1]+zh)],
                       closed=True, fill=False, edgecolor=C_GRAY, lw=LW_THIN,
                       ls=(0, (2, 2)), zorder=6))

    panel_label(a, "(a)", loc="upper left", fs=FS_LABEL)

    # ---- Zoom inset (right side, aligned with main view) ----
    IW, IH = 52.0, 40.0
    IX = W_STD - IW - 4.0
    IY = 30.0
    ia = ax_frame(fig, IX, IY, IW, IH, ec=C_GRAY, lw=LW_THIN)
    zc_x = (WP[0] + seg_end[0]) / 2
    zc_y = (WP[1] + seg_end[1]) / 2
    zh2 = 160.0
    ia.set_xlim(zc_x - zh2, zc_x + zh2)
    ia.set_ylim(zc_y - zh2, zc_y + zh2)
    ia.set_aspect("equal", adjustable="box")

    # Coverage circle boundary (for scale reference)
    ia.add_patch(Circle(nearest_pt, R_COV, fill=False, edgecolor=C_BLUE,
                        alpha=0.4, lw=LW_THIN, zorder=1))

    # Margin segment (red thick)
    ia.plot([WP[0], seg_end[0]], [WP[1], seg_end[1]],
            color=C_RED, lw=LW_THICK, ls="-", zorder=5)

    # Worst point (red square)
    ia.plot(*WP, marker="s", ms=8.0, color=C_RED,
            markeredgecolor=C_DARK, markeredgewidth=0.5, zorder=8)

    # 1000m boundary point (end of margin segment)
    ia.plot(*seg_end, marker="o", ms=4.0, color=C_RED,
            markeredgecolor="white", markeredgewidth=0.4, zorder=7)

    # Margin label: 173.2 m
    mid_m = ((WP[0] + seg_end[0]) / 2, (WP[1] + seg_end[1]) / 2)
    ia.annotate("%.1f m" % margin,
                xy=mid_m, xytext=(mid_m[0] - 50, mid_m[1] + 50),
                fontsize=FS_NUM, color=C_RED, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=C_RED, lw=LW_MID),
                zorder=9)

    panel_label(ia, "(b)", loc="upper left", fs=FS_LABEL)

    # ---- Summary text at bottom ----
    fig.text((MX + MW / 2) / W_STD, (88 - 7) / 88.0,
             "9 points   r_min = 1000 m   max uncovered = %.1f m   margin = %.1f m" %
             (nearest_d, margin),
             fontsize=FS_LABEL, color=C_DARK, fontweight="bold",
             ha="center", va="top")

    print("Fig.5  nearest=%.2f  margin=%.2f  cover_points=%d" %
          (nearest_d, margin, len(COVER)))
    out = os.path.join(os.path.dirname(src_dir), "figures_final", "Fig05")
    return save(fig, out, "Fig05")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
