# -*- coding: utf-8 -*-
"""图 2  测向误差与可行域压缩   165 x 85 mm
视觉顺序：结构（四格圆域） -> 关系（橙色区域递减） -> 数字（直径）
图内非数字文字：一个读数 / 直径 / m  （共 <= 8 字）
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle, Arc
from _common import *
from b26 import locate

R = 1800.0
S1 = (0.0, 0.0); S2 = (0.0, 1000.0); S3 = (1500.0, -800.0); G = (1000.0, 0.0)


def bear(s, g):
    return math.degrees(math.atan2(g[1] - s[1], g[0] - s[0])) % 360.0


def region(pairs):
    poly = None
    for (s, t) in pairs:
        w = locate.wedge_poly(s, t, R)
        poly = w if poly is None else locate.intersect(poly, w)
        if not poly:
            return []
    return poly


def draw(src_dir):
    fig = canvas(85)
    X0, W, GAP, N = 3.0, 159.0, 3.0, 4
    CW = (W - (N - 1) * GAP) / N
    PAIRS = [[], [(S1, bear(S1, G))],
             [(S1, bear(S1, G)), (S2, bear(S2, G))],
             [(S1, bear(S1, G)), (S2, bear(S2, G)), (S3, bear(S3, G))]]
    DIA = []
    for i in range(N):
        x = X0 + i * (CW + GAP)
        ax = A(fig, x, 5, CW, 50)
        eq(ax, (-R * 1.04, R * 1.04), (-R * 1.04, R * 1.04))
        ax.add_patch(Circle((0, 0), R, facecolor="none", edgecolor=C_GRAY, lw=LW_THIN))
        reg = region(PAIRS[i])
        if i == 0:
            ax.add_patch(Circle((0, 0), R, facecolor=C_ORANGE, alpha=0.35,
                                edgecolor=C_ORANGE, lw=LW_THICK, zorder=3))
            DIA.append(3600.0)
        else:
            for (s, t) in PAIRS[i]:
                ax.add_patch(MPoly(locate.wedge_poly(s, t, R), closed=True,
                                   facecolor=C_BLUE, alpha=0.13, edgecolor="none", zorder=2))
            if reg:
                DIA.append(locate.diameter(reg))
                ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.70,
                                   edgecolor=C_ORANGE, lw=LW_THICK, zorder=5))
            for (s, t) in PAIRS[i]:
                ax.plot(*s, marker="o", ms=3.0, color=C_BLUE, zorder=8)
        ax.text(0.5, 0.99, "%d" % i, transform=ax.transAxes, fontsize=FS_SUB + 1.5,
                color=C_DARK, ha="center", va="top", fontweight="bold")
        if i == 1:
            ax.text(0.63, 0.40, r"$\pm 1^\circ$", transform=ax.transAxes,
                    fontsize=FS_MATH, color=C_RED, fontweight="bold")
        if i == 3 and reg:
            for p in reg:
                ax.plot(*p, marker="o", ms=2.4, color=C_ORANGE, zorder=9)
            best, pa, pb = -1, None, None
            for a in range(len(reg)):
                for b in range(a + 1, len(reg)):
                    dd = math.dist(reg[a], reg[b])
                    if dd > best:
                        best, pa, pb = dd, reg[a], reg[b]
            ux = (pb[0] - pa[0]) / best; uy = (pb[1] - pa[1]) / best
            L = 0.62 * R
            ax.plot([-ux * L, ux * L], [-uy * L, uy * L], ls=(0, (3, 2)),
                    color=C_RED, lw=LW_THICK, zorder=10)

    ax = A(fig, X0, 60, W, 21)
    for i in range(N):
        xf = (i * (CW + GAP) + CW / 2.0) / W
        ax.text(xf, 0.68, ("%.2f" % DIA[i]).rstrip("0").rstrip("."),
                transform=ax.transAxes, fontsize=FS_NUM + 2.5, color=C_ORANGE,
                ha="center", va="center", fontweight="bold")
        ax.text(xf, 0.18, "m", transform=ax.transAxes, fontsize=FS_TINY,
                color=C_GRAY, ha="center", va="center")

    print("F2 diameters:", [round(v, 2) for v in DIA])
    return save(fig, out("F2"), "F2")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
