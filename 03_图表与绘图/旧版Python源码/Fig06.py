# -*- coding: utf-8 -*-
"""Fig.6  第二测点的候选区域：四重约束的交（165 x 96 mm）"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly
from _viz import *
from b26 import locate

R = 1800.0
RMIN, RMAX = 1000.0, 1500.0
RTIME = 1300.0
HALF = 34.0


def draw(src_dir):
    fig = canvas(96)
    ax = A(fig, 3, 3, 100, 68)
    eq(ax, (-R * 1.05, R * 1.05), (-R * 1.05, R * 1.05))
    ax.add_patch(MPoly(locate.disk_poly(0, 0, R), closed=True, facecolor="white",
                       edgecolor=C_GRAY, lw=LW_MID, zorder=1))
    wedge = locate.wedge_poly((0, 0), 0.0, R, delta=HALF)
    ax.add_patch(MPoly(wedge, closed=True, facecolor=C_BLUE, alpha=0.15,
                       edgecolor=C_BLUE, lw=LW_MID, zorder=2))
    ring = locate.intersect(locate.disk_poly(0, 0, RMAX), wedge)
    ax.add_patch(MPoly(ring, closed=True, facecolor=C_BLUE, alpha=0.10,
                       edgecolor=C_BLUE, lw=LW_THIN, ls=(0, (4, 3)), zorder=3))
    cen = locate.intersect(wedge, locate.disk_poly(0, 0, RMIN))
    ax.add_patch(MPoly(cen, closed=True, facecolor=C_ORANGE, alpha=0.55,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=5))
    tt = locate.intersect(wedge, locate.disk_poly(0, 0, RTIME))
    ax.add_patch(MPoly(tt, closed=True, facecolor="none", edgecolor=C_ORANGE,
                       lw=LW_MID, ls=(0, (2, 2)), zorder=6))
    ax.plot(0, 0, marker="o", ms=6, color=C_BLUE, zorder=9)
    ax.text(40, -140, "$S_1$", fontsize=FS_MATH, color=C_BLUE, fontweight="bold")
    ax.text(0, 190, "转角 ±%g°" % HALF, fontsize=FS_TINY, color=C_BLUE, ha="center")
    ax.text(-RMIN * 0.72, RMIN * 0.72, "$r\\leq 1000$ m\n一定能测到", fontsize=FS_TINY,
            color=C_BLUE, ha="center", va="center", fontweight="bold")
    ax.text(RMAX * 0.80, -RMAX * 0.42, "1000~1500 m\n可能测到", fontsize=FS_TINY,
            color=C_GRAY, ha="center", va="center")
    ax.text(-RTIME * 0.78, -RTIME * 0.50, "来得及走", fontsize=FS_TINY,
            color=C_ORANGE, ha="center", va="center")
    ax.text(0.5, 0.035, "深色 = 候选区域  A ∩ B ∩ C ∩ D", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_ORANGE, ha="center", va="bottom", fontweight="bold")
    ax.text(0.99, 0.99, "示意，未按比例", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="right", va="top")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    ax = A(fig, 106, 3, 56, 68)
    box(ax, ec=C_GRAY_L, lw=LW_MID)
    rows = [
        (C_BLUE,   "A  夹角带",     "从 $S_1$ 看过去，\n交会角落在可用区间内"),
        (C_BLUE,   "B  一定能测到", "$r\\leq r_{\\min}=1000$ m\n（接收半径的【下界】）"),
        (C_ORANGE, "C  来得及走",   "到 $S_1$ 的距离在\n时间预算之内"),
        (C_GRAY,   "D  坐标合法",   "$|x|,|y|\\leq 2000000$ m\n远小于本方案取值"),
    ]
    for i, (c, t, d) in enumerate(rows):
        y = 0.875 - i * 0.215
        ax.plot([0.04], [y], marker="s", ms=5, color=c, transform=ax.transAxes, zorder=6)
        ax.text(0.13, y, t, transform=ax.transAxes, fontsize=FS_BODY, color=c,
                va="center", fontweight="bold")
        ax.text(0.13, y - 0.085, d, transform=ax.transAxes, fontsize=FS_TINY,
                color="#555555", va="top")
    ax.text(0.5, 0.975, "候选区域 = 四者的交集", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_DARK, ha="center", va="top", fontweight="bold")

    ax = A(fig, 3, 74, 159, 19)
    box(ax, ec=C_ORANGE, lw=LW_MID)
    ax.text(0.5, 0.70, "约束 B 为什么必须取 1000 m 而不是 1500 m", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_ORANGE, ha="center", va="center", fontweight="bold")
    ax.text(0.5, 0.28, "题面给出接收半径为 1000–1500 m，且接口不返回其真实值。"
                       "只有取【下界】1000 m，才能保证「无论该源的真实半径是多少都一定测得到」。",
            transform=ax.transAxes, fontsize=FS_TINY, color=C_DARK,
            ha="center", va="center")
    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig06")
    return save(fig, out, "Fig06")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
