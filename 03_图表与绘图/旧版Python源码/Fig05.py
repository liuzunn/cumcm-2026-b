# -*- coding: utf-8 -*-
"""Fig.5  定位误差的几何来源：两条误差带相交所得平行四边形的长对角线（165 x 100 mm）"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly
from _viz import *
from b26 import locate

DELTA = math.radians(1.0)
S1 = (-1000.0, 0.0); S2 = (0.0, 1414.0); G = (0.0, 0.0)


def bear(s, g):
    return math.degrees(math.atan2(g[1] - s[1], g[0] - s[0])) % 360.0


def draw(src_dir):
    fig = canvas(100)
    t1 = bear(S1, G); t2 = bear(S2, G)
    w1 = locate.wedge_poly(S1, t1, 3000.0)
    w2 = locate.wedge_poly(S2, t2, 3000.0)
    reg = locate.intersect(w1, w2)
    D = locate.diameter(reg)
    xs = [p[0] for p in reg]; ys = [p[1] for p in reg]
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    best, pa, pb = -1, None, None
    for i in range(len(reg)):
        for j in range(i + 1, len(reg)):
            dd = math.dist(reg[i], reg[j])
            if dd > best:
                best, pa, pb = dd, reg[i], reg[j]

    ax = A(fig, 3, 3, 108, 66)
    eq(ax, (cx - 45, cx + 45), (cy - 45, cy + 45))
    ax.add_patch(MPoly(w1, closed=True, facecolor=C_BLUE, alpha=0.14,
                       edgecolor=C_BLUE, lw=LW_MID, zorder=2))
    ax.add_patch(MPoly(w2, closed=True, facecolor=C_BLUE, alpha=0.14,
                       edgecolor=C_BLUE, lw=LW_MID, zorder=2))
    ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.55,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=5))
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], ls=(0, (3, 2)), color=C_RED,
            lw=LW_THICK, zorder=8)
    ax.plot(*G, marker="*", ms=11, color=C_ORANGE, zorder=9)
    ax.text(G[0] + 3, G[1] - 11, "源 G", fontsize=FS_BODY, color=C_ORANGE, fontweight="bold")
    ax.text(0.035, 0.965, "误差带 1（宽 $2\\delta d_1$）", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_BLUE, ha="left", va="top")
    ax.text(0.035, 0.10, "误差带 2\n（宽 $2\\delta d_2$）", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_BLUE, ha="left", va="bottom")
    ax.text(0.97, 0.90, "D = %.2f m" % D, transform=ax.transAxes, fontsize=FS_NUM - 1.0,
            color=C_RED, ha="right", va="top", fontweight="bold")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    gi = inset(fig, 85, 28, 24, 24, frame=C_GRAY, lw=LW_THIN)
    gi.plot([S1[0], G[0]], [S1[1], G[1]], color=C_BLUE, lw=LW_THIN)
    gi.plot([S2[0], G[0]], [S2[1], G[1]], color=C_BLUE, lw=LW_THIN)
    gi.plot(*S1, marker="o", ms=3, color=C_BLUE); gi.plot(*S2, marker="o", ms=3, color=C_BLUE)
    gi.plot(*G, marker="*", ms=8, color=C_ORANGE)
    gi.text(S1[0] - 40, S1[1] - 200, "$S_1$", fontsize=FS_TINY, color=C_BLUE)
    gi.text(S2[0] + 60, S2[1] + 60, "$S_2$", fontsize=FS_TINY, color=C_BLUE)
    gi.set_xlim(-1350, 1350); gi.set_ylim(-1350, 1850)

    ax = A(fig, 113, 3, 49, 30)
    eq(ax, (0, 180), (0, 105), asp="auto")
    dd = [i * 2 for i in range(91)]
    ax.plot(dd, [0.049365 * x for x in dd], lw=LW_THICK, color=C_BLUE)
    ax.plot([81.03], [40], marker="o", ms=5, color=C_RED, zorder=6)
    ax.plot([0, 180], [40, 40], ls=(0, (3, 2)), color=C_RED, lw=LW_THIN)
    ax.text(0.06, 0.90, "$D \\propto d$ 严格线性", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_BLUE, va="top", fontweight="bold")
    ax.text(0.94, 0.62, "斜率 $2\\sqrt{2}\\delta$", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="right")
    box(ax, ec=C_GRAY_L, lw=LW_THIN)

    ax = A(fig, 113, 35, 49, 34)
    ax.text(0.5, 0.94, "误差由三个量共同决定", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_DARK, ha="center", va="top", fontweight="bold")
    ax.text(0.5, 0.70, "$\\alpha = 90^\\circ$   (本图算例)", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.text(0.5, 0.52, "$d_1 = 1000$ m,  $d_2 = 1414$ m", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.text(0.5, 0.30, "$D\\propto d$ 线性，$D$ 对 $\\alpha$ 呈 U 形", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="center", va="center")
    ax.text(0.5, 0.12, "解析式与精确裁剪差 < 1%", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="center", va="center")
    box(ax, ec=C_GRAY_L, lw=LW_THIN)

    ax = A(fig, 3, 72, 159, 13)
    ax.text(0.30, 0.5,
            r"$D=\frac{2\delta}{\sin\alpha}\sqrt{d_1^2+d_2^2+2d_1d_2|\cos\alpha|}$",
            transform=ax.transAxes, fontsize=FS_MATH + 1.5, color=C_DARK,
            ha="center", va="center")
    ax.text(0.60, 0.5, "等距退化", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_GRAY, ha="center", va="center")
    ax.text(0.83, 0.5, r"$D=\frac{2\delta d}{\sin(\alpha/2)}$", transform=ax.transAxes,
            fontsize=FS_MATH + 1.5, color=C_ORANGE, ha="center", va="center",
            fontweight="bold")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    ax = A(fig, 3, 88, 159, 10)
    ax.text(0.5, 0.55, "误差的主导变量是【距离】而不是夹角 —— 这一条决定了 Q2 的全部策略",
            transform=ax.transAxes, fontsize=FS_BODY, color=C_DARK,
            ha="center", va="center", fontweight="bold")
    print("Fig.5 D =", round(D, 2), "alpha =", round(math.degrees(math.acos(
        ((S1[0]) * (S2[0]) + (S1[1]) * (S2[1])) /
        (math.hypot(*S1) * math.hypot(*S2)))), 2))
    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig05")
    return save(fig, out, "Fig05")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
