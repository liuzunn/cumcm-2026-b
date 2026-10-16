# -*- coding: utf-8 -*-
"""Q4 检出证书算子（Stage A · 证明工具层）

【文件性质】04_CODE/b26/ 冻结包**之外**的新文件；不修改任何既有文件、不覆盖任何既有数据。
【依据】04_CODE/Q4_MVP设计.md  §4 / §7 / §8 / §9 / §11 / §20
【证据等级】本文件只提供"算子与自证"，不产生任何"官方/Mock 端到端"结论。

核心对象
--------
D             = {P : ||P|| <= R_DOMAIN}                  目标闭圆盘
S_c           = 频道 c 的证据集（已 /measure 的位置）
D(P)          = { phi(P->s) : s in S_c, ||P-s|| <= r_min }
E(S_c)        = { P in D : for all beta exists s: ||P-s|| <= r_min and phi(P->s) in [beta-90, beta+90] }

定理 1（精确判据，已证）
    P in E(S_c)  <=>  max_gap(D(P)) <= 180  <=>  D(P) 不被任何开半平面包含

保守规则 A13
    与 P 重合（||P-s|| < EPS_POS）的探测点**不计入** D(P)（题面未定义距离 0 时的覆盖角归属）。

本文件同时提供**独立第二条路径**（按定义直接枚举 beta），用于交叉验证判据实现。
"""

import math

R_DOMAIN = 1800.0
R_MIN = 1000.0
R_MAX = 1500.0
L_NEAR = 5.0
L_CLR = 20.0
EPS_POS = 1e-6
SECTOR_HALF_DEG = 90.0

# --------------------------------------------------------------------------
# 1. 环与候选族
# --------------------------------------------------------------------------

def ring(n, radius, phase_deg=0.0):
    """半径 radius、n 等分、初相 phase_deg 的环。radius<=0 时退化为圆心单点。"""
    if radius <= 0.0 or n <= 0:
        return [(0.0, 0.0)]
    out = []
    for k in range(n):
        a = math.radians(360.0 * k / n + phase_deg)
        out.append((radius * math.cos(a), radius * math.sin(a)))
    return out


def build_pts(rings):
    """rings: [(radius, n, phase_deg), ...] -> 点集 list[(x, y)]"""
    pts = []
    for (a, n, ph) in rings:
        pts.extend(ring(n, a, ph))
    return pts


