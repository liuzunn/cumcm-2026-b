# -*- coding: utf-8 -*-
"""图 6  定向源：覆盖不等于可见，与未知朝向的消去   165 x 95 mm
图内非数字文字：未知 / 估计 / 成本 / 判据  （<= 12 字）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from _common import *


def node(ax, x, y, w, h, txt, ec, fc, tc, fs=None, lw=None, z=4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.35",
                 facecolor=fc, edgecolor=ec, lw=(lw or LW_THICK), zorder=z,
                 transform=ax.transData))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
            fontsize=(fs or FS_SUB), color=tc, zorder=z + 1)


def arrow(ax, p, q, col=C_GRAY, lw=LW_MID):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", color=col, lw=lw,
                 mutation_scale=10, zorder=3))


def draw(src_dir):
    fig = canvas(95)
    ax = A(fig, 3, 3, 159, 89)
    ax.set_xlim(0, 159); ax.set_ylim(0, 89)
    ax.invert_yaxis()
    ax.axis("off")

    # 顶部：beta 未知
    node(ax, 60, 2, 39, 15, r"$\beta$  未知", C_DARK, "white", C_DARK, fs=FS_SUB + 1.0)
    # 分叉
    arrow(ax, (79.5, 17), (79.5, 24), C_GRAY)
    ax.plot([22, 137], [24, 24], color=C_GRAY, lw=LW_MID, zorder=2)
    arrow(ax, (22, 24), (22, 30), C_RED)
    arrow(ax, (137, 24), (137, 30), C_BLUE)

    # 左支（被淘汰）
    node(ax, 3, 31, 38, 15, r"估计 $\beta$", C_GRAY, "#f2f2f2", "#666666")
    arrow(ax, (22, 46), (22, 53), C_GRAY)
    node(ax, 3, 54, 38, 15, "成本", C_GRAY, "#f2f2f2", "#666666")
    ax.plot([4, 41], [70, 30], color=C_RED, lw=LW_THICK, zorder=6,
            solid_capstyle="butt")
    ax.plot([4, 41], [70, 30], color=C_RED, lw=LW_THICK, zorder=6,
            solid_capstyle="butt", alpha=0.0)
    for xa, ya in ((4, 70), (41, 30)):
        ax.plot([xa - 1.2, xa + 1.2], [ya - 1.6, ya + 1.6], color=C_RED,
                lw=LW_THICK, zorder=6)

    # 右支（采用）
    xs = [46, 78, 110]
    labels = [r"$\forall\beta$", r"$E(S)$", "判据"]
    for i, (xx, lb) in enumerate(zip(xs, labels)):
        node(ax, xx, 31, 26, 15, lb,
             C_BLUE if i < 2 else C_ORANGE,
             "#eef6fc" if i < 2 else "#fdf3e3",
             C_BLUE if i < 2 else C_ORANGE)
        if i < 2:
            arrow(ax, (xx + 26, 38.5), (xx + 32, 38.5), C_BLUE, LW_THICK)
    arrow(ax, (123, 46), (123, 55), C_ORANGE)
    node(ax, 110, 56, 26, 16, r"$\beta$", C_GRAY, "white", C_GRAY,
         fs=FS_FOCUS, lw=LW_MID)
    for s in ax.patches[-1:]:
        s.set_linestyle((0, (3, 2)))
    ax.text(139, 64, "消失", fontsize=FS_BODY, color=C_GREEN,
            ha="left", va="center", fontweight="bold")

    return save(fig, out("F6"), "F6")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
