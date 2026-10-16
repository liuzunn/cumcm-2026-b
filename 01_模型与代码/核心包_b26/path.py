# -*- coding: utf-8 -*-
"""路径模块：最近必做集合调度（把"扫描"和"清除"合并计费）。"""
import math

def nearest(pos, actions):
    """actions: [(kind, target_point, channel 或 None)]，返回距离最近的一个"""
    if not actions: return None
    return min(actions, key=lambda a: math.dist(pos, a[1]))

def order_nearest(pos, points):
    left = list(points); out = []
    cur = pos
    while left:
        b = min(left, key=lambda q: math.dist(cur, q))
        out.append(b); left.remove(b); cur = b
    return out
