# -*- coding: utf-8 -*-
"""图 9  从数学证明到官方演练的四层证据链   165 x 95 mm
塔形：底宽顶窄；认知路径 灰 -> 蓝 -> 橙 -> 绿（自下而上）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyBboxPatch
from _common import *


def bar(ax, x, y, w, h, ec, fc, tc, title, sub):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.5",
                 facecolor=fc, edgecolor=ec, lw=LW_THICK, zorder=3))
    ax.text(x + w / 2, y + h * 0.38, title, ha="center", va="center",
            fontsize=FS_SUB, color=tc, fontweight="bold", zorder=5)
    if sub:
        ax.text(x + w / 2, y + h * 0.74, sub, ha="center", va="center",
                fontsize=FS_TINY, color="#666666", zorder=5)


def draw(src_dir):
    fig = canvas(95)
    ax = A(fig, 3, 3, 159, 89)
    ax.set_xlim(0, 159); ax.set_ylim(0, 89); ax.invert_yaxis(); ax.axis("off")

    rows = [
        (60, 22, 39, 14, C_GREEN, "#eaf7ee", C_GREEN, "官方演练", "n = 1 / 3"),
        (52, 38, 55, 14, C_ORANGE, "#fdf3e3", C_ORANGE, "工程验证", ""),
        (44, 54, 71, 14, C_BLUE, "#eef6fc", C_BLUE, "离线仿真", "自建 mock"),
        (36, 70, 87, 14, C_DARK, "white", C_DARK, "数学证明", "11 条"),
    ]
    for r_ in rows:
        bar(ax, *r_)

    ax.add_patch(FancyBboxPatch((62, 3), 35, 14,
                 boxstyle="round,pad=0.02,rounding_size=0.5",
                 facecolor="white", edgecolor=C_RED, lw=LW_THICK,
                 linestyle=(0, (4, 3)), zorder=3))
    ax.text(79.5, 8.4, "0 / 6", ha="center", va="center", fontsize=FS_NUM + 3.0,
            color=C_RED, fontweight="bold", zorder=5)
    ax.text(79.5, 13.8, "正式测试", ha="center", va="center", fontsize=FS_TINY,
            color=C_RED, zorder=5)

    ax.text(96, 20.0, "pending", ha="left", va="center",
            fontsize=FS_TINY, color=C_RED, style="italic")
    ax.text(109, 36.0, "confirms", ha="left", va="center",
            fontsize=FS_TINY, color=C_GRAY, style="italic")
    ax.text(117, 52.0, "implements", ha="left", va="center",
            fontsize=FS_TINY, color=C_GRAY, style="italic")
    ax.text(125, 68.0, "instantiates", ha="left", va="center",
            fontsize=FS_TINY, color=C_GRAY, style="italic")
    return save(fig, out("F9"), "F9")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