def candidate_families():
    """Q4_MVP设计.md §9.3 的候选族 + 若干补充族。

    相位交错（同一族内相邻环相位相差 pi/n）用于消除"源与环点严格对齐"时的退化。
    """
    F = {}
    F['Q3_COVER_9'] = dict(rings=[(0.0, 1, 0.0), (1200.0, 8, 0.0)],
                           note='Q3 证书（负对照：无越界点，按定理 3 必然不可认证）')
    F['F8'] = dict(rings=[(0.0, 1, 0.0), (900.0, 8, 0.0), (2500.0, 8, 0.0)],
                   note='双环+圆心，同相')
    F['F8s'] = dict(rings=[(0.0, 1, 0.0), (900.0, 8, 22.5), (2500.0, 8, 0.0)],
                    note='双环+圆心，交错相位')
    F['F12'] = dict(rings=[(0.0, 1, 0.0), (1000.0, 12, 0.0), (2500.0, 12, 0.0)],
                    note='双环+圆心，同相')
    F['F12s'] = dict(rings=[(0.0, 1, 0.0), (1000.0, 12, 30.0), (2500.0, 12, 0.0)],
                     note='双环+圆心，交错相位')
    F['F12_4r'] = dict(rings=[(0.0, 1, 0.0), (1000.0, 12, 0.0), (1500.0, 12, 15.0), (2500.0, 12, 0.0)],
                       note='三环+圆心')
    F['F12_6r'] = dict(rings=[(0.0, 1, 0.0), (800.0, 12, 0.0), (1100.0, 12, 15.0),
                              (1500.0, 12, 0.0), (2100.0, 12, 15.0), (2600.0, 12, 0.0)],
                       note='五环+圆心（内外交错）')
    F['F16_6r'] = dict(rings=[(0.0, 1, 0.0), (800.0, 16, 0.0), (1100.0, 16, 11.25),
                              (1500.0, 16, 0.0), (2100.0, 16, 11.25), (2600.0, 16, 0.0)],
                       note='五环+圆心，n=16')
    F['F24_5r'] = dict(rings=[(0.0, 1, 0.0), (800.0, 24, 0.0), (1200.0, 24, 7.5),
                              (2100.0, 24, 0.0), (2600.0, 24, 7.5)],
                       note='四环+圆心，n=24')
    F['F36_6r'] = dict(rings=[(0.0, 1, 0.0), (700.0, 36, 0.0), (1100.0, 36, 5.0),
                              (1500.0, 36, 0.0), (2300.0, 36, 5.0), (2700.0, 36, 0.0)],
                       note='五环+圆心，n=36')
    # —— 以下两族由 b26_q4_verify.py --min-search 的系统搜索给出 ——
    F['MVP_41'] = dict(rings=[(0.0, 1, 0.0), (850.0, 8, 0.0), (1200.0, 8, 22.5),
                              (1700.0, 8, 0.0), (2300.0, 8, 22.5), (2700.0, 8, 0.0)],
                       note='最少点数搜索命中（41 点）：五环+圆心，n=8，相位交错 22.5°')
    F['REC_61'] = dict(rings=[(0.0, 1, 0.0), (950.0, 12, 0.0), (1250.0, 12, 15.0),
                              (1650.0, 12, 0.0), (2250.0, 12, 15.0), (2700.0, 12, 0.0)],
                       note='推荐备用（61 点）：五环+圆心，n=12，相位交错 15°，裕量更大')
    F['S51_a'] = dict(rings=[(0.0, 1, 0.0), (800.0, 10, 0.0), (1100.0, 10, 18.0),
                             (1500.0, 10, 0.0), (2100.0, 10, 18.0), (2600.0, 10, 0.0)],
                      note='51 点候选 a（五环+圆心，n=10）')
    F['S51_b'] = dict(rings=[(0.0, 1, 0.0), (950.0, 10, 0.0), (1250.0, 10, 18.0),
                             (1650.0, 10, 0.0), (2250.0, 10, 18.0), (2700.0, 10, 0.0)],
                      note='51 点候选 b（五环+圆心，n=10）')
    F['S51_c'] = dict(rings=[(0.0, 1, 0.0), (850.0, 10, 0.0), (1200.0, 10, 18.0),
                             (1700.0, 10, 0.0), (2300.0, 10, 18.0), (2700.0, 10, 0.0)],
                      note='51 点候选 c（与 41 点命中同阶梯，n=10）')
    return F


# --------------------------------------------------------------------------
# 2. 精确判据（定理 1）
# --------------------------------------------------------------------------

def bearings(P, S, r_min=R_MIN, eps_pos=EPS_POS):
    """返回 (方位角列表, 因与 P 重合而被丢弃的探测点数)。角度单位：度，[0,360)。"""
    out = []
    n_drop = 0
    px, py = P[0], P[1]
    for (sx, sy) in S:
        dx, dy = sx - px, sy - py
        d = math.hypot(dx, dy)
        if d <= eps_pos:
            n_drop += 1
            continue
        if d <= r_min:
            out.append(math.degrees(math.atan2(dy, dx)) % 360.0)
    return out, n_drop


def max_gap_deg(dirs):
    """圆上方位集合的最大相邻角间隙（含首尾环绕）。|dirs|<=1 时返回 360。"""
    k = len(dirs)
    if k <= 1:
        return 360.0
    d = sorted(dirs)
    g = 0.0
    for i in range(1, k):
        v = d[i] - d[i - 1]
        if v > g:
            g = v
    w = d[0] + 360.0 - d[k - 1]
    if w > g:
        g = w
    return g


def margin_at(P, S, r_min=R_MIN, eps_pos=EPS_POS):
    """margin = 180 - max_gap。margin >= 0 <=> P in E。返回 (margin, 计数点数, 丢弃数)。"""
    dirs, n_drop = bearings(P, S, r_min, eps_pos)
    return 180.0 - max_gap_deg(dirs), len(dirs), n_drop


