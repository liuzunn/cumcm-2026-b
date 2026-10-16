# -*- coding: utf-8 -*-
"""全篇统一视觉系统（Step 8）。
所有 FigXX.py 必须 import 本模块；不得自行定义颜色 / 线宽 / 字号。
坐标约定：布局坐标 (x, y) 以 mm 为单位、以画布【左上角】为原点、y 向下。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
    "svg.fonttype": "path",
    "pdf.fonttype": 42,
    "figure.dpi": 300,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.0,
})

MM = 1.0 / 25.4
W_STD = 165.0

C_BLUE   = "#2e6da4"
C_ORANGE = "#b35c00"
C_RED    = "#c0392b"
C_GREEN  = "#1e8449"
C_GRAY   = "#8a8a8a"
C_GRAY_L = "#cfcfcf"
C_BG     = "#f2f2f2"
C_DARK   = "#1a3d5c"

LW_THIN, LW_MID, LW_THICK = 0.5, 0.8, 1.6
FS_BODY, FS_SUB, FS_MATH, FS_FOCUS = 6.5, 7.5, 7.0, 13.0
FS_NUM = 9.0
FS_TINY = 6.0


def canvas(h_mm, w_mm=W_STD):
    return plt.figure(figsize=(w_mm * MM, h_mm * MM))


def A(fig, x, y, w, h):
    """无边框坐标轴。(x, y) 为左上角（mm，y 向下）。"""
    fw, fh = fig.get_size_inches()
    FW, FH = fw / MM, fh / MM
    ax = fig.add_axes([x / FW, (FH - y - h) / FH, w / FW, h / FH])
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.patch.set_visible(False)
    return ax


def inset(fig, x, y, w, h, frame=None, lw=LW_THICK):
    ax = A(fig, x, y, w, h)
    if frame:
        for s in ax.spines.values():
            s.set_visible(True); s.set_color(frame); s.set_linewidth(lw)
    ax.set_aspect("equal", adjustable="box")
    return ax


def box(ax, ec=C_GRAY_L, lw=LW_MID, fc="none", ls="-"):
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(ec); s.set_linewidth(lw); s.set_linestyle(ls)
    ax.patch.set_visible(True); ax.patch.set_facecolor(fc)


def rbox(ax, x, y, w, h, ec=C_GRAY_L, lw=LW_MID, fc="none", pad=0.012):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=%g,rounding_size=%g" % (pad, pad * 1.6),
                 fc=fc, ec=ec, lw=lw, zorder=3))


def note(ax, txt, xy, fs=FS_BODY, fc="#eef6fc", ec=C_BLUE, tc=C_DARK,
         ha="left", va="bottom", z=20):
    ax.text(xy[0], xy[1], txt, transform=ax.transAxes, fontsize=fs, color=tc,
            ha=ha, va=va, linespacing=1.5, zorder=z,
            bbox=dict(boxstyle="round,pad=0.45", fc=fc, ec=ec, lw=0.7))


def eq(ax, xlim, ylim, asp=1.0):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect(asp if asp == "auto" else asp, adjustable="box")


def save(fig, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(os.path.join(outdir, "%s.%s" % (name, ext)),
                    format=ext, facecolor="white")
    plt.close(fig)
    return os.path.join(outdir, name + ".png")
