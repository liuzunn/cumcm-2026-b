# -*- coding: utf-8 -*-
"""图 5  9 点保证性覆盖证书   165 x 92 mm
图内非数字文字：m / 点  （<= 4 字）
判空定理完全移出本图（由正文定理与三行反证承担）
"""
import os, sys, math
import numpy as np
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Circle, Rectangle
from _common import *
from b26 import search

R, RMIN = 1800.0, 1000.0
COVER9 = search.COVER_9


def certified(cover, step=10.0):
    n = int(R / step) + 1
    g = np.arange(-n, n + 1) * step
    X, Y = np.meshgrid(g, g)
    keep = (X * X + Y * Y) <= R * R
    d = np.full(X.shape, 1e18)
    for (cx, cy) in cover:
        d = np.minimum(d, np.hypot(X - cx, Y - cy))
    d = np.where(keep, d, -1.0)
    i = int(np.argmax(d))
    return (float(X.ravel()[i]), float(Y.ravel()[i])), float(d.ravel()[i])


def draw(src_dir):
    fig = canvas(92)
    wp, dw = certified(COVER9)
    near = min(COVER9, key=lambda c: math.dist(c, wp))

    ax = A(fig, 3, 3, 159, 59)
    g = np.arange(-2150, 2151, 5.0)
    X, Y = np.meshgrid(g, g)
    d = np.full(X.shape, 1e18)
    for (cx, cy) in COVER9:
        d = np.minimum(d, np.hypot(X - cx, Y - cy))
    ins = (d <= RMIN).astype(float)
    ax.contourf(X, Y, ins, levels=[0.5, 1.5], colors=[C_BLUE], alpha=0.24, zorder=2)
    ax.contour(X, Y, ins, levels=[0.5], colors=[C_BLUE], linewidths=LW_THICK, zorder=3)
    for (cx, cy) in COVER9:
        ax.add_patch(Circle((cx, cy), RMIN, facecolor="none", edgecolor=C_BLUE,
                            lw=LW_THIN, ls=(0, (2, 3)), alpha=0.85, zorder=4))
        ax.plot(cx, cy, marker="o", ms=4.0, color=C_BLUE, zorder=8)
    ax.add_patch(Circle((0, 0), R, facecolor="none", edgecolor="#555555",
                        lw=LW_THICK, zorder=6))
    ax.plot(*wp, marker="o", ms=7, color=C_RED, zorder=10)
    ax.plot([near[0], wp[0]], [near[1], wp[1]], ls=(0, (3, 2)),
            color=C_RED, lw=LW_THICK, zorder=9)
    ax.annotate("%.1f m" % dw, wp, textcoords="offset points", xytext=(18, 30),
                fontsize=FS_NUM + 1.0, color=C_RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=LW_MID))
    ax.set_xlim(-2150, 2150); ax.set_ylim(-2150, 2150)
    ax.set_aspect("equal", adjustable="box")

    ax = A(fig, 3, 66, 159, 16)
    cells = [("826.8", "m 最远", C_GRAY, "white"), ("1000", "m 下界", C_GRAY, "white"),
             ("173.2", "m 裕量", C_GREEN, "#eaf7ee"), ("9", "个", C_GRAY, "white")]
    for i, (v, u, c, fc) in enumerate(cells):
        x0 = 0.008 + i * 0.248
        ax.add_patch(Rectangle((x0, 0.10), 0.238, 0.80, transform=ax.transAxes,
                               facecolor=fc, edgecolor=c,
                               lw=(LW_THICK if c == C_GREEN else LW_MID), zorder=3))
        ax.text(x0 + 0.119, 0.50, v, transform=ax.transAxes,
                fontsize=(FS_NUM + 4.0 if c == C_GREEN else FS_NUM + 2.0),
                color=(c if c != C_GRAY else C_DARK), ha="center", va="center",
                fontweight="bold", zorder=5)
        ax.text(x0 + 0.119, 0.16, u, transform=ax.transAxes, fontsize=FS_TINY,
                color=C_GRAY, ha="center", va="center", zorder=5)
    print("F5 worst %.2f m @ (%.0f, %.0f)" % (dw, wp[0], wp[1]))
    return save(fig, out("F5"), "F5")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
