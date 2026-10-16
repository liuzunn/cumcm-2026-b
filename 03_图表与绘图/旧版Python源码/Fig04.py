# -*- coding: utf-8 -*-
"""Fig.4  以定位区域直径为直径的圆不能保证覆盖（画布 165 x 106 mm）"""
import os, sys, math, pickle
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle
from _viz import *

TEACH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dstr(p):
    best, pa, pb = -1, None, None
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            dd = math.dist(p[i], p[j])
            if dd > best:
                best, pa, pb = dd, p[i], p[j]
    M = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
    return best, pa, pb, M


def draw(src_dir):
    fig = canvas(106)
    ce = pickle.load(open(os.path.join(TEACH, "_q1_ce.pkl"), "rb"))
    Pc = ce["P"]; ac = ce["a"]; bc = ce["b"]; Dc = ce["Dm"]; Mc = ce["M"]
    viol = ce["viol"][0]; over = ce["over"]

    # ---------- 左栏：能覆盖（黄金算例 D = 110.59 m）----------
    ax = A(fig, 3, 3, 52, 58)
    eq(ax, (-120, 120), (-120, 120))
    S1 = (0.0, 0.0); S2 = (0.0, 1000.0); Gq = (1000.0, 0.0)
    t1 = math.degrees(math.atan2(Gq[1] - S1[1], Gq[0] - S1[0])) % 360
    t2 = math.degrees(math.atan2(Gq[1] - S2[1], Gq[0] - S2[0])) % 360
    from b26 import locate
    reg = locate.intersect(locate.wedge_poly(S1, t1), locate.wedge_poly(S2, t2))
    Dg, ag, bg, Mg = dstr(reg)
    reg = [(p[0] - Mg[0], p[1] - Mg[1]) for p in reg]
    ag = (ag[0] - Mg[0], ag[1] - Mg[1]); bg = (bg[0] - Mg[0], bg[1] - Mg[1])
    ax.add_patch(Circle((0, 0), Dg / 2, facecolor=C_GREEN, alpha=0.13,
                        edgecolor=C_GREEN, lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    ax.add_patch(MPoly(reg, closed=True, facecolor=C_ORANGE, alpha=0.55,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
    ax.plot([ag[0], bg[0]], [ag[1], bg[1]], ls=(0, (3, 2)), color=C_RED,
            lw=LW_THICK, zorder=6)
    for p, lb, of in ((ag, "a", (5, 6)), (bg, "b", (5, -12))):
        ax.plot(*p, marker="o", ms=4, color=C_RED, zorder=7)
        ax.text(p[0] + of[0], p[1] + of[1], lb, fontsize=FS_MATH, color=C_RED,
                fontweight="bold")
    for p in reg:
        ax.plot(*p, marker="o", ms=3, color=C_GREEN, zorder=7)
    ax.text(0.5, 0.965, "能覆盖", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_GREEN, ha="center", va="top", fontweight="bold")
    ax.text(0.5, 0.055, "四个顶点全在圆内或圆上", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GREEN, ha="center", va="bottom")
    ax.text(0.5, 0.99, "D = %.2f m" % Dg, transform=ax.transAxes,
            fontsize=FS_NUM - 1.0, color=C_ORANGE, ha="center", va="bottom", fontweight="bold")

    # ---------- 中栏：最强反例（数字卡）----------
    ax = A(fig, 57, 3, 52, 58)
    box(ax, ec=C_RED, lw=LW_THICK, fc="white")
    ax.text(0.5, 0.90, "最强反例", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_RED, ha="center", va="center", fontweight="bold")
    ax.text(0.5, 0.74, r"$\alpha=90.04^\circ$", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.text(0.5, 0.62, "D = 59.65 m", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.text(0.5, 0.48, "圆半径 D/2 = 29.825 m", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.text(0.5, 0.36, "最小覆盖圆半径 = 29.84 m", transform=ax.transAxes,
            fontsize=FS_MATH, color=C_DARK, ha="center", va="center")
    ax.plot([0.10, 0.90], [0.29, 0.29], transform=ax.transAxes, color=C_RED, lw=LW_THICK)
    ax.text(0.5, 0.175, "差 0.015 m  →  盖不住", transform=ax.transAxes,
            fontsize=FS_NUM, color=C_RED, ha="center", va="center", fontweight="bold")
    ax.text(0.5, 0.055, "超出量仅 1.5 cm，无法在图内按比例显示", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="center", va="center")

    # ---------- 右栏：直观反例（几何 + 顶点级放大）----------
    ax = A(fig, 111, 3, 51, 58)
    m2 = dstr(Pc)[3]
    sh = [(p[0] - m2[0], p[1] - m2[1]) for p in Pc]
    ac2 = (ac[0] - m2[0], ac[1] - m2[1]); bc2 = (bc[0] - m2[0], bc[1] - m2[1])
    v2 = (viol[0] - m2[0], viol[1] - m2[1])
    eq(ax, (-1.6 * Dc / 2, 1.6 * Dc / 2), (-1.6 * Dc / 2, 1.6 * Dc / 2))
    ax.add_patch(Circle((0, 0), Dc / 2, facecolor=C_RED, alpha=0.10,
                        edgecolor=C_RED, lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    ax.add_patch(MPoly(sh, closed=True, facecolor=C_ORANGE, alpha=0.55,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=4))
    ax.plot([ac2[0], bc2[0]], [ac2[1], bc2[1]], color=C_RED, lw=LW_THICK, zorder=6)
    for p in sh:
        ax.plot(*p, marker="o", ms=3, color=C_ORANGE, zorder=7)
    ax.plot(*v2, marker="o", ms=6, color=C_RED, zorder=9)
    ax.text(0.5, 0.965, "直观反例", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_RED, ha="center", va="top", fontweight="bold")
    ax.text(0.5, 0.99, "D = %.2f m，顶点跑到圆外 %.2f m" % (Dc, over),
            transform=ax.transAxes, fontsize=FS_TINY, color=C_RED,
            ha="center", va="bottom")
    iv = inset(fig, 113, 41, 20, 20, frame=C_RED, lw=LW_MID)
    iv.add_patch(Circle((0, 0), Dc / 2, facecolor="none", edgecolor=C_RED,
                        lw=LW_THICK, ls=(0, (5, 3)), zorder=2))
    iv.add_patch(MPoly([(p[0] - v2[0], p[1] - v2[1]) for p in sh], closed=True,
                       facecolor=C_ORANGE, alpha=0.55, edgecolor=C_ORANGE,
                       lw=LW_MID, zorder=4))
    iv.plot(0, 0, marker="o", ms=4, color=C_RED, zorder=9)
    iv.set_xlim(-9, 9); iv.set_ylim(-9, 9)
    iv.set_title("放大", fontsize=FS_TINY, color=C_RED, pad=1.5)

    # ---------- 判据条 ----------
    ax = A(fig, 3, 64, 159, 16)
    ax.text(0.5, 0.72, r"$(\mathbf{a}-\mathbf{v})\cdot(\mathbf{b}-\mathbf{v})\leq 0\ \ \forall \mathbf{v}\in V$"
                       r"   $\Longleftrightarrow$   $\angle\mathbf{a}\mathbf{v}\mathbf{b}\geq 90^\circ$"
                       r"   $\Longleftrightarrow$   $\mathbf{v}$ 在圆内或圆上",
            transform=ax.transAxes, fontsize=FS_MATH + 1.0, color=C_DARK,
            ha="center", va="center")
    ax.text(0.5, 0.22, "逐个检查每个顶点看直径两端 a、b 的夹角；只要有一个小于 90°，就盖不住",
            transform=ax.transAxes, fontsize=FS_BODY, color=C_DARK,
            ha="center", va="center", fontweight="bold")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    # ---------- 保底 + 统计条 ----------
    ax = A(fig, 3, 83, 78, 20)
    box(ax, ec=C_GREEN, lw=LW_MID)
    ia = inset(fig, 6, 86, 14, 14)
    ia.add_patch(Circle((0, 0), 1.0, facecolor="none", edgecolor=C_RED, lw=LW_MID))
    ia.add_patch(Circle((0, 0), 1.1547, facecolor="none", edgecolor=C_GREEN,
                        lw=LW_MID, ls=(0, (3, 2))))
    ia.set_xlim(-1.4, 1.4); ia.set_ylim(-1.4, 1.4)
    ax.text(0.30, 0.62, "半径 D/√3 的圆一定够", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_GREEN, va="center", fontweight="bold")
    ax.text(0.30, 0.26, "比 D/2 大 15.47%", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, va="center")

    ax = A(fig, 84, 83, 78, 20)
    box(ax, ec=C_RED, lw=LW_MID)
    ax.add_patch(MPoly([(0.05, 0.34), (0.95, 0.34), (0.95, 0.52), (0.05, 0.52)],
                       closed=True, transform=ax.transAxes, facecolor="#ececec",
                       edgecolor="none", zorder=2))
    ax.add_patch(MPoly([(0.05, 0.34), (0.05 + 0.90 * 0.0173, 0.34),
                        (0.05 + 0.90 * 0.0173, 0.52), (0.05, 0.52)], closed=True,
                       transform=ax.transAxes, facecolor=C_RED, edgecolor="none", zorder=3))
    ax.text(0.5, 0.70, "197 745 组良态配置 → 3 422 组不可覆盖 = 1.73%",
            transform=ax.transAxes, fontsize=FS_BODY, color=C_DARK,
            ha="center", va="center", fontweight="bold")
    ax.text(0.5, 0.15, "反例很少，但确实存在", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_RED, ha="center", va="center")

    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig04")
    return save(fig, out, "Fig04")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
