# -*- coding: utf-8 -*-
"""
Fig.2  Wedge feasible-region compression (165 x 82 mm)
Archetype: geometry-led
Visual focus: orange intersection shrinks from full disk to thin quadrilateral
Panels: (a) before observation  (b) 1 station  (c) 2 stations  (d) 3 stations
In-figure numbers: 3600 / 1801.71 / 110.59 / 69.96
Data: frozen package b26.locate (real-time computation, no mock data)
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle
from _pub import *
from b26 import locate

R = 1800.0
# Stations and true source (golden example from frozen data)
S1 = (0.0, 0.0)
S2 = (0.0, 1000.0)
S3 = (1500.0, -800.0)
G  = (1000.0, 0.0)

def bearing(s, g):
    return math.degrees(math.atan2(g[1] - s[1], g[0] - s[0])) % 360.0

def region(pairs):
    poly = None
    for (s, t) in pairs:
        w = locate.wedge_poly(s, t, R)
        poly = w if poly is None else locate.intersect(poly, w)
        if not poly:
            return []
    return poly

def draw_zoom_inset(fig, px, py, pw, ph, reg, with_diameter=False):
    """Draw a zoomed inset of the intersection region. Thin frame, no rounded corners."""
    ia = ax_frame(fig, px, py, pw, ph, ec=C_GRAY, lw=LW_THIN)
    xs = [p[0] for p in reg]
    ys = [p[1] for p in reg]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    h = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.6 + 15
    ia.set_xlim(cx - h, cx + h)
    ia.set_ylim(cy - h, cy + h)
    ia.set_aspect("equal", adjustable="box")
    ia.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.70,
                        edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
    for p in reg:
        ia.plot(*p, marker="o", ms=3.0, color=C_ORANGE,
                markeredgecolor=C_DARK, markeredgewidth=0.4, zorder=6)
    if with_diameter:
        best, pa, pb = -1, None, None
        for ai in range(len(reg)):
            for bi in range(ai + 1, len(reg)):
                dd = math.dist(reg[ai], reg[bi])
                if dd > best:
                    best, pa, pb = dd, reg[ai], reg[bi]
        ia.plot([pa[0], pb[0]], [pa[1], pb[1]], ls=(0, (3, 2)),
                color=C_RED, lw=LW_MID, zorder=7)


def draw(src_dir):
    fig = canvas(82)

    MARGIN_X = 4.0
    GAP = 3.0
    PW = (W_STD - 2 * MARGIN_X - 3 * GAP) / 4.0
    PANEL_Y = 4.0
    PANEL_H = 56.0
    LABEL_Y = 64.0

    PAIRS = [
        [],
        [(S1, bearing(S1, G))],
        [(S1, bearing(S1, G)), (S2, bearing(S2, G))],
        [(S1, bearing(S1, G)), (S2, bearing(S2, G)), (S3, bearing(S3, G))],
    ]
    dia_vals = {}

    for i in range(4):
        x = MARGIN_X + i * (PW + GAP)
        a = ax(fig, x, PANEL_Y, PW, PANEL_H)
        eq(a, (-R * 1.06, R * 1.06), (-R * 1.06, R * 1.06))

        # Task domain boundary
        a.add_patch(Circle((0, 0), R, fill=False, edgecolor=C_GRAY_L,
                            lw=LW_THIN, zorder=1))

        # Wedges (blue with visible boundary)
        for (s, t) in PAIRS[i]:
            w = locate.wedge_poly(s, t, R)
            a.add_patch(MPoly(w, closed=True, facecolor=C_BLUE, alpha=0.15,
                               edgecolor=C_BLUE, lw=LW_THIN, zorder=2))

        reg = region(PAIRS[i])
        if i == 0:
            a.add_patch(Circle((0, 0), R, facecolor=C_ORANGE, alpha=0.35,
                                edgecolor=C_ORANGE, lw=LW_THICK, zorder=3))
            dia_vals[i] = 2 * R
        elif reg:
            dia_vals[i] = locate.diameter(reg)
            a.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.80,
                               edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
            for p in reg:
                a.plot(*p, marker="o", ms=2.5, color=C_ORANGE,
                       markeredgecolor=C_DARK, markeredgewidth=0.3, zorder=6)

        # Station markers
        for (s, t) in PAIRS[i]:
            a.plot(*s, marker="o", ms=3.5, color=C_BLUE,
                   markeredgecolor="white", markeredgewidth=0.4, zorder=8)

        panel_label(a, "(%s)" % chr(97 + i), loc="upper left", fs=FS_LABEL)

        # Zoom inset for panels c and d (region too small to see in full view)
        if i >= 2 and reg:
            inset_w = PW * 0.48
            inset_h = PANEL_H * 0.48
            ix = x + PW - inset_w - 1.0
            iy = PANEL_Y + 1.0
            draw_zoom_inset(fig, ix, iy, inset_w, inset_h, reg,
                            with_diameter=(i == 3))
            # Zoom indicator box in main view
            xs = [p[0] for p in reg]
            ys = [p[1] for p in reg]
            zx = (min(xs) + max(xs)) / 2
            zy = (min(ys) + max(ys)) / 2
            zh = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.5 + 20
            a.add_patch(MPoly([(zx-zh, zy-zh), (zx+zh, zy-zh), (zx+zh, zy+zh), (zx-zh, zy+zh)],
                               closed=True, fill=False, edgecolor=C_GRAY, lw=LW_THIN,
                               ls=(0, (2, 2)), zorder=5))

        # Diameter value
        fig.text((x + PW / 2) / W_STD, (82 - LABEL_Y) / 82.0,
                 "D = %.2f m" % dia_vals[i],
                 fontsize=FS_NUM, color=C_ORANGE, fontweight="bold",
                 ha="center", va="top")

    print("Fig.2 diameters:", {i: round(v, 2) for i, v in dia_vals.items()})
    out = os.path.join(os.path.dirname(src_dir), "figures_final", "Fig02")
    return save(fig, out, "Fig02")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
