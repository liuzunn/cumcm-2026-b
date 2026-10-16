# -*- coding: utf-8 -*-
"""最终版绘图公共层（Step 8 收敛阶段）。沿用 _viz 的视觉系统，仅增加最终版输出路径。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _viz import *          # noqa
from _viz import canvas, A, inset, box, rbox, eq, save, note

FINAL_FIG_DIR = r"D:\BaiduNetdiskDownload\数学建模\_teach\figures\final"


def out(name):
    return os.path.join(FINAL_FIG_DIR, name)
