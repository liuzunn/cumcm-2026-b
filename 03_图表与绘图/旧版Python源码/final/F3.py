# -*- coding: utf-8 -*-
"""图 3  直径圆覆盖命题的 1.73% 反例   165 x 80 mm
图内非数字文字：能 / 不能 / 圆半径 （共 <= 6 字）
"""
import os, sys, math, pickle
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle
from _common import *
from b26 import locate

TEACH = r"D:\BaiduNetdiskDownload\数学建模\_teach"


def diam(poly):
    best, pa, pb = -1, None, None
    for i in range(len(poly)):
        for j in range(i + 1, len(poly)):
            dd = math.dist(poly[i], poly[j])
            if dd > best:
                best, pa, pb = dd, poly[i], poly[j]
    return best, pa, pb


def draw(src_dir):
    fig = canvas(80)

    # ---------- 左：能 ----------
    ax = A(fig, 3, 4, 77, 54)
    S1 = (0.0, 0.0); S2 = (0.0, 1000.0); G = (1000.0, 0.0)
    t1 = math.degrees(math.atan2(G[1] - S1[1], G[0] - S1[0])) % 360
    t2 = math.degrees(math.atan2(G[1] - S2[1], G[0] - S2[0])) % 360
    reg = locate.intersect(locate.wedge_poly(S1, t1), locate.wedge_poly(S2, t2))
    Dg, ag, bg = diam(reg)
    M = ((ag[0] + bg[0]) / 2, (ag[1] + bg[1]) / 2)
    reg = [(p[0] - M[0], p[1] - M[1]) for p in reg]
    ag = (ag[0] - M[0], ag[1] - M[1]); bg = (bg[0] - M[0], bg[1] - M[1])
    eq(ax, (-92, 92), (-92, 92))
    ax.add_patch(Circle((0, 0), Dg / 2, facecolor=C_GREEN, alpha=0.14,
                        edgecolor=C_GREEN, lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.60,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
    ax.plot([ag[0], bg[0]], [ag[1], bg[1]], ls=(0, (3, 2)), color=C_RED,
            lw=LW_THICK, zorder=6)
    for p in reg:
        ax.plot(*p, marker="o", ms=3.4, color=C_GREEN, zorder=7)
    ax.text(0.5, 0.99, "能", transform=ax.transAxes, fontsize=FS_SUB + 1.0,
            color=C_GREEN, ha="center", va="top", fontweight="bold")
    ax.text(0.5, 0.02, "%.2f m" % Dg, transform=ax.transAxes, fontsize=FS_NUM + 1.0,
            color=C_ORANGE, ha="center", va="bottom", fontweight="bold")

    # ---------- 右：不能 ----------
    ce = pickle.load(open(os.path.join(TEACH, "_q1_ce.pkl"), "rb"))
    Pc, ac, bc, Dc, Mc, viol, over = ce["P"], ce["a"], ce["b"], ce["Dm"], ce["M"], ce["viol"][0], ce["over"]
    sh = [(p[0] - Mc[0], p[1] - Mc[1]) for p in Pc]
    ac2 = (ac[0] - Mc[0], ac[1] - Mc[1]); bc2 = (bc[0] - Mc[0], bc[1] - Mc[1])
    v2 = (viol[0] - Mc[0], viol[1] - Mc[1])
    ax = A(fig, 85, 4, 66, 54)
    lim = 1.38 * Dc / 2
    eq(ax, (-lim, lim), (-lim, lim))
    ax.add_patch(Circle((0, 0), Dc / 2, facecolor=C_RED, alpha=0.11,
                        edgecolor=C_RED, lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    ax.add_patch(MPoly(sh, closed=True, facecolor=C_ORANGE, alpha=0.60,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
    ax.plot([ac2[0], bc2[0]], [ac2[1], bc2[1]], ls=(0, (3, 2)), color=C_RED,
            lw=LW_THICK, zorder=6)
    for p in sh:
        ax.plot(*p, marker="o", ms=3.2, color=C_ORANGE, zorder=7)
    ax.plot(*v2, marker="o", ms=7.5, color=C_RED, zorder=9)
    ax.text(0.5, 0.99, "不能", transform=ax.transAxes, fontsize=FS_SUB + 1.0,
            color=C_RED, ha="center", va="top", fontweight="bold")
    ax.text(0.5, 0.02, "%.2f m" % Dc, transform=ax.transAxes, fontsize=FS_NUM + 1.0,
            color=C_ORANGE, ha="center", va="bottom", fontweight="bold")
    iv = inset(fig, 85.5, 36.5, 17, 17, frame=C_RED, lw=LW_MID)
    iv.add_patch(Circle((0, 0), Dc / 2, facecolor="none", edgecolor=C_RED,
                        lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    iv.add_patch(MPoly([(p[0] - v2[0], p[1] - v2[1]) for p in sh], closed=True,
                       facecolor=C_ORANGE, alpha=0.60, edgecolor=C_ORANGE,
                       lw=LW_MID, zorder=4))
    iv.plot(0, 0, marker="o", ms=5, color=C_RED, zorder=9)
    iv.plot([-9, 9], [0, 0], ls=(0, (2, 2)), color=C_RED, lw=LW_THIN, zorder=8)
    iv.set_xlim(-9.5, 9.5); iv.set_ylim(-9.5, 9.5)

    # ---------- 底：判据 + 比例条 ----------
    ax = A(fig, 3, 62, 159, 15)
    ax.text(0.0, 0.82, r"$(\mathbf{a}-\mathbf{v})\cdot(\mathbf{b}-\mathbf{v})\leq 0$",
            transform=ax.transAxes, fontsize=FS_MATH + 1.5, color=C_DARK,
            ha="left", va="center")
    ax.text(0.0, 0.24, r"$\forall\,\mathbf{v}\in V$", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="left", va="center")
    ax.text(0.30, 0.82, "29.84 m", transform=ax.transAxes, fontsize=FS_NUM,
            color=C_RED, ha="left", va="center", fontweight="bold")
    ax.text(0.30, 0.24, "圆半径", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_GRAY, ha="left", va="center")
    ax.add_patch(plt.Rectangle((0.52, 0.20), 0.40, 0.44, transform=ax.transAxes,
                               facecolor="#ececec", edgecolor="none", zorder=2))
    ax.add_patch(plt.Rectangle((0.52, 0.20), 0.40 * 0.0173, 0.44, transform=ax.transAxes,
                               facecolor=C_RED, edgecolor="none", zorder=3))
    ax.text(0.94, 0.42, "1.73%", transform=ax.transAxes, fontsize=FS_NUM + 1.0,
            color=C_RED, ha="left", va="center", fontweight="bold")
    return save(fig, out("F3"), "F3")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