# --------------------------------------------------------------------------
# 3. 按定义的独立实现（第二条原理路径，用于交叉验证）
# --------------------------------------------------------------------------

def detects(P, s, beta_deg, r, sector_half_deg=SECTOR_HALF_DEG):
    """按题面定义：探测点 s 对"位于 P、朝向 beta、半径 r"的源是否可检出。
    sector_half_deg=180 即"扇区退化为全圆"（全向退化对标用）。"""
    dx, dy = s[0] - P[0], s[1] - P[1]
    d = math.hypot(dx, dy)
    if d > r:
        return False
    ang = math.degrees(math.atan2(dy, dx))
    delta = (ang - beta_deg + 180.0) % 360.0 - 180.0
    return abs(delta) <= sector_half_deg + 1e-9


def in_E_definition(P, S, r_min=R_MIN, beta_step=0.5, sector_half_deg=SECTOR_HALF_DEG):
    """按定义直接检验：forall beta exists s 可检出。返回 (是否成立, 第一个反例 beta 或 None)。"""
    b = 0.0
    while b < 360.0 - 1e-12:
        ok = False
        for s in S:
            if detects(P, s, b, r_min, sector_half_deg):
                ok = True
                break
        if not ok:
            return False, b
        b += beta_step
    return True, None


def witness_beta_from_gap(P, S, r_min=R_MIN, eps_pos=EPS_POS):
    """由最大角间隙反解见证 beta：间隙长度 > 180 时取该间隙中点；否则返回 None。
    该 beta 的闭扇区完全落在开间隙内 => 没有任何探测点可检出。"""
    dirs, _ = bearings(P, S, r_min, eps_pos)
    k = len(dirs)
    if k == 0:
        return 0.0                      # 无任何证据：任意 beta 都是见证
    if k == 1:
        return (dirs[0] + 180.0) % 360.0  # 单个方位：取其反向，闭扇区 [th+90, th+270] 不含 th
    d = sorted(dirs)
    best, at = -1.0, None
    for i in range(k):
        a = d[i]
        b = d[(i + 1) % k]
        gap = (b - a) % 360.0
        if i == k - 1:
            gap = d[0] + 360.0 - d[k - 1]
        if gap > best:
            best, at = gap, a
    if best <= 180.0:
        return None
    return (at + best / 2.0) % 360.0


def verify_witness(P, S, beta_deg, r_min=R_MIN, sector_half_deg=SECTOR_HALF_DEG):
    """见证复核：给定 beta，是否确实无任何探测点可检出。"""
    for s in S:
        if detects(P, s, beta_deg, r_min, sector_half_deg):
            return False
    return True


# --------------------------------------------------------------------------
# 4. Q3 覆盖证书的独立复刻（C-2 用；采样约定与 b26/search.py 完全一致）
# --------------------------------------------------------------------------

def max_uncovered(cover, R=R_DOMAIN, step=20.0):
    """target: 圆域内任一点到最近探测点的最大距离。
    采样：n = int(R/step)+1，i,j in [-n, n]，格点 step，保留 x^2+y^2 <= R^2。"""
    n = int(R / step) + 1
    worst = 0.0
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * step, j * step
            if x * x + y * y > R * R:
                continue
            d = min(math.hypot(x - q[0], y - q[1]) for q in cover)
            if d > worst:
                worst = d
    return worst


def coverage_certificate(cover, r_min=R_MIN, R=R_DOMAIN, step=20.0):
    m = max_uncovered(cover, R, step)
    return (m <= r_min), m, r_min - m


# --------------------------------------------------------------------------
# 5. 代价模型
# --------------------------------------------------------------------------

def cost_model(n_probes, n_channels, t_measure=5.0, t_switch=1.0, v=5.0):
    """证书扫描的虚拟时间量级：每点每频道最坏 6 s（5 s 检测 + 1 s 切换）。行程另计。"""
    return dict(点数=n_probes, 频道数=n_channels,
                扫描上界_s=n_probes * n_channels * (t_measure + t_switch),
                单点单频道_s=t_measure + t_switch)


