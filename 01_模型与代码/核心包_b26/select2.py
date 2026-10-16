# -*- coding: utf-8 -*-
"""问题2 的三种第二个检测点选点策略（把理论结论正式接进主程序）。

理论依据（见《2026B_问题1-2_定位模型与检测点优化.md》）：
  D = (2δ/sinα)·sqrt(d1²+d2²+2·d1·d2·|cosα|)
  ① 两测点到源距离固定      -> α*=90°，D_min = 2√2·δ·d
  ② 第二点沿过首测点的垂线外移 -> ρ*=√2·d，α*=54.7°，D_min = 6·δ·d
  ③ 距离未知时按极小化极大选点
几何事实：α=90° ⟺ 第二测点落在「过源、且垂直于 源—首测点 连线」的直线上。
"""
import math
from . import locate

STRATEGIES = ("fixed90", "perp547", "dynamic")

def _rep(F):
    """可行域的代表点与它到 S1 的距离"""
    c = locate.centroid(F)
    return c

def pick_fixed90(S1, F):
    """固定 90°：把第二点放在过代表点、垂直于 S1→代表点 的直线上（对称取 |t| = d̂）"""
    G = _rep(F)
    if G is None: return None
    dx, dy = G[0]-S1[0], G[1]-S1[1]
    d = math.hypot(dx, dy)
    if d < 1e-6: return None
    ux, uy = dx/d, dy/d
    n = (-uy, ux)                       # 法向
    return (G[0] + d*n[0], G[1] + d*n[1])

def pick_perp547(S1, F):
    """54.7°：沿垂直于首测方向偏移 ρ* = √2·d̂（等距时的解析最优）"""
    G = _rep(F)
    if G is None: return None
    dx, dy = G[0]-S1[0], G[1]-S1[1]
    d = math.hypot(dx, dy)
    if d < 1e-6: return None
    ux, uy = dx/d, dy/d
    rho = math.sqrt(2.0)*d
    return (S1[0] - rho*uy, S1[1] + rho*ux)

def _diam_after(S1, th1, S2, G):
    """在假定源位于 G 时，两测点交会所得定位区域的直径"""
    th2 = math.degrees(math.atan2(G[1]-S2[1], G[0]-S2[0])) % 360.0
    w1 = locate.wedge_poly(S1, th1)
    if not w1: return float("inf")
    w2 = locate.wedge_poly(S2, th2)
    if not w2: return float("inf")
    inter = locate.intersect(w1, w2)
    return locate.diameter(inter)

def pick_dynamic(S1, th1, F, n_ang=12, n_rad=5, n_d=3):
    """动态优化：在**与固定策略同等路程预算**内网格扫描，取极小化极大者。

    候选：以 S1 为心、半径 ρ ∈ (0, cap] 的极坐标网格；cap = √2·d̂（与 fixed90 / perp547 同路程）。
    目标：min over S2 of max over 代表距离抽样 d 的 diam(区域)。
    """
    G = _rep(F)
    if G is None: return None
    dx, dy = G[0]-S1[0], G[1]-S1[1]
    d = math.hypot(dx, dy)
    if d < 1e-6: return None
    ux, uy = dx/d, dy/d
    cap = math.sqrt(2.0)*d
    # 代表距离抽样：沿 S1→G 方向取 0.5d ~ 1.5d
    samples = []
    for k in range(n_d):
        t = d*(0.5 + 1.0*k/(max(1, n_d-1)))
        samples.append((S1[0] + t*ux, S1[1] + t*uy))
    best, bestq = float("inf"), None
    for ia in range(n_ang):
        psi = 2*math.pi*ia/n_ang
        for ir in range(1, n_rad+1):
            rho = cap*ir/n_rad
            q = (S1[0] + rho*math.cos(psi), S1[1] + rho*math.sin(psi))
            worst = 0.0
            ok = True
            for Gs in samples:
                D = _diam_after(S1, th1, q, Gs)
                if not (D < 1e18): ok = False; break
                if D > worst: worst = D
            if ok and worst < best:
                best, bestq = worst, q
    return bestq

def pick_dynamicT(S1, th1, F, n_ang=12, n_rad=5, n_d=3, lo=0.5, hi=1.5):
    """动态选点（含路程项，无自由参数）：
    目标 J(q) = ‖S1→q‖ + max_d diam(测后区域)
    —— 两项都是"米"：前者是去那里的代价，后者是残留不确定度（将来还要用路程换）。
    这是把"走多远"与"测得准不准"放在同一量纲上的最小改动。
    """
    G = _rep(F)
    if G is None: return None
    dx, dy = G[0]-S1[0], G[1]-S1[1]
    d = math.hypot(dx, dy)
    if d < 1e-6: return None
    ux, uy = dx/d, dy/d
    cap = math.sqrt(2.0)*d
    samples = []
    for k in range(n_d):
        t = d*(lo + (hi-lo)*k/(max(1, n_d-1)))
        samples.append((S1[0] + t*ux, S1[1] + t*uy))
    best, bestq = float("inf"), None
    for ia in range(n_ang):
        psi = 2*math.pi*ia/n_ang
        for ir in range(1, n_rad+1):
            rho = cap*ir/n_rad
            q = (S1[0] + rho*math.cos(psi), S1[1] + rho*math.sin(psi))
            worst = 0.0; ok = True
            for Gs in samples:
                D = _diam_after(S1, th1, q, Gs)
                if not (D < 1e18): ok = False; break
                if D > worst: worst = D
            if not ok: continue
            J = rho + worst                       # ← 路程项 + 残留不确定度项，同为米
            if J < best: best, bestq = J, q
    return bestq

def pick_dynamicN(S1, th1, F):
    """动态选点（窄不确定集 ±20%）：验证"不确定集越窄，动态规则越接近基线"这一趋势"""
    return pick_dynamicT(S1, th1, F, lo=0.8, hi=1.2)

def pick(strategy, S1, th1, F):
    if strategy == "centroid": return None          # 基线：直接移到可行域中心
    if strategy == "dynamicT": return pick_dynamicT(S1, th1, F)
    if strategy == "dynamicN": return pick_dynamicN(S1, th1, F)
    if strategy == "fixed90": return pick_fixed90(S1, F)
    if strategy == "perp547": return pick_perp547(S1, F)
    if strategy == "dynamic": return pick_dynamic(S1, th1, F)
    raise ValueError("unknown strategy: %s" % strategy)
