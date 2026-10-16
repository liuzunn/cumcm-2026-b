# -*- coding: utf-8 -*-
"""审计用：验证「三个表盘」设计是否成立（9点 / 51点仅场内环 / 51点含场外环）。"""
import sys, os, math
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
from b26 import search
from b26_q4_certificate import ring, bearings, max_gap_deg

CERT_RINGS = [(0.0,1,0.0),(950.0,10,0.0),(1250.0,10,18.0),
              (1650.0,10,0.0),(2250.0,10,18.0),(2700.0,10,0.0)]
CERT = [p for (a,n,ph) in CERT_RINGS for p in ring(n,a,ph)]
INNER = [p for (a,n,ph) in CERT_RINGS if a <= 1800.0 for p in ring(n,a,ph)]
COVER9 = search.COVER_9

def rep(name, S, P):
    dirs, _ = bearings(P, S)
    mg = max_gap_deg(dirs)
    print("%-34s P=(%7.1f,%7.1f)  可见方位 %2d  max_gap %7.2f  margin %+8.2f  %s"
          % (name, P[0], P[1], len(dirs), mg, 180.0-mg, "通过" if 180-mg >= 0 else "失败"))

P1 = (1750.0, 0.0)
print("=== 表盘 A/B/C 候选：同一个 P ===")
rep("A  Q3 九点证书", COVER9, P1)
rep("B  S51_b 仅场内环", INNER, P1)
rep("C  S51_b 含场外环", CERT, P1)
print()
print("场内环点数 =", len(INNER), " 全部证书点数 =", len(CERT))
print()
print("=== 认证最坏点（用于图注）===")
Pw = (1745.0*math.cos(math.radians(136.0)), 1745.0*math.sin(math.radians(136.0)))
rep("C  S51_b 含场外环", CERT, Pw)
rep("B  S51_b 仅场内环", INNER, Pw)
