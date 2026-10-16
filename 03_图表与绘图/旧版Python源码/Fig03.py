# -*- coding: utf-8 -*-
"""Fig.3  多测点交集压缩为凸多边形（画布 165 x 78 mm）
视觉焦点：橙色交集区域在四格中逐格缩小
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Arc
from _viz import *
from b26 import locate

R = 1800.0
S1 = (0.0, 0.0); S2 = (0.0, 1000.0); S3 = (1500.0, -800.0); G = (1000.0, 0.0)
CW, CH, CY = (39, 39, 39, 33), 58, 3


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


def draw(src_dir):
    fig = canvas(78)
    XS = [3, 45, 87, 129]
    LBL = ["观测前", "1 个测点", "2 个测点", "3 个测点"]
    PAIRS = [[], [(S1, bearing(S1, G))], [(S1, bearing(S1, G)), (S2, bearing(S2, G))],
             [(S1, bearing(S1, G)), (S2, bearing(S2, G)), (S3, bearing(S3, G))]]
    dia = {}
    for i, x in enumerate(XS):
        w = CW[i]
        ax = A(fig, x, CY, w, CH)
        eq(ax, (-R * 1.05, R * 1.05), (-R * 1.05, R * 1.05))
        ax.add_patch(Arc((0, 0), 2 * R, 2 * R, theta1=0, theta2=360, color=C_GRAY, lw=LW_MID))
        for (s, t) in PAIRS[i]:
            ax.add_patch(MPoly(locate.wedge_poly(s, t, R), closed=True,
                               facecolor=C_BLUE, alpha=0.14, edgecolor="none", zorder=2))
        reg = region(PAIRS[i])
        if i == 0:
            ax.add_patch(Arc((0, 0), 2 * R, 2 * R, theta1=0, theta2=360,
                             color=C_ORANGE, lw=LW_THICK, zorder=5))
            ax.add_patch(Arc((0, 0), 2 * R * 0.985, 2 * R * 0.985, theta1=0, theta2=360,
                             color=C_ORANGE, lw=6.0, alpha=0.45, zorder=4))
            dia[LBL[i]] = 3600.0
        elif reg:
            dia[LBL[i]] = locate.diameter(reg)
            ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.60,
                               edgecolor=C_ORANGE, lw=LW_THICK, zorder=6))
        for (s, t) in PAIRS[i]:
            ax.plot(*s, marker="o", ms=3.6, color=C_BLUE, zorder=8)
        if i == 3 and reg:
            for p in reg:
                ax.plot(*p, marker="o", ms=3.0, color=C_ORANGE, zorder=9)
            best, pa, pb = -1, None, None
            for a in range(len(reg)):
                for b in range(a + 1, len(reg)):
                    dd = math.dist(reg[a], reg[b])
                    if dd > best:
                        best, pa, pb = dd, reg[a], reg[b]
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], ls=(0, (3, 2)),
                    color=C_RED, lw=LW_THICK, zorder=10)
        ax.text(0.5, 0.965, LBL[i], transform=ax.transAxes, fontsize=FS_SUB,
                color=C_DARK, ha="center", va="top", fontweight="bold")
        ax.text(0.94, 0.055, "D = %.2f m" % dia[LBL[i]], transform=ax.transAxes,
                fontsize=FS_NUM if i else FS_NUM - 0.5, color=C_ORANGE,
                ha="right", va="bottom", fontweight="bold")
    # 放大插图（格 3 / 格 4）
    for (px, pr, pw) in ((88, PAIRS[2], 17), (130, PAIRS[3], 17)):
        ia = inset(fig, px, 40, pw, pw, frame=C_ORANGE, lw=LW_MID)
        rg = region(pr)
        if not rg:
            continue
        xs = [p[0] for p in rg]; ys = [p[1] for p in rg]
        cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
        h = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.9 + 8
        ia.set_xlim(cx - h, cx + h); ia.set_ylim(cy - h, cy + h)
        ia.add_patch(MPoly(rg, closed=True, facecolor=C_ORANGE, alpha=0.60,
                           edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
        for p in rg:
            ia.plot(*p, marker="o", ms=2.6, color=C_ORANGE, zorder=6)
    ax = A(fig, 3, 64, 159, 11)
    ax.text(0.5, 0.55, "约束越多，区域越小；而它永远是凸的 —— 直径必在顶点对之间取得",
            fontsize=FS_SUB, color=C_DARK, ha="center", va="center", fontweight="bold")
    box(ax, ec=C_GRAY_L, lw=LW_MID)
    print("Fig.3 D:", {k: round(v, 2) for k, v in dia.items()})
    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig03")
    return save(fig, out, "Fig03")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
