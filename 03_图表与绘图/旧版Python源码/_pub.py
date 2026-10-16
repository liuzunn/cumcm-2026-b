# -*- coding: utf-8 -*-
"""
全篇统一视觉系统（本轮重构版）。
约束：图内零中文、无圆角卡片、无印章条、无多余箭头。
所有 FigXX.py 必须 import 本模块；不得自行定义颜色/线宽/字号。
坐标约定：布局坐标 (x, y) 以 mm 为单位、以画布左上角为原点、y 向下。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,          # editable TrueType in PDF
    "svg.fonttype": "none",       # editable text in SVG
    "figure.dpi": 300,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.0,
    "axes.spines.right": False,
    "axes.spines.top": False,
})

MM = 1.0 / 25.4
W_STD = 165.0

# ---- 颜色（ restrained palette ）----
C_BLUE   = "#2e6da4"   # 中性 / 几何
C_ORANGE = "#b35c00"   # 信号 / 焦点区域
C_RED    = "#c0392b"   # 证伪 / 反例 / 边界（必配虚线）
C_GREEN  = "#1e8449"   # 通过 / 采用 / 保证（必配加粗实线）
C_GRAY   = "#707070"
C_GRAY_L = "#c8c8c8"
C_DARK   = "#1a2a3a"

# ---- 线宽三档 ----
LW_THIN  = 0.5
LW_MID   = 0.8
LW_THICK = 1.6

# ---- 字号 ----
FS_TICK  = 6.0
FS_LABEL = 7.0
FS_MATH  = 7.0
FS_NUM   = 9.0    # 关键数字加粗
FS_FOCUS = 11.0
FS_TINY  = 5.5


def canvas(h_mm, w_mm=W_STD):
    """创建画布，默认 165 mm 宽。"""
    return plt.figure(figsize=(w_mm * MM, h_mm * MM))


def ax(fig, x, y, w, h):
    """无边框坐标轴。(x,y) 左上角（mm，y 向下）。"""
    fw, fh = fig.get_size_inches()
    FW, FH = fw / MM, fh / MM
    a = fig.add_axes([x / FW, (FH - y - h) / FH, w / FW, h / FH])
    a.set_xticks([])
    a.set_yticks([])
    for s in a.spines.values():
        s.set_visible(False)
    a.patch.set_visible(False)
    return a


def ax_frame(fig, x, y, w, h, ec=C_GRAY_L, lw=LW_MID):
    """带细边框的坐标轴（仅用于需要边界的几何面板，不用圆角）。"""
    a = ax(fig, x, y, w, h)
    for s in a.spines.values():
        s.set_visible(True)
        s.set_color(ec)
        s.set_linewidth(lw)
    return a


def eq(a, xlim, ylim, asp=1.0):
    """设置等比例坐标范围。"""
    a.set_xlim(*xlim)
    a.set_ylim(*ylim)
    a.set_aspect(asp if asp == "auto" else asp, adjustable="box")


def save(fig, outdir, name, png_dpi=300):
    """输出 PDF + PNG。SVG 仅在字体可编辑时保留。"""
    os.makedirs(outdir, exist_ok=True)
    pdf_path = os.path.join(outdir, "%s.pdf" % name)
    png_path = os.path.join(outdir, "%s.png" % name)
    fig.savefig(pdf_path, format="pdf", facecolor="white")
    fig.savefig(png_path, format="png", dpi=png_dpi, facecolor="white")
    plt.close(fig)
    return pdf_path, png_path


def panel_label(a, text, loc="upper left", fs=FS_LABEL):
    """面板标号（a/b/c/d），用纯文字不用圆角框。"""
    if loc == "upper left":
        a.text(0.04, 0.96, text, transform=a.transAxes, fontsize=fs,
               fontweight="bold", color=C_DARK, ha="left", va="top")
    elif loc == "upper right":
        a.text(0.96, 0.96, text, transform=a.transAxes, fontsize=fs,
               fontweight="bold", color=C_DARK, ha="right", va="top")
