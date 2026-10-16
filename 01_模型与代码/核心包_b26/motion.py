# -*- coding: utf-8 -*-
"""移动模块：虚拟时间账（三个时间轴必须分开记）。"""
import math
V = 5.0; T_MEASURE = 5.0; T_SWITCH = 1.0; T_OPTICAL = 3.0; T_CLEAR = 2.0

class Motion:
    def __init__(self, pos=(0.0, 0.0), channel=1):
        self.pos = pos; self.channel = channel
        self.dist = 0.0
    def move_cost(self, q):
        return math.dist(self.pos, q) / V
    def apply(self, q, channel_after=None):
        self.dist += math.dist(self.pos, q)
        self.pos = q
        if channel_after is not None: self.channel = channel_after
