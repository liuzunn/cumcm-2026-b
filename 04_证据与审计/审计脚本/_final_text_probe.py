# -*- coding: utf-8 -*-
"""精确统计：运行时拦截 matplotlib 的 Axes.text，只统计真正渲染出来的字符串。"""
import os, re, sys, importlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.axes

SRC = r"D:\BaiduNetdiskDownload\数学建模\_teach\figure_sources\final"
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, ".."))

LOG = []
_orig = matplotlib.axes.Axes.text
def patched(self, x, y, s, *a, **k):
    LOG.append(s)
    return _orig(self, x, y, s, *a, **k)
matplotlib.axes.Axes.text = patched

cjk = re.compile(r"[\u4e00-\u9fff]")
lat = re.compile(r"[A-Za-z]{2,}")
BUDGET = {"F1": 60, "F2": 30, "F3": 35, "F4": 45, "F5": 35,
          "F6": 35, "F7": 40, "F8": 35, "F9": 40}
tot = 0
for k in range(1, 10):
    key = "F%d" % k
    LOG.clear()
    m = importlib.import_module(key)
    m.draw(os.path.join(SRC, key))
    body = " ".join(str(s) for s in LOG)
    body = re.sub(r"\$[^$]*\$", " ", body)          # 公式不计
    body = re.sub(r"[-+]?\d[\d\.]*", " ", body)     # 数字不计
    n = len(cjk.findall(body)) + len(lat.findall(body))
    tot += n
    b = BUDGET[key]
    print("%-3s  文字 %3d  /  预算 %3d   %s" % (key, n, b, "OK" if n <= b else "OVER"))
print("total =", tot)