# --------------------------------------------------------------------------
# 6. 自证（验证器自身必须先被验证 —— 用户红线）
# --------------------------------------------------------------------------

def _s1_degenerate_cases():
    """S1：max_gap / margin 的退化情形。"""
    cases = []
    P = (0.0, 0.0)
    # 单点 -> 360 -> margin -180
    m, k, _ = margin_at(P, [(100.0, 0.0)])
    cases.append(('single_point', m == -180.0, m))
    # 两点对径 -> 180 -> margin 0
    m, k, _ = margin_at(P, [(100.0, 0.0), (-100.0, 0.0)])
    cases.append(('two_antipodal', abs(m) < 1e-9, m))
    # 两点非对径 -> 间隙 > 180 -> margin < 0
    m, k, _ = margin_at(P, [(100.0, 0.0), (100.0 * math.cos(math.radians(20)),
                                          100.0 * math.sin(math.radians(20)))])
    cases.append(('two_non_antipodal', m < 0.0, m))
    # 三点 0/120/240 -> 间隙 120 -> margin 60
    tri = [(math.cos(math.radians(a)) * 100, math.sin(math.radians(a)) * 100) for a in (0, 120, 240)]
    m, k, _ = margin_at(P, tri)
    cases.append(('three_120', abs(m - 60.0) < 1e-9, m))
    # 重合点被丢弃（A13）
    m, k, nd = margin_at(P, [(0.0, 0.0), (100.0, 0.0), (-100.0, 0.0)])
    cases.append(('coincident_dropped', nd == 1 and abs(m) < 1e-9, (m, nd)))
    # 跨 0/360 环绕：方位 350 与 10 -> 间隙 340 / 20 -> margin -160
    m, k, _ = margin_at(P, [(100.0 * math.cos(math.radians(350)), 100.0 * math.sin(math.radians(350))),
                            (100.0 * math.cos(math.radians(10)), 100.0 * math.sin(math.radians(10)))])
    cases.append(('wrap_around', abs(m - (-160.0)) < 1e-9, m))
    # 超过 r_min 的探测点不参与
    m, k, _ = margin_at(P, [(1500.0, 0.0)])
    cases.append(('out_of_range_ignored', m == -180.0 and k == 0, (m, k)))
    return cases


def _s2_criterion_vs_definition(seed=20260913, n_case=120, beta_step=1.0):
    """S2：精确判据 vs 按定义的 beta 枚举（两条原理不同的路径）。"""
    import random
    rng = random.Random(seed)
    bad = []
    bad_w = []
    miss = []
    n_fail = 0
    for t in range(n_case):
        # 随机证据集：围绕 P 的随机方位 / 半径
        P = (rng.uniform(-1800, 1800), rng.uniform(-1800, 1800))
        S = []
        for _ in range(rng.randint(1, 8)):
            a = rng.uniform(0, 360)
            d = rng.choice([rng.uniform(1, 200), rng.uniform(200, 1000), rng.uniform(1000, 1600)])
            S.append((P[0] + d * math.cos(math.radians(a)), P[1] + d * math.sin(math.radians(a))))
        m, k, _ = margin_at(P, S)
        crit = (m >= 0.0)
        defn_ok, b = in_E_definition(P, S, beta_step=beta_step)
        if crit and (not defn_ok):
            # 真不一致：判据说"保证成立"而定义找到反例 —— 不可能，若出现即判据实现有错
            bad.append(dict(P=P, m=m, crit=crit, defn=defn_ok, beta=b, k=k))
        if (not crit) and defn_ok:
            # 可解释：最大间隙超出量 (max_gap-180) 小于 beta 网格步长时，网格可能跨过反例区间
            miss.append(dict(P=P, 超出量_deg=round(-m, 6), beta步长=beta_step, k=k))
        if not crit:
            n_fail += 1
            # 见证必须存在且经定义复核
            w = witness_beta_from_gap(P, S)
            if w is None or not verify_witness(P, S, w):
                bad_w.append(dict(P=P, m=m, witness=w, note='witness_invalid'))
    max_exc = max([x['超出量_deg'] for x in miss], default=0.0)
    return dict(用例数=n_case, beta步长=beta_step, 判据判负用例数=n_fail,
                判据vs定义_不一致数=len(bad), 见证失败数=len(bad_w),
                网格未命中数=len(miss), 网格未命中_最大超出量_deg=round(max_exc, 6),
                网格未命中_可否由分辨率解释=bool(max_exc < beta_step + 1e-9),
                样例=bad[:2] + bad_w[:2])


