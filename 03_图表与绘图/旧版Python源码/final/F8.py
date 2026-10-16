# -*- coding: utf-8 -*-
"""图 8  方法架构：四柱一梁   165 x 100 mm
柱内不写任何数字；每根柱子配一个极简几何图示（无文字）
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MPoly
from _common import *


def rbox2(ax, x, y, w, h, ec, fc, lw=LW_THICK, z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.03,rounding_size=0.6",
                 facecolor=fc, edgecolor=ec, lw=lw, zorder=z))


def draw(src_dir):
    fig = canvas(100)
    ax = A(fig, 3, 3, 159, 94)
    ax.set_xlim(0, 159); ax.set_ylim(0, 94); ax.invert_yaxis(); ax.axis("off")

    rbox2(ax, 6, 3, 147, 20, C_ORANGE, "#fdf3e3")
    ax.text(79.5, 10.5, r"$\beta$-independent guarantee", ha="center", va="center",
            fontsize=FS_SUB + 1.5, color=C_ORANGE, fontweight="bold")
    ax.text(79.5, 17.6, "任意朝向成立", ha="center", va="center",
            fontsize=FS_BODY, color=C_ORANGE)

    cols = [("几何", C_BLUE), ("数学", C_ORANGE), ("算法", C_BLUE), ("证据", C_GREEN)]
    X0, W, GAP = 6.0, 33.0, 5.0
    for i, (nm, c) in enumerate(cols):
        x = X0 + i * (W + GAP)
        rbox2(ax, x, 30, W, 44, c, "white")
        ax.text(x + W / 2, 38, nm, ha="center", va="center",
                fontsize=FS_SUB + 1.0, color=c, fontweight="bold")

    # 柱 1 几何：两半平面之交
    i1 = inset(fig, 3 + X0 + 3, 3 + 47, W - 6, 20)
    for sgn in (-1, 1):
        i1.plot([-1, 1], [-0.55 * sgn, 0.55 * sgn], color=C_BLUE, lw=LW_THICK)
    i1.add_patch(MPoly([(-0.5, 0), (0.5, 0.275), (0.5, -0.275)], closed=True,
                       facecolor=C_ORANGE, alpha=0.7, edgecolor=C_ORANGE, lw=LW_MID))
    i1.set_xlim(-1.15, 1.15); i1.set_ylim(-1.15, 1.15)

    # 柱 2 数学：圆盘之并
    i2 = inset(fig, 3 + X0 + (W + GAP) + 3, 3 + 47, W - 6, 20)
    for ang in range(0, 360, 72):
        r = math.radians(ang)
        i2.add_patch(Circle((0.42 * math.cos(r), 0.42 * math.sin(r)), 0.62,
                            facecolor="none", edgecolor=C_ORANGE, lw=LW_MID))
    i2.add_patch(Circle((0, 0), 0.62, facecolor=C_ORANGE, alpha=0.18, edgecolor="none"))
    i2.set_xlim(-1.15, 1.15); i2.set_ylim(-1.15, 1.15)

    # 柱 3 算法：调度轨迹
    i3 = inset(fig, 3 + X0 + 2 * (W + GAP) + 3, 3 + 45, W - 6, 22)
    rng = random.Random(7)
    pts = [(0.0, 0.0)]
    while len(pts) < 9:
        x, y = rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9)
        if x * x + y * y <= 0.85: pts.append((x, y))
    i3.add_patch(Circle((0, 0), 1.0, facecolor="none", edgecolor=C_GRAY, lw=LW_THIN))
    for p in pts[1:5]:
        i3.plot(*p, marker="o", ms=2.0, color=C_BLUE)
    for p in pts[5:]:
        i3.plot(*p, marker="*", ms=3.0, color=C_ORANGE)
    order = sorted(pts[1:], key=lambda q: math.hypot(q[0], q[1]))
    for k in range(len(order) - 1):
        i3.plot([order[k][0], order[k + 1][0]], [order[k][1], order[k + 1][1]],
                color=C_GREEN, lw=LW_THIN, alpha=0.9)
    i3.set_xlim(-1.15, 1.15); i3.set_ylim(-1.15, 1.15)
    cx3 = X0 + 2 * (W + GAP) + W / 2
    ax.text(cx3 - 5.2, 68.5, "26983", ha="center", va="center", fontsize=FS_TINY,
            color=C_GREEN, fontweight="bold")
    ax.text(cx3 + 5.2, 68.5, "13903", ha="center", va="center", fontsize=FS_TINY,
            color=C_GREEN, fontweight="bold")
    ax.plot([cx3 - 2.6, cx3 + 2.6], [68.5, 68.5], color=C_GREEN, lw=LW_THIN)

    # 柱 4 证据：四层小塔
    i4 = inset(fig, 3 + X0 + 3 * (W + GAP) + 5, 3 + 46, W - 10, 21)
    for k, wid in enumerate((1.0, 0.78, 0.56, 0.34)):
        i4.add_patch(FancyBboxPatch((-wid / 2, -0.85 + k * 0.46), wid, 0.36,
                     boxstyle="round,pad=0.02,rounding_size=0.05",
                     facecolor="none", edgecolor=[C_GRAY, C_BLUE, C_ORANGE, C_GREEN][k],
                     lw=LW_MID))
    i4.set_xlim(-1, 1); i4.set_ylim(-1, 1)

    rbox2(ax, 6, 78, 147, 13, C_GRAY, "#f7f7f7", lw=LW_MID)
    ax.text(79.5, 84.5, "确保全部清除", ha="center", va="center",
            fontsize=FS_BODY, color="#555555")
    return save(fig, out("F8"), "F8")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
