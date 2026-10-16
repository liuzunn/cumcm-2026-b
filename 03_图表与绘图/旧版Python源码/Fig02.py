# -*- coding: utf-8 -*-
"""Fig.2  从测向读数到楔形可行域（画布 165 x 92 mm）"""
import os, sys, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import Polygon as MPoly, Arc
from _viz import *
from b26 import locate

TH = 0.0; DD = 1.0
F = r"$W(\mathbf{s},\theta)=\{\mathbf{p}:|\varphi(\mathbf{p}-\mathbf{s})-\theta|\leq 1^\circ\}=H_1\cap H_2$"


def draw(src_dir):
    fig = canvas(92)
    ax = A(fig, 3, 3, 55, 52)
    eq(ax, (-1.2, 1.2), (-1.2, 1.2))
    ax.add_patch(Arc((0, 0), 2.0, 2.0, theta1=0, theta2=360,
                     color=C_GRAY, lw=LW_MID, ls=(0, (4, 3))))
    G = (0.66, 0.50); S = (-0.62, -0.62)
    ax.plot([S[0], G[0]], [S[1], G[1]], color=C_BLUE, lw=LW_MID, zorder=4)
    ax.plot(*G, marker="*", ms=14, color=C_ORANGE, zorder=6)
    ax.plot(*S, marker="o", ms=5.5, color=C_BLUE, zorder=6)
    ax.text(G[0] + 0.08, G[1] + 0.04, "源", fontsize=FS_BODY, color=C_ORANGE)
    ax.text(S[0] - 0.04, S[1] - 0.19, "探测点", fontsize=FS_BODY, color=C_BLUE, ha="center")
    ax.text(0.0, 1.12, "现实空间", fontsize=FS_SUB, color=C_DARK,
            ha="center", va="top", fontweight="bold")

    ax = A(fig, 62, 3, 46, 52)
    eq(ax, (-0.06, 1.14), (-0.20, 0.20))
    w = locate.wedge_poly((0, 0), TH, R=1.0, delta=DD)
    ax.add_patch(MPoly(w, closed=True, facecolor=C_BLUE, alpha=0.60,
                       edgecolor=C_BLUE, lw=LW_MID, zorder=3))
    ax.plot([0, 1.06], [0, 0], ls=(0, (4, 3)), color="#666666", lw=LW_THIN, zorder=5)
    ax.plot(0, 0, marker="o", ms=5.5, color=C_BLUE, zorder=6)
    ax.plot([1.0, 1.07], [0.0175, 0.0175], color=C_RED, lw=LW_MID, zorder=7)
    ax.plot([1.0, 1.07], [-0.0175, -0.0175], color=C_RED, lw=LW_MID, zorder=7)
    ax.text(0.28, 0.055, "2°", fontsize=FS_MATH, color=C_RED, fontweight="bold")
    ax.text(0.44, 0.178, "一个读数 = 一把扇子（真实比例）", fontsize=FS_BODY,
            color=C_DARK, ha="center", va="top", fontweight="bold")
    ax.text(0.03, -0.178, "它【有宽度】，不是一条线", fontsize=FS_TINY, color=C_BLUE)

    ax = A(fig, 112, 3, 50, 52)
    eq(ax, (-1.3, 1.5), (-1.2, 1.2))
    DH = 14.0
    ax.add_patch(MPoly([(-1.3, 0.0), (1.5, 1.5 * math.tan(math.radians(DH))),
                        (1.5, 1.3), (-1.3, 1.3)], closed=True,
                       facecolor=C_BLUE, alpha=0.13, edgecolor="none", zorder=2))
    ax.add_patch(MPoly([(-1.3, 0.0), (1.5, -1.5 * math.tan(math.radians(DH))),
                        (1.5, -1.3), (-1.3, -1.3)], closed=True,
                       facecolor=C_BLUE, alpha=0.13, edgecolor="none", zorder=2))
    for sgn, lab, lp in ((-1, "$H_1$", (-1.26, 0.36)), (1, "$H_2$", (1.24, -0.32))):
        th = math.radians(sgn * DH)
        ax.plot([-1.3, 1.5], [-1.3 * math.tan(th), 1.5 * math.tan(th)],
                color=C_BLUE, lw=LW_THICK, zorder=4)
        ax.text(lp[0], lp[1], lab, fontsize=FS_MATH, color=C_BLUE, fontweight="bold")
    ax.add_patch(MPoly([(-0.7, 0.0), (0.7, 0.7 * math.tan(math.radians(DH))),
                        (0.7, -0.7 * math.tan(math.radians(DH)))], closed=True,
                       facecolor=C_ORANGE, alpha=0.85, edgecolor=C_ORANGE,
                       lw=LW_THICK, zorder=6))
    ax.text(0.06, 1.12, "数学对象", fontsize=FS_SUB,
            color=C_DARK, va="top", fontweight="bold")
    ax.text(0.06, 0.99, "（角度已放大绘制）", fontsize=FS_TINY, color=C_GRAY, va="top")

    ax = A(fig, 3, 58, 159, 12)
    ax.text(0.13, 0.55, "点", fontsize=FS_BODY, color=C_GRAY, ha="center", va="center")
    ax.annotate("", xy=(0.21, 0.55), xytext=(0.16, 0.55),
                arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=LW_MID))
    ax.text(0.27, 0.55, "射线", fontsize=FS_BODY, color=C_GRAY, ha="center", va="center")
    ax.annotate("", xy=(0.35, 0.55), xytext=(0.30, 0.55),
                arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=LW_THICK))
    ax.text(0.44, 0.55, "2° 楔形", fontsize=FS_BODY, color=C_BLUE, ha="center",
            va="center", fontweight="bold")
    ax.text(0.78, 0.55, "误差不是噪声，而是区域的宽度", fontsize=FS_SUB,
            color=C_DARK, ha="center", va="center", fontweight="bold")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    ax = A(fig, 3, 74, 159, 13)
    ax.text(0.5, 0.5, F, fontsize=FS_MATH + 1.2, color=C_DARK, ha="center", va="center")
    box(ax, ec=C_GRAY_L, lw=LW_MID)

    out = os.path.join(os.path.dirname(src_dir), "figures", "Fig02")
    return save(fig, out, "Fig02")


if __name__ == "__main__":
    print(draw(os.path.dirname(os.path.abspath(__file__))))
