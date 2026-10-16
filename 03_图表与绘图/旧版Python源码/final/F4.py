# -*- coding: utf-8 -*-
"""图 4  第二测点：候选区域与策略选择   165 x 90 mm
图内非数字文字：A B C D / 质心 / 动态 / s  （<= 10 字）
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle
from _common import *
from b26 import locate

R, RMIN, RMAX, RTIME, HALF = 1800.0, 1000.0, 1500.0, 1300.0, 34.0
ARMS = [("质心", 488.2, True), ("动态", 531.9, False),
        ("90°", 609.7, False), ("54.7°", 675.3, False)]


def draw(src_dir):
    fig = canvas(90)

    # ---------- 左：候选区域 ----------
    ax = A(fig, 3, 4, 70, 82)
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
    ax.add_patch(MPoly(cen, closed=True, facecolor=C_ORANGE, alpha=0.62,
                       edgecolor=C_ORANGE, lw=LW_THICK, zorder=5))
    tt = locate.intersect(wedge, locate.disk_poly(0, 0, RTIME))
    ax.add_patch(MPoly(tt, closed=True, facecolor="none", edgecolor=C_ORANGE,
                       lw=LW_MID, ls=(0, (2, 2)), zorder=6))
    ax.plot(0, 0, marker="o", ms=6, color=C_BLUE, zorder=9)
    ax.text(0.50, 0.965, "A", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_BLUE, ha="center", va="top", fontweight="bold")
    ax.text(0.50, 0.035, "B", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_BLUE, ha="center", va="bottom", fontweight="bold")
    ax.text(0.13, 0.50, "C", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_ORANGE, ha="center", va="center", fontweight="bold")
    ax.text(0.90, 0.50, "D", transform=ax.transAxes, fontsize=FS_SUB,
            color=C_GRAY, ha="center", va="center", fontweight="bold")

    # ---------- 右：策略对照 ----------
    ax = A(fig, 78, 4, 84, 82)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    vmax = 700.0
    for i, (nm, v, keep) in enumerate(ARMS):
        y = 0.80 - i * 0.185
        col = C_GREEN if keep else C_RED
        w = 0.62 * v / vmax
        ax.add_patch(Rectangle((0.20, y - 0.055), w, 0.11,
                               facecolor=col, alpha=(0.75 if keep else 0.35),
                               edgecolor=col, lw=(LW_THICK if keep else LW_MID), zorder=3))
        ax.text(0.175, y, nm, fontsize=FS_BODY, color=(C_GREEN if keep else "#555555"),
                ha="right", va="center", fontweight=("bold" if keep else "normal"))
        ax.text(0.21 + w + 0.02, y, "%.1f  s" % v, fontsize=FS_NUM,
                color=col, ha="left", va="center", fontweight="bold")
    ax.plot([0.20, 0.20], [0.06, 0.88], color=C_GRAY, lw=LW_THIN)

    return save(fig, out("F4"), "F4")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
