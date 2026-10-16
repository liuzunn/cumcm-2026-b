# -*- coding: utf-8 -*-
"""图 7  最大角间隙判据与越界证书   165 x 95 mm
三个表盘 = 同一个 P 下三种证书（严格控制变量）
图内非数字文字：m / 点  （<= 4 字）
"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Arc, Circle, Rectangle, Wedge
from _common import *
from b26 import search
from b26_q4_certificate import ring, bearings, max_gap_deg

RINGS = [(0.0,1,0.0),(950.0,10,0.0),(1250.0,10,18.0),
         (1650.0,10,0.0),(2250.0,10,18.0),(2700.0,10,0.0)]
CERT  = [p for (a,n,ph) in RINGS for p in ring(n,a,ph)]
INNER = [p for (a,n,ph) in RINGS if a <= 1800.0 for p in ring(n,a,ph)]
COVER9 = search.COVER_9
P = (1750.0, 0.0)


def dial(fig, cx_mm, cy_mm, rad_mm, S, ok):
    """画一个方位表盘；返回 max_gap（度）。"""
    x0, y0 = cx_mm - rad_mm, cy_mm - rad_mm
    ax = A(fig, x0, y0, 2 * rad_mm, 2 * rad_mm)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.set_aspect("equal", adjustable="box")
    dirs, _ = bearings(P, S)
    mg = max_gap_deg(dirs)
    col = C_GREEN if ok else C_RED
    ax.add_patch(Circle((0, 0), 1.0, facecolor="none", edgecolor=col,
                        lw=LW_THICK, ls=("-" if ok else (0, (4, 3))), zorder=6))
    # 180 度参考直径
    ax.plot([-1.06, 1.06], [0, 0], ls=(0, (2, 2)), color=C_GRAY,
            lw=LW_THIN, zorder=4)
    ds = sorted(dirs)
    if len(ds) >= 2:
        best, at = -1.0, None
        for i in range(len(ds)):
            a = ds[i]; b = ds[(i + 1) % len(ds)]
            g = (b - a) % 360.0
            if i == len(ds) - 1:
                g = ds[0] + 360.0 - ds[-1]
            if g > best:
                best, at = g, a
        ax.add_patch(Wedge((0, 0), 1.0, at, at + best,
                           facecolor=col, alpha=0.16, edgecolor="none", zorder=2))
        for t in (at, at + best):
            r = math.radians(t)
            ax.plot([0, 1.0 * math.cos(r)], [0, 1.0 * math.sin(r)],
                    color=col, lw=LW_MID, zorder=5)
        ax.add_patch(Arc((0, 0), 2.0, 2.0, theta1=at, theta2=at + best,
                         color=col, lw=3.0, zorder=7))
        tr = math.radians(at + best / 2.0)
        rr = 0.58
        ax.text(rr * math.cos(tr), rr * math.sin(tr), "%.1f" % best,
                fontsize=FS_NUM, color=col, fontweight="bold",
                ha="center", va="center", zorder=9,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85))
    else:
        ax.add_patch(Circle((0, 0), 1.0, facecolor=col, alpha=0.16,
                            edgecolor="none", zorder=2))
        ax.add_patch(Arc((0, 0), 2.0, 2.0, theta1=0, theta2=359.6,
                         color=col, lw=3.0, zorder=7))
        ax.text(0, -1.32, "360.0", fontsize=FS_NUM, color=col,
                fontweight="bold", ha="center", va="center", zorder=9)
    for a in ds:
        r = math.radians(a)
        ax.plot([math.cos(r)], [math.sin(r)], marker="o", ms=4.0,
                color=C_BLUE, zorder=10)
    return mg


def draw(src_dir):
    fig = canvas(95)
    CY, RAD = 33.0, 21.0
    CX = [30.0, 82.0, 134.0]
    m1 = dial(fig, CX[0], CY, RAD, COVER9, False)
    m2 = dial(fig, CX[1], CY, RAD, INNER, False)
    m3 = dial(fig, CX[2], CY, RAD, CERT, True)
    ax = A(fig, 3, 3, 159, 6)
    for cx, n in zip(CX, [len(COVER9), len(INNER), len(CERT)]):
        ax.text(cx / 165.0, 0.5, "%d" % n, transform=ax.transAxes,
                fontsize=FS_NUM, color=C_BLUE, ha="right", va="center",
                fontweight="bold")
        ax.text(cx / 165.0 + 0.008, 0.5, "点", transform=ax.transAxes,
                fontsize=FS_TINY, color=C_GRAY, ha="left", va="center")

    ax = A(fig, 3, 64, 159, 16)
    cells = [("51", "点", C_GRAY, "white"), ("24.50", "度 基础裕量", C_GRAY, "white"),
             ("3.687", "度 认证裕量", C_GREEN, "#eaf7ee"), ("0", "未认证", C_GREEN, "#eaf7ee")]
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

    ax = A(fig, 3, 83, 159, 10)
    ax.plot([0.02], [0.62], marker="o", ms=4.0, color=C_BLUE,
            transform=ax.transAxes, zorder=5)
    ax.text(0.045, 0.62, "可见方位", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_BLUE, ha="left", va="center")
    ax.plot([0.24, 0.275], [0.62, 0.62], color=C_RED, lw=3.0, transform=ax.transAxes)
    ax.text(0.29, 0.62, "最大空档", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_RED, ha="left", va="center")
    ax.plot([0.52, 0.575], [0.62, 0.62], ls=(0, (2, 2)), color=C_GRAY,
            lw=LW_THIN, transform=ax.transAxes)
    ax.text(0.59, 0.62, r"$180^\circ$", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_GRAY, ha="left", va="center")
    print("F7 gaps:", round(m1, 2), round(m2, 2), round(m3, 2),
          "| lens:", len(COVER9), len(INNER), len(CERT))
    return save(fig, out("F7"), "F7")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
