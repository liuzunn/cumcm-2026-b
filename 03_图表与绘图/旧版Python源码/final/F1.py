# -*- coding: utf-8 -*-
"""图 1  全文主轴：三个未知量的逐层消去   165 x 90 mm"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, FancyArrowPatch
from _common import *


def draw(src_dir):
    fig = canvas(90)
    ax = A(fig, 3, 3, 159, 84)
    ax.set_xlim(0, 159); ax.set_ylim(0, 84); ax.invert_yaxis(); ax.axis("off")

    band = [(4, 4), (32, 4), (24, 80), (12, 80)]
    ax.add_patch(MPoly(band, closed=True, facecolor="#f0f0f0", edgecolor="none", zorder=1))
    ax.text(18, 14, "信息不完备", fontsize=FS_TINY, color=C_GRAY,
            ha="center", va="center")
    ax.text(18, 70, "可保证", fontsize=FS_TINY, color=C_GREEN,
            ha="center", va="center")
    ax.text(37, 42, "逐层消去", fontsize=FS_BODY, color=C_GRAY,
            ha="center", va="center", rotation=90)

    rows = [(C_BLUE, "位置", "可行域"), (C_ORANGE, "数量", "覆盖证书"),
            (C_GREEN, "朝向", r"$\forall\beta$ 保证集")]
    for i, (c, a, b) in enumerate(rows):
        y = 14 + i * 22
        ax.add_patch(FancyBboxPatch((46, y), 26, 15,
                     boxstyle="round,pad=0.02,rounding_size=0.5",
                     facecolor="white", edgecolor=C_GRAY, lw=LW_MID, zorder=3))
        ax.text(59, y + 7.5, a, ha="center", va="center", fontsize=FS_SUB,
                color=C_DARK, fontweight="bold", zorder=5)
        ax.add_patch(FancyArrowPatch((72.5, y + 7.5), (88, y + 7.5),
                     arrowstyle="-|>", color=c, lw=LW_THICK,
                     mutation_scale=11, zorder=4))
        ax.add_patch(FancyBboxPatch((88, y), 62, 15,
                     boxstyle="round,pad=0.02,rounding_size=0.5",
                     facecolor="white", edgecolor=c, lw=LW_THICK, zorder=3))
        ax.text(119, y + 7.5, b, ha="center", va="center", fontsize=FS_SUB,
                color=c, fontweight="bold", zorder=5)
    return save(fig, out("F1"), "F1")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
