# -*- coding: utf-8 -*-
"""定位模块：把"示向度 ±1°"变成可计算的定位区域。"""
import math
DELTA_DEG = 1.0
DELTA_RAD = math.radians(DELTA_DEG)

def clip(poly, n, c, keep_le):
    out = []
    for i in range(len(poly)):
        P, Q = poly[i], poly[(i + 1) % len(poly)]
        fp = n[0]*P[0] + n[1]*P[1] - c
        fq = n[0]*Q[0] + n[1]*Q[1] - c
        okp = (fp <= 1e-12) if keep_le else (fp >= -1e-12)
        okq = (fq <= 1e-12) if keep_le else (fq >= -1e-12)
        if okp: out.append(P)
        if okp != okq:
            t = fp / (fp - fq)
            out.append((P[0] + t*(Q[0]-P[0]), P[1] + t*(Q[1]-P[1])))
    return out

def disk_poly(cx, cy, r, k=72, circumscribe=True):
    """圆盘的多边形表示；circumscribe=True 时外切（保守地"多留一些"）"""
    rr = r / math.cos(math.pi/k) if circumscribe else r
    return [(cx + rr*math.cos(2*math.pi*i/k), cy + rr*math.sin(2*math.pi*i/k)) for i in range(k)]

_DISK_CACHE = {}
def _disk(R):
    if R not in _DISK_CACHE: _DISK_CACHE[R] = disk_poly(0.0, 0.0, R)
    return _DISK_CACHE[R]

def wedge_poly(s, theta_deg, R=1800.0, delta=DELTA_DEG):
    """以 s 为顶点、中轴 theta、半角 delta 的楔形 ∩ 目标圆域"""
    a = math.radians(theta_deg)
    dd = math.radians(delta)
    n1 = (-math.sin(a-dd), math.cos(a-dd)); c1 = n1[0]*s[0] + n1[1]*s[1]
    n2 = (-math.sin(a+dd), math.cos(a+dd)); c2 = n2[0]*s[0] + n2[1]*s[1]
    poly = list(_disk(R))
    poly = clip(poly, n1, c1, False)
    if not poly: return []
    poly = clip(poly, n2, c2, True)
    return poly

def intersect(poly_a, poly_b):
    """两个凸多边形的交（把 b 的每条边当作半平面裁剪 a）"""
    if not poly_a or not poly_b: return []
    out = poly_a
    m = len(poly_b)
    for i in range(m):
        P, Q = poly_b[i], poly_b[(i + 1) % m]
        ex, ey = Q[0]-P[0], Q[1]-P[1]
        n = (ey, -ex)                      # 逆时针多边形的内法向
        c = n[0]*P[0] + n[1]*P[1]
        # 保证方向：取 poly_b 的重心判定
        cx = sum(p[0] for p in poly_b)/m; cy = sum(p[1] for p in poly_b)/m
        if n[0]*cx + n[1]*cy > c: n = (-n[0], -n[1]); c = -c
        out = clip(out, n, c, True)
        if not out: return []
    return out

def clip_disk(poly, cx, cy, r):
    """用圆盘裁剪（外切多边形，保守）"""
    return intersect(poly, disk_poly(cx, cy, r))

def diameter(poly):
    if not poly or len(poly) < 2: return 0.0
    return max(math.dist(a, b) for a in poly for b in poly)

def centroid(poly):
    if not poly: return None
    return (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))

def contains(poly, p):
    """点是否在凸多边形内（含边界）"""
    if not poly or len(poly) < 3: return False
    m = len(poly); sgn = 0
    for i in range(m):
        a, b = poly[i], poly[(i+1) % m]
        cr = (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
        if cr > 1e-9: s = 1
        elif cr < -1e-9: s = -1
        else: continue
        if sgn == 0: sgn = s
        elif sgn != s: return False
    return True

def project(poly, p):
    """把点投影到凸多边形上（投影到凸集是非扩张的，用于构造"保证覆盖"的取样网）"""
    if not poly: return p
    if contains(poly, p): return p
    best, bq = float("inf"), p
    m = len(poly)
    for i in range(m):
        a, b = poly[i], poly[(i+1) % m]
        ex, ey = b[0]-a[0], b[1]-a[1]
        L2 = ex*ex + ey*ey
        t = 0.0 if L2 < 1e-15 else max(0.0, min(1.0, ((p[0]-a[0])*ex + (p[1]-a[1])*ey)/L2))
        q = (a[0]+t*ex, a[1]+t*ey)
        d = math.dist(q, p)
        if d < best: best, bq = d, q
    return bq

def area(poly):
    if not poly or len(poly) < 3: return 0.0
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i+1) % len(poly)]
        s += x1*y2 - x2*y1
    return abs(s)/2

class Ledger:
    """可行域账本：每个频道一个可行域 {channel: polygon}"""
    def __init__(self, channels, R=1800.0):
        self.R = R
        self.F = {c: disk_poly(0.0, 0.0, R) for c in channels}
        self.probes = {c: [] for c in channels}
        self.seen_dc = set()
    def on_direction(self, c, s, theta_deg):
        self.probes[c].append(s)
        self.seen_dc.add(c)
        w = wedge_poly(s, theta_deg, self.R)
        self.F[c] = intersect(self.F[c], w)
        self.F[c] = clip_disk(self.F[c], s[0], s[1], 1500.0)
    def on_no_signal(self, c, s):
        self.probes[c].append(s)
    def on_cleared(self, c):
        self.F[c] = []
        self.seen_dc.add(c)
    def region(self, c):
        return self.F[c]
    def diam(self, c):
        return diameter(self.F[c])
    def point(self, c):
        return centroid(self.F[c])
    def is_degenerate(self, c):
        return len(self.F[c]) < 3