def _s3_witness_definition_check(n=50, seed=7):
    """S3：所有判负点都必须能给出经定义复核的见证 beta。"""
    import random
    rng = random.Random(seed)
    ok, bad = 0, []
    for _ in range(n):
        P = (rng.uniform(-1700, 1700), rng.uniform(-1700, 1700))
        S = []
        for _ in range(rng.randint(1, 6)):
            a = rng.uniform(0, 360)
            d = rng.uniform(1, 1000)
            S.append((P[0] + d * math.cos(math.radians(a)), P[1] + d * math.sin(math.radians(a))))
        m, k, _ = margin_at(P, S)
        if m >= 0.0:
            continue
        w = witness_beta_from_gap(P, S)
        if w is not None and verify_witness(P, S, w):
            ok += 1
        else:
            bad.append((P, m, w))
    return dict(判负用例=ok + len(bad), 见证复核通过=ok, 失败=len(bad))


def _s4_lipschitz_empirical(n=3000, seed=11, kdrop=2.0, rc=8.0):
    """S4：认证所用 Lipschitz 界的经验有效性检验（单侧、固定子集）。

    声明的界（认证定理）：
        设 S_count = {s : kdrop*rc < d(P0,s) <= r_min - kdrop*rc}（在 P0 处定集合，之后固定不动），
        d_min_cell = min_{s in S_count} d(P0,s) - rc > 0，
        则对单元内任意 P1（||P1-P0|| <= rc）：
            max_gap(S_count, P1) <= max_gap(S_count, P0) + 2*rc/d_min_cell   （弧度）
    据此：max_gap(全证据集, P1) <= max_gap(S_count, P0) + 2*rc/d_min_cell
    （因为全证据集 ⊇ S_count，加入探测点只会减小 max_gap）。
    """
    import random
    rng = random.Random(seed)
    fam = candidate_families()['F12_6r']
    S = build_pts(fam['rings'])
    worst_ratio = 0.0
    viol = 0
    tested = 0
    lim = rc / math.sqrt(2.0)
    for _ in range(n):
        rho = rng.uniform(0, 1800)
        al = rng.uniform(0, 360)
        P0 = (rho * math.cos(math.radians(al)), rho * math.sin(math.radians(al)))
        dx, dy = rng.uniform(-lim, lim), rng.uniform(-lim, lim)
        P1 = (P0[0] + dx, P0[1] + dy)
        if math.hypot(P1[0], P1[1]) > R_DOMAIN + 50:
            continue
        d0 = [math.hypot(s[0] - P0[0], s[1] - P0[1]) for s in S]
        idx = [i for i, d in enumerate(d0) if d > kdrop * rc and d <= R_MIN - kdrop * rc]
        if len(idx) < 2:
            continue
        Ssub = [S[i] for i in idx]
        dmin_cell = max(1e-9, min(d0[i] for i in idx) - rc)
        bound_deg = 2.0 * rc / dmin_cell * (180.0 / math.pi)
        g0 = max_gap_deg([math.degrees(math.atan2(s[1] - P0[1], s[0] - P0[0])) % 360.0 for s in Ssub])
        g1 = max_gap_deg([math.degrees(math.atan2(s[1] - P1[1], s[0] - P1[0])) % 360.0 for s in Ssub])
        tested += 1
        inc = g1 - g0
        ratio = inc / bound_deg if bound_deg > 0 else 0.0
        worst_ratio = max(worst_ratio, ratio)
        if inc > bound_deg + 1e-9:
            viol += 1
    return dict(样本=n, 有效样本=tested, 位移上限_m=rc, kdrop=kdrop,
                最大占比=round(worst_ratio, 4), 越界次数=viol)


