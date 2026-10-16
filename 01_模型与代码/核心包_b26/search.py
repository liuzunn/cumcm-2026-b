# -*- coding: utf-8 -*-
"""搜索模块：保证性覆盖点与覆盖缺口。"""
import math
import numpy as np

def ring_cover(n, radius):
    return [(radius*math.cos(2*math.pi*k/n), radius*math.sin(2*math.pi*k/n)) for k in range(n)]

# 7 点临界方案（裕量 0 m）与 9 点带裕量方案
COVER_7 = ring_cover(7, 1000.0)
COVER_9 = [(0.0, 0.0)] + ring_cover(8, 1200.0)

def max_uncovered(cover, R=1800.0, step=20.0):
    """数值检验：目标圆域内任一点到最近探测点的最大距离（覆盖证书）"""
    worst = 0.0
    n = int(R/step) + 1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            x, y = i*step, j*step
            if x*x + y*y > R*R: continue
            d = min(math.dist((x, y), q) for q in cover)
            if d > worst: worst = d
    return worst

def coverage_certificate(cover, r_min=1000.0, R=1800.0, step=20.0):
    m = max_uncovered(cover, R, step)
    return m <= r_min, m, r_min - m
