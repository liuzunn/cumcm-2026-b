# -*- coding: utf-8 -*-
"""Fig.8  9 点巡逻集对 1800 m 任务域的保证性覆盖及 173.2 m 最小安全裕量
画布 165 x 102 mm ｜ 视觉焦点：证书印章条中的 173.2 m 绿色印章
数字口径：与项目 b26.search.coverage_certificate 完全一致（网格按 step 对齐，step=10）
"""
import os, sys, math
import numpy as np
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Circle, Rectangle
from _viz import *
from b26 import search

R, RMIN, STEP = 1800.0, 1000.0, 10.0
COVER9, COVER7 = search.COVER_9, search.COVER_7


def certified(cover, step=STEP):
    """与 b26.search.max_uncovered 完全相同的网格枚举，并返回最坏点坐标。"""
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


def draw_panel(ax, cover, col, worst, wdist, nearc, lw_main=LW_THICK, lab_near=True):
    g = np.arange(-2150, 2151, 5.0)
    X, Y = np.meshgrid(g, g)
    d = np.full(X.shape, 1e18)
    for (cx, cy) in cover:
        d = np.minimum(d, np.hypot(X - cx, Y - cy))
    inside = (d <= RMIN).astype(float)
    ax.contourf(X, Y, inside, levels=[0.5, 1.5], colors=[col], alpha=0.22, zorder=2)
    ax.contour(X, Y, inside, levels=[0.5], colors=[col], linewidths=lw_main, zorder=3)
    for (cx, cy) in cover:
        ax.add_patch(Circle((cx, cy), RMIN, facecolor="none", edgecolor=col,
                            lw=LW_THIN, ls=(0, (2, 3)), alpha=0.85, zorder=4))
        ax.plot(cx, cy, marker="o", ms=4.2, color=col, zorder=8)
    ax.add_patch(Circle((0, 0), R, facecolor="none", edgecolor="#555555",
                        lw=lw_main, zorder=6))
    ax.plot(*worst, marker="o", ms=6.5, color=C_RED, zorder=10)
    ax.plot([nearc[0], worst[0]], [nearc[1], worst[1]], ls=(0, (3, 2)),
            color=C_RED, lw=LW_THICK, zorder=9)
    ax.set_xlim(-2150, 2150); ax.set_ylim(-2150, 2150)
    ax.set_aspect("equal", adjustable="box")


def draw(src_dir):
    fig = canvas(102)
    wp9, d9 = certified(COVER9)
    n9 = min(COVER9, key=lambda c: math.dist(c, wp9))
    wp7, d7 = certified(COVER7)
    n7 = min(COVER7, key=lambda c: math.dist(c, wp7))

    ax = A(fig, 3, 3, 104, 68)
    draw_panel(ax, COVER9, C_BLUE, wp9, d9, n9)
    ax.text(0.5, 0.985, "9 点保证性覆盖（圆心 + 半径 1200 m 圆周 8 点）",
            transform=ax.transAxes, fontsize=FS_SUB, color=C_DARK,
            ha="center", va="top", fontweight="bold")
    ax.annotate("最远点：距最近巡逻点 %.1f m（< 1000 m）" % d9, wp9,
                textcoords="offset points", xytext=(-6, 46), fontsize=FS_BODY,
                color=C_RED, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=LW_MID))
    ax.text(0.5, 0.045, "深蓝区域 = 9 个 1000 m 接收邻域之并，完整包住整个任务域",
            transform=ax.transAxes, fontsize=FS_TINY, color=C_BLUE, ha="center",
            va="bottom", bbox=dict(boxstyle="round,pad=0.35", fc="white",
                                   ec=C_BLUE, lw=0.6))

    ax = A(fig, 111, 3, 51, 68)
    draw_panel(ax, COVER7, C_GRAY, wp7, d7, n7, lw_main=LW_MID)
    ax.text(0.5, 0.985, "对照：7 点方案", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_GRAY, ha="center", va="top", fontweight="bold")
    ax.annotate("最坏点 = 圆心，正好 %.1f m" % d7, wp7,
                textcoords="offset points", xytext=(-4, 26), fontsize=FS_TINY,
                color=C_RED, ha="right", va="bottom", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=LW_MID))
    ax.text(0.5, 0.045, "最大未覆盖 %.1f m｜裕量 0.0 m → 临界，工程不可用" % d7,
            transform=ax.transAxes, fontsize=FS_TINY, color=C_RED, ha="center",
            va="bottom", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="#fdecea", ec=C_RED, lw=0.7))

    # ================= 证书印章条（Fig.15 复用同一组件） =================
    ax = A(fig, 3, 74, 159, 15)
    cells = [("最大未覆盖（10 m 网格）", "826.8 m", C_GRAY, "white"),
             ("接收半径下界 $r_{\\min}$", "1000 m", C_GRAY, "white"),
             ("安全裕量", "173.2 m", C_GREEN, "#eaf7ee"),
             ("覆盖点数", "9", C_GRAY, "white")]
    for i, (t, v, c, fc) in enumerate(cells):
        x0 = 0.008 + i * 0.248
        ax.add_patch(Rectangle((x0, 0.08), 0.238, 0.84, transform=ax.transAxes,
                               facecolor=fc, edgecolor=c,
                               lw=(LW_THICK if c == C_GREEN else LW_MID), zorder=3))
        ax.text(x0 + 0.119, 0.72, t, transform=ax.transAxes, fontsize=FS_TINY,
                color=C_GRAY, ha="center", va="center", zorder=5)
        ax.text(x0 + 0.119, 0.36, v, transform=ax.transAxes,
                fontsize=(FS_NUM + 2.0 if c == C_GREEN else FS_NUM + 0.5),
                color=(c if c != C_GRAY else C_DARK), ha="center", va="center",
                fontweight="bold", zorder=5)

    ax = A(fig, 3, 92, 159, 8)
    ax.text(0.5, 0.5, "冻结程序默认按 20 m 网格打印 821.0 m / 179.0 m；两者均为数值下界，网格越细数值越大。论文统一采用 10 m 网格口径（5 m 网格复算相同）。",
            transform=ax.transAxes, fontsize=FS_TINY, color=C_GRAY,
            ha="center", va="center")
    box(ax, ec=C_GRAY_L, lw=LW_THIN)

    print("Fig.8  9点 最坏点 %.2f m @ (%.0f, %.0f)  最近点 (%.0f, %.0f)" % (d9, wp9[0], wp9[1], n9[0], n9[1]))
    print("Fig.8  7点 最坏点 %.2f m @ (%.0f, %.0f)  <-- 圆心" % (d7, wp7[0], wp7[1]))
    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig08")
    return save(fig, out, "Fig08")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
