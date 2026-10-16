# -*- coding: utf-8 -*-
"""冻结配置：本队正式采用的方案（单一事实来源，改这里就等于改方案）。"""
from . import search

CONFIG_NAME = "G-9点覆盖+自适应缺口驱动+就近复测"

COVER = search.COVER_9        # 圆心 + 8 点均匀分布在半径 1200 m 圆周上，覆盖裕量 173.2 m
COVER_MODE = "adaptive"       # 覆盖点与"待清除/待复测目标"统一按最近调度
STRATEGY = "centroid"         # 第二测点 = 可行域质心（不启用动态选点）
D_THRESHOLD = 40.0            # 定位区域直径门槛 = 2 × 清除半径 20 m
MAX_REFINE = 4
PORT = 2026                   # 官方模拟器默认端口
ARENA = "default"

def describe():
    ok, worst, margin = search.coverage_certificate(COVER)
    return dict(方案=CONFIG_NAME, 覆盖点数=len(COVER), 最大未覆盖距离_m=round(worst, 1),
                覆盖裕量_m=round(margin, 1), 覆盖证书合格=bool(ok),
                覆盖模式=COVER_MODE, 选点策略=STRATEGY, 清除门槛_m=D_THRESHOLD)