def _s5_degradation_C1(step=50.0, beta_samples=5, seed=3):
    """C-1：算子退化。sector_half = 180（全圆）时，E 必须逐点等于 ∪ B(s, r_min)。"""
    import random
    rng = random.Random(seed)
    fam = candidate_families()['F12_6r']
    S = build_pts(fam['rings'])
    betas = [360.0 * i / beta_samples for i in range(beta_samples)]
    n = int(R_DOMAIN / step) + 1
    tot, exc, mx = 0, 0, 0.0
    sample_bad = []
    for i in range(-n, n + 1, 1):
        for j in range(-n, n + 1, 1):
            x, y = i * step, j * step
            if x * x + y * y > R_DOMAIN * R_DOMAIN:
                continue
            P = (x, y)
            tot += 1
            # 定义：全圆扇区下，任取 beta 都可被"距离 <= r_min 的探测点"检出
            in_def = all(any(detects(P, s, b, R_MIN, 180.0) for s in S) for b in betas)
            in_union = any(math.hypot(s[0] - P[0], s[1] - P[1]) <= R_MIN for s in S)
            if in_def != in_union:
                exc += 1
                if len(sample_bad) < 3:
                    sample_bad.append((P, in_def, in_union))
    return dict(网格步长_m=step, 采样点=tot, 例外点=exc, beta采样=beta_samples, 样例=sample_bad)


def _s6_C2_certificate(step_list=(20.0, 10.0)):
    """C-2：证书退化。用本文件的独立复刻计算 COVER_9 的覆盖证书，
    并与冻结包 b26.search.coverage_certificate 的 20 m 结果对比。"""
    fam = candidate_families()['Q3_COVER_9']
    cover = build_pts(fam['rings'])
    out = {}
    for st in step_list:
        ok, worst, margin = coverage_certificate(cover, R_MIN, R_DOMAIN, st)
        out['%g m' % st] = dict(最大未覆盖_m=round(worst, 4), 裕量_m=round(margin, 4), 合格=bool(ok))
    frozen = None
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from b26 import search as _s
        fok, fworst, fmargin = _s.coverage_certificate(_s.COVER_9)
        frozen = dict(最大未覆盖_m=round(fworst, 4), 裕量_m=round(fmargin, 4), 合格=bool(fok))
    except Exception as e:
        frozen = dict(错误=str(e)[:120])
    same = (frozen.get('最大未覆盖_m') == out['20 m']['最大未覆盖_m']) if '错误' not in frozen else None
    return dict(本文件复刻=out, 冻结包b26_search=frozen, 逐位一致_20m=same,
                论文采用值='173.2 m（10 m 网格，更保守；见 Q4_MVP设计.md 矛盾 1 处置建议）')


def self_test(verbose=True):
    """验证器自证套件（S1—S6）。返回报告 dict。"""
    rep = {}
    rep['S1_退化情形'] = _s1_degenerate_cases()
    rep['S2_判据vs定义'] = _s2_criterion_vs_definition()
    rep['S3_见证复核'] = _s3_witness_definition_check()
    rep['S4_Lipschitz经验检验'] = _s4_lipschitz_empirical()
    rep['S5_C1_退化'] = _s5_degradation_C1()
    rep['S6_C2_证书'] = _s6_C2_certificate()
    ok1 = all(c[1] for c in rep['S1_退化情形'])
    s2 = rep['S2_判据vs定义']
    ok2 = (s2['判据vs定义_不一致数'] == 0) and (s2['见证失败数'] == 0) and (s2['网格未命中_可否由分辨率解释'] is True)
    ok3 = rep['S3_见证复核']['失败'] == 0
    ok4 = rep['S4_Lipschitz经验检验']['越界次数'] == 0
    ok5 = rep['S5_C1_退化']['例外点'] == 0
    ok6 = rep['S6_C2_证书']['逐位一致_20m'] is True
    rep['自证结论'] = dict(S1=ok1, S2=ok2, S3=ok3, S4=ok4, S5=ok5, S6=ok6,
                          全部通过=bool(ok1 and ok2 and ok3 and ok4 and ok5 and ok6))
    if verbose:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


if __name__ == '__main__':
    self_test()
