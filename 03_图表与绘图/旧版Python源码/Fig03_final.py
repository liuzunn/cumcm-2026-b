# -*- coding: utf-8 -*-
"""
Fig.3  Diameter-circle coverage counterexample (165 x 78 mm)
Archetype: geometry-led (contrast pair)
Left:  golden example, diameter circle SUCCEEDS (D=110.59 m)
Right: counterexample, diameter circle FAILS (D=116.92 m, vertex 2.00 m outside)
Visual focus: red square vertex outside the dashed circle (right panel)
Data: _q1_ce.pkl (counterexample) + b26.locate (golden example)
In-figure numbers: 110.59 / 116.92 / 58.46 / 2.00
"""
import os, sys, math, pickle
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle, FancyArrowPatch
from _pub import *
from b26 import locate

R_DOM = 1800.0

def bearing(s, g):
    return math.degrees(math.atan2(g[1] - s[1], g[0] - s[0])) % 360.0

def diameter_endpoints(reg):
    best, pa, pb = -1, None, None
    for i in range(len(reg)):
        for j in range(i + 1, len(reg)):
            d = math.dist(reg[i], reg[j])
            if d > best:
                best, pa, pb = d, reg[i], reg[j]
    return best, pa, pb

def draw(src_dir):
    fig = canvas(78)

    # ---- Golden example (left panel) ----
    S1 = (0.0, 0.0); S2 = (0.0, 1000.0); G = (1000.0, 0.0)
    w1 = locate.wedge_poly(S1, bearing(S1, G), R_DOM)
    w2 = locate.wedge_poly(S2, bearing(S2, G), R_DOM)
    reg_gold = locate.intersect(w1, w2)
    D_gold, a_gold, b_gold = diameter_endpoints(reg_gold)
    c_gold = ((a_gold[0] + b_gold[0]) / 2, (a_gold[1] + b_gold[1]) / 2)
    r_gold = D_gold / 2

    # ---- Counterexample (right panel) ----
    with open(os.path.join(os.path.dirname(src_dir), "_q1_ce.pkl"), "rb") as f:
        ce = pickle.load(f)
    reg_ce = ce["P"]
    D_ce = ce["Dm"]
    r_ce = D_ce / 2.0  # diameter-circle radius = D/2 = 58.46 m (NOT min-covering radius)
    a_ce = ce["a"]; b_ce = ce["b"]
    c_ce = ce["M"]  # diameter-circle center = midpoint of AB (NOT min-covering center)
    viol = ce["viol"][0]
    over = ce["over"]

    # Layout: two equal panels
    MARGIN_X = 6.0
    GAP = 6.0
    PW = (W_STD - 2 * MARGIN_X - GAP) / 2.0
    PANEL_Y = 4.0
    PANEL_H = 58.0
    LABEL_Y = 66.0

    # Equal scale: use counterexample bounds (larger), centered on each circle center
    VIEW_HALF = max(r_ce, r_gold) * 1.45 + 5  # ~90 m

    def draw_panel(px, reg, a, b, c, r, D, is_success, viol_pt=None, over_dist=None):
        a_ax = ax(fig, px, PANEL_Y, PW, PANEL_H)
        eq(a_ax, (c[0] - VIEW_HALF, c[0] + VIEW_HALF),
           (c[1] - VIEW_HALF, c[1] + VIEW_HALF))

        # Diameter circle (dashed)
        circle_color = C_GREEN if is_success else C_RED
        a_ax.add_patch(Circle(c, r, fill=False, edgecolor=circle_color,
                               lw=LW_MID, ls=(0, (4, 3)), zorder=3))

        # Diameter line (thin solid)
        a_ax.plot([a[0], b[0]], [a[1], b[1]], color=C_DARK,
                  lw=LW_THIN, ls="-", zorder=4)

        # Region (orange)
        a_ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.55,
                              edgecolor=C_ORANGE, lw=LW_MID, zorder=5))

        # Vertices
        for p in reg:
            is_viol = (viol_pt is not None and
                       abs(p[0] - viol_pt[0]) < 0.01 and abs(p[1] - viol_pt[1]) < 0.01)
            if is_viol:
                # Red square (shape + color dual encoding)
                a_ax.plot(*p, marker="s", ms=7.0, color=C_RED,
                          markeredgecolor=C_DARK, markeredgewidth=0.5, zorder=8)
            else:
                a_ax.plot(*p, marker="o", ms=3.5, color=C_ORANGE,
                          markeredgecolor=C_DARK, markeredgewidth=0.3, zorder=6)

        # Diameter endpoints A, B
        a_ax.plot(*a, marker="o", ms=5.0, color=C_DARK,
                  markeredgecolor="white", markeredgewidth=0.5, zorder=7)
        a_ax.plot(*b, marker="o", ms=5.0, color=C_DARK,
                  markeredgecolor="white", markeredgewidth=0.5, zorder=7)

        # Panel label
        panel_label(a_ax, "(a)" if is_success else "(b)", loc="upper left", fs=FS_LABEL)

        # Status tag (top right)
        status = "covered" if is_success else "not covered"
        a_ax.text(0.96, 0.96, status, transform=a_ax.transAxes,
                  fontsize=FS_LABEL, color=circle_color, fontweight="bold",
                  ha="right", va="top")

        # Over-distance annotation for counterexample
        if viol_pt is not None and over_dist is not None:
            # Draw a short line from violator to circle boundary
            dx = viol_pt[0] - c[0]
            dy = viol_pt[1] - c[1]
            dist = math.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist
            edge_pt = (c[0] + ux * r, c[1] + uy * r)
            a_ax.plot([edge_pt[0], viol_pt[0]], [edge_pt[1], viol_pt[1]],
                      color=C_RED, lw=LW_MID, ls="-", zorder=7)
            # Label
            mid_pt = ((edge_pt[0] + viol_pt[0]) / 2, (edge_pt[1] + viol_pt[1]) / 2)
            a_ax.text(mid_pt[0] + 3, mid_pt[1], "%.2f m" % over_dist,
                      fontsize=FS_LABEL, color=C_RED, fontweight="bold",
                      ha="left", va="center", zorder=9)

        # D value below panel
        fig.text((px + PW / 2) / W_STD, (78 - LABEL_Y) / 78.0,
                 "D = %.2f m" % D,
                 fontsize=FS_NUM, color=C_ORANGE, fontweight="bold",
                 ha="center", va="top")
        if not is_success:
            fig.text((px + PW / 2) / W_STD, (78 - LABEL_Y + 6) / 78.0,
                     "R = %.2f m   outside = %.2f m" % (r, over_dist),
                     fontsize=FS_LABEL, color=C_RED, fontweight="bold",
                     ha="center", va="top")

    # Left: success
    draw_panel(MARGIN_X, reg_gold, a_gold, b_gold, c_gold, r_gold,
               D_gold, is_success=True)
    # Right: failure
    draw_panel(MARGIN_X + PW + GAP, reg_ce, a_ce, b_ce, c_ce, r_ce,
               D_ce, is_success=False, viol_pt=viol, over_dist=over)

    print("Fig.3  gold D=%.2f  ce D=%.2f  R=%.2f  over=%.2f" %
          (D_gold, D_ce, r_ce, over))
    out = os.path.join(os.path.dirname(src_dir), "figures_final", "Fig03")
    return save(fig, out, "Fig03")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
