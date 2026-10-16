# -*- coding: utf-8 -*-
"""Fig.9  判空定理（Q3）  画布 165 x 116 mm
版式：定理陈述带 + 四段纵向数学证书 + 右侧几何构型 + 量词消去条
视觉焦点：③ 段中的量词配对结构（forall p  与  exists s）
"""
import os, sys, math
import numpy as np
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Circle
from _viz import *
from b26 import search

R, RMIN = 1800.0, 1000.0
COVER9 = search.COVER_9
WP = (1660.0, -690.0)          # 与 Fig.8 同一枚最坏点（10 m 网格口径 826.8 m）
NEAR = (849.0, -849.0)


def seg(ax, y, title, body, col, fc, tcol):
    ax.add_patch(plt.Rectangle((0.004, 0.06), 0.992, 0.88, transform=ax.transAxes,
                               facecolor=fc, edgecolor=col, lw=LW_THICK, zorder=3))
    ax.text(0.035, 0.50, title, transform=ax.transAxes, fontsize=FS_SUB,
            color=tcol, ha="left", va="center", fontweight="bold", zorder=5)
    ax.text(0.30, 0.50, body, transform=ax.transAxes, fontsize=FS_BODY,
            color=C_DARK, ha="left", va="center", zorder=5)


def draw(src_dir):
    fig = canvas(116)

    # ---------- 定理陈述带 ----------
    ax = A(fig, 3, 3, 159, 16)
    box(ax, ec=C_GRAY, lw=LW_MID, fc="#fafafa")
    ax.text(0.5, 0.72, "判空定理", transform=ax.transAxes, fontsize=FS_SUB + 0.5,
            color=C_DARK, ha="center", va="center", fontweight="bold")
    ax.text(0.5, 0.28,
            "若巡逻点集满足覆盖条件，则任一未清除的源必被某巡逻点检出；"
            "从而「从未返回 direction / near」意味着「该频道为空」。",
            transform=ax.transAxes, fontsize=FS_BODY, color=C_DARK,
            ha="center", va="center")

    # ---------- 四段 ----------
    ys = [22, 41, 60, 79]
    seg(A(fig, 3, ys[0], 100, 16), 0, "① Claim",
        "假设该频道存在未清除干扰源，位于 $\\mathbf{p}\\in\\mathcal{D}$",
        C_GRAY, "white", C_GRAY)
    seg(A(fig, 3, ys[1], 100, 16), 0, "② Condition",
        "覆盖条件：$\\forall \\mathbf{p}\\in\\mathcal{D}\\ \\exists \\mathbf{s}\\in\\mathcal{P}$，"
        "$\\|\\mathbf{p}-\\mathbf{s}\\|\\leq r_{\\min}$",
        C_BLUE, "#eef6fc", C_BLUE)
    seg(A(fig, 3, ys[2], 100, 16), 0, "③ Certificate",
        "量词配对结构",
        C_ORANGE, "#fdf3e3", C_ORANGE)
    seg(A(fig, 3, ys[3], 100, 16), 0, "④ Conclusion",
        "该点必返回 direction 或 near，与「全部为 no_signal」矛盾",
        C_GREEN, "#eaf7ee", C_GREEN)

    # ③ 段的量词突出 + 橙色配对弧
    ax = A(fig, 3, ys[2], 100, 16)
    ax.text(0.72, 0.50, r"$\forall \mathbf{p}$", transform=ax.transAxes,
            fontsize=11.0, color=C_ORANGE, ha="center", va="center",
            fontweight="bold", zorder=6)
    ax.text(0.90, 0.50, r"$\exists \mathbf{s}$", transform=ax.transAxes,
            fontsize=11.0, color=C_ORANGE, ha="center", va="center",
            fontweight="bold", zorder=6)
    ArcMid(0.72, 0.52, 0.90, 0.52, 0.28, ax, C_ORANGE)
    # ④ 段的红色矛盾删除线
    ax = A(fig, 3, ys[3], 100, 16)
    ax.plot([0.62, 0.96], [0.50, 0.50], transform=ax.transAxes,
            color=C_RED, lw=LW_THICK, zorder=6)
    ax.text(0.79, 0.72, "矛盾", transform=ax.transAxes, fontsize=FS_TINY,
            color=C_RED, ha="center", va="center", fontweight="bold", zorder=7)

    # ---------- 右侧几何构型 ----------
    ax = A(fig, 106, 22, 56, 73)
    g = np.arange(-2150, 2151, 6.0)
    X, Y = np.meshgrid(g, g)
    d = np.full(X.shape, 1e18)
    for (cx, cy) in COVER9:
        d = np.minimum(d, np.hypot(X - cx, Y - cy))
    ins = (d <= RMIN).astype(float)
    ax.contourf(X, Y, ins, levels=[0.5, 1.5], colors=[C_BLUE], alpha=0.20, zorder=2)
    ax.contour(X, Y, ins, levels=[0.5], colors=[C_BLUE], linewidths=LW_MID, zorder=3)
    for (cx, cy) in COVER9:
        ax.plot(cx, cy, marker="o", ms=3.6, color=C_BLUE, zorder=8)
    ax.add_patch(Circle((0, 0), R, facecolor="none", edgecolor="#555555",
                        lw=LW_MID, zorder=6))
    ax.plot(*WP, marker="*", ms=13, color=C_RED, zorder=10)
    ax.plot([NEAR[0], WP[0]], [NEAR[1], WP[1]], ls=(0, (3, 2)),
            color=C_RED, lw=LW_MID, zorder=9)
    ax.annotate("假想源 $\\mathbf{p}$", WP, textcoords="offset points",
                xytext=(-8, 30), fontsize=FS_TINY, color=C_RED, ha="right",
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=LW_THIN))
    ax.text(0.5, 0.03, "$\\leq r_{\\min}=1000$ m", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_RED, ha="center", va="bottom")
    ax.set_xlim(-2150, 2150); ax.set_ylim(-2150, 2150)
    ax.set_aspect("equal", adjustable="box")

    # ---------- 量词消去条 ----------
    ax = A(fig, 3, 98, 159, 15)
    box(ax, ec=C_GRAY_L, lw=LW_MID)
    ax.text(0.13, 0.62, "源的位置未知", transform=ax.transAxes, fontsize=FS_BODY,
            color=C_DARK, ha="center", va="center")
    ax.text(0.13, 0.24, "？", transform=ax.transAxes, fontsize=13.0,
            color="#111111", ha="center", va="center", fontweight="bold")
    ax.annotate("", xy=(0.30, 0.50), xytext=(0.22, 0.50), transform=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=LW_MID))
    ax.text(0.42, 0.62, r"$\forall \mathbf{p}\in\mathcal{D}$", transform=ax.transAxes,
            fontsize=FS_MATH + 1.5, color=C_BLUE, ha="center", va="center")
    ax.text(0.42, 0.24, "遍历场地的每一个位置", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="center", va="center")
    ax.annotate("", xy=(0.59, 0.50), xytext=(0.51, 0.50), transform=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=LW_MID))
    ax.text(0.71, 0.62, "每个位置都在某个探测点的 1000 m 内", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_DARK, ha="center", va="center")
    ax.text(0.71, 0.24, "（左图已证）", transform=ax.transAxes,
            fontsize=FS_TINY, color=C_GRAY, ha="center", va="center")
    ax.annotate("", xy=(0.855, 0.50), xytext=(0.775, 0.50), transform=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=LW_THICK))
    ax.text(0.93, 0.62, "源的位置从推理中消失", transform=ax.transAxes,
            fontsize=FS_BODY, color=C_GREEN, ha="center", va="center", fontweight="bold")
    ax.text(0.93, 0.24, "？", transform=ax.transAxes, fontsize=13.0,
            color=C_GRAY, ha="center", va="center", fontweight="bold",
            bbox=dict(boxstyle="circle,pad=0.10", fc="white", ec=C_GRAY, lw=1.0))

    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig09")
    return save(fig, out, "Fig09")


class ArcMid:
    """在 axes 坐标两点之间画一条上凸的橙色弧线（量词配对）。"""
    def __new__(cls, x1, y1, x2, y2, h, ax, col):
        from matplotlib.patches import Arc
        import numpy as _np
        t = _np.linspace(0, 1, 60)
        xs = x1 + (x2 - x1) * t
        ys = y1 + h * _np.sin(_np.pi * t)
        ln, = ax.plot(xs, ys, transform=ax.transAxes, color=col,
                      lw=LW_THICK, zorder=7, solid_capstyle="round")
        return ln


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
