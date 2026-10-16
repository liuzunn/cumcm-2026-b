# -*- coding: utf-8 -*-
"""Q4 证书严格验证器（Stage A · 证明工具层）

【文件性质】04_CODE/b26/ 冻结包之外的新文件；不修改任何既有文件。
【依据】04_CODE/Q4_MVP设计.md §10（验证算法）与 §28.2（Stage A 出口判据）
【输出】05_EXPERIMENTS/results/_work_b26_q4_cert.json（**新文件**，不覆盖任何既有数据）

管线（用户指定）
----------------
候选点集 -> 精确 E_Q4 判据 -> 离散筛查 -> 临界区域细分 -> Lipschitz 认证 -> 最小裕量 -> PASS/UNVERIFIED

认证定理（本验证器使用，已由自证套件 S4 经验检验）
--------------------------------------------------
对单元中心 P0、单元最大位移半径 rc：
    S_count = { s : kdrop*rc < d(P0,s) <= r_min - kdrop*rc }
    margin  = 180 - max_gap( S_count 在 P0 处的方位 )
    bound   = 2 * rc / ( min_{s in S_count} d(P0,s) - rc ) * (180/pi)
若 margin > bound，则单元内任意点的 max_gap <= 180 - (margin - bound) < 180  =>  该单元被认证。
理由：单元内全证据集 ⊇ S_count（越界进入的探测点只会减小 max_gap；S_count 成员在单元内始终
      满足 1e-6 < d <= r_min），且各方位的漂移 <= rc/d，最大间隙两端漂移合计 <= 2*rc/d。

命令
----
    python b26_q4_verify.py                 # 自证 + 全部候选族认证
    python b26_q4_verify.py --family F12_6r # 只认证一个族（详细输出）
    python b26_q4_verify.py --selftest      # 只跑自证套件
    python b26_q4_verify.py --search        # 候选点集自动搜索（回答"最少需要多少点"）
"""

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b26_q4_certificate import (R_DOMAIN, R_MIN, EPS_POS, candidate_families, build_pts,
                                margin_at, max_gap_deg, witness_beta_from_gap, ring,
                                verify_witness, self_test, cost_model)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, '05_EXPERIMENTS', 'results', '_work_b26_q4_cert.json')


# --------------------------------------------------------------------------
# 1. 向量化核心：距离矩阵 -> max_gap / margin
# --------------------------------------------------------------------------

def dist_ang_matrices(Px, Py, S):
    Sx = np.asarray([s[0] for s in S], dtype=float)
    Sy = np.asarray([s[1] for s in S], dtype=float)
    dx = Sx[None, :] - Px[:, None]
    dy = Sy[None, :] - Py[:, None]
    d = np.hypot(dx, dy)
    ang = np.degrees(np.arctan2(dy, dx)) % 360.0
    return d, ang


def max_gap_and_count(d, ang, r_min=R_MIN, eps_pos=EPS_POS):
    """对每一行给出 (max_gap_deg, 参与计数的探测点数)。实现与定理 1 的判据一致。"""
    n, m = d.shape
    valid = (d <= r_min) & (d > eps_pos)
    k = valid.sum(axis=1)
    a = np.where(valid, ang, np.nan)
    a = np.sort(a, axis=1)                       # 有效项在前（升序），NaN 在末尾
    if m >= 2:
        diffs = np.diff(a, axis=1)
        diffs = np.nan_to_num(diffs, nan=0.0)
        idx = np.arange(m - 1)[None, :]
        ok = idx < (k - 1)[:, None]
        g = np.where(ok, diffs, 0.0)
        mg = g.max(axis=1)
        kk = np.maximum(k, 1)
        last = np.nan_to_num(a[np.arange(n), kk - 1], nan=0.0)
        wrap = a[:, 0] + 360.0 - last
        wrap = np.where(k >= 2, wrap, 360.0)
        mg = np.where(k >= 2, np.maximum(mg, wrap), 360.0)
    else:
        mg = np.full(n, 360.0)
    return mg, k


# --------------------------------------------------------------------------
# 2. 基础网格扫描（离散筛查）
# --------------------------------------------------------------------------

def sweep(S, rho_step=5.0, alpha_step_deg=1.0, rho_max=R_DOMAIN):
    rhos = np.arange(0.0, rho_max + 1e-9, rho_step)
    alphas = np.arange(0.0, 360.0, alpha_step_deg)
    ar = np.radians(alphas)
    ca, sa = np.cos(ar), np.sin(ar)
    worst = dict(margin=1e9, rho=None, alpha=None, k=None)
    n_neg = 0
    total = 0
    margins_min_per_rho = []
    for rho in rhos:
        Px = rho * ca
        Py = rho * sa
        d, ang = dist_ang_matrices(Px, Py, S)
        mg, k = max_gap_and_count(d, ang)
        marg = 180.0 - mg
        total += len(marg)
        n_neg += int((marg < 0).sum())
        i = int(np.argmin(marg))
        margins_min_per_rho.append(float(marg[i]))
        if marg[i] < worst['margin']:
            worst = dict(margin=float(marg[i]), rho=float(rho), alpha=float(alphas[i]),
                         k=int(k[i]), max_gap=float(mg[i]))
    return dict(采样点数=total, 例外点数=marg_neg_count(margins_min_per_rho, n_neg),
                最小裕量_deg=round(worst['margin'], 6), 最坏点=dict(rho=worst['rho'], alpha=worst['alpha']),
                最坏点计数点数=worst['k'], 最坏点max_gap=round(worst['max_gap'], 6),
                负裕量点数=n_neg,
                逐rho最小裕量的最小值=round(min(margins_min_per_rho), 6))


def marg_neg_count(_per_rho, n_neg):
    return n_neg


# --------------------------------------------------------------------------
# 3. 单元认证（临界细分 + Lipschitz 认证）
# --------------------------------------------------------------------------

def certify(S, rho_step=5.0, alpha_step_deg=1.0, kdrop=2.0, rc_min=0.02,
            max_levels=30, max_cells=4000000, batch=4096, verbose=False):
    """返回认证报告。certified_min_margin = min over 认证单元 of (margin - bound)。"""
    rhos = np.arange(0.0, R_DOMAIN + 1e-9, rho_step)
    alphas = np.arange(0.0, 360.0, alpha_step_deg)
    # 基础单元：(rho_c, alpha_c, rc, h_rho, h_alpha)；rc = 单元内最大位移
    rows = []
    for rho in rhos:
        h_rho = rho_step / 2.0
        h_al = alpha_step_deg / 2.0
        arc = math.radians(h_al) * max(rho, 1.0)
        rc = math.sqrt(h_rho ** 2 + arc ** 2)
        for al in alphas:
            rows.append((rho, al, rc, h_rho, h_al))
    cells = np.asarray(rows, dtype=float)
    certified_min = 1e9
    n_certified = 0
    uncertified = []
    unc_area = 0.0
    total_cells = 0
    level = 0
    cap_hit = False
    bind = None
    while len(cells):
        nxt = []
        for b0 in range(0, len(cells), batch):
            chunk = cells[b0:b0 + batch]
            total_cells += len(chunk)
            if total_cells > max_cells:
                cap_hit = True
                break
            rho = chunk[:, 0]
            al = np.radians(chunk[:, 1])
            rc = chunk[:, 2]
            Px = rho * np.cos(al)
            Py = rho * np.sin(al)
            d, ang = dist_ang_matrices(Px, Py, S)
            keep = (d > (kdrop * rc)[:, None]) & (d <= (R_MIN - kdrop * rc)[:, None])
            n_keep = keep.sum(axis=1)
            a = np.where(keep, ang, np.nan)
            a = np.sort(a, axis=1)
            m = a.shape[1]
            if m >= 2:
                diffs = np.nan_to_num(np.diff(a, axis=1), nan=0.0)
                idx = np.arange(m - 1)[None, :]
                ok = idx < (n_keep - 1)[:, None]
                g = np.where(ok, diffs, 0.0)
                mg = g.max(axis=1)
                kk = np.maximum(n_keep, 1)
                last = np.nan_to_num(a[np.arange(len(chunk)), kk - 1], nan=0.0)
                wrap = np.where(n_keep >= 2, a[:, 0] + 360.0 - last, 360.0)
                mg = np.where(n_keep >= 2, np.maximum(mg, wrap), 360.0)
            else:
                mg = np.full(len(chunk), 360.0)
            margin = 180.0 - mg
            margin = np.where(n_keep >= 2, margin, -180.0)
            dmin = np.where(keep, d, np.inf).min(axis=1) - rc
            dmin = np.maximum(dmin, 1e-9)
            bound = 2.0 * rc / dmin * (180.0 / math.pi)
            ok_cell = (margin > bound) & (n_keep >= 2)
            if ok_cell.any():
                cvals = (margin - bound)[ok_cell]
                j = int(np.argmin(cvals))
                if float(cvals[j]) < certified_min:
                    certified_min = float(cvals[j])
                    idxs = np.where(ok_cell)[0]
                    i0 = int(idxs[j])
                    bind = dict(rho=round(float(chunk[i0, 0]), 4), alpha=round(float(chunk[i0, 1]), 4),
                                rc=round(float(chunk[i0, 2]), 6), margin=round(float(margin[i0]), 4),
                                bound=round(float(bound[i0]), 4), 层级=level)
                n_certified += int(ok_cell.sum())
            bad = np.where(~ok_cell)[0]
            if len(bad) == 0:
                continue
            if float(chunk[bad[0], 2]) > rc_min and level < max_levels:
                for i in bad:
                    r0, a0, rc0, hr, ha = chunk[i]
                    for dr in (-hr / 2.0, hr / 2.0):
                        for da in (-ha / 2.0, ha / 2.0):
                            r1 = float(np.clip(r0 + dr, 0.0, R_DOMAIN))
                            a1 = float((a0 + da) % 360.0)
                            arc1 = math.radians(ha / 2.0) * max(r1, 1.0)
                            rc1 = math.sqrt((hr / 2.0) ** 2 + arc1 ** 2)
                            nxt.append((r1, a1, rc1, hr / 2.0, ha / 2.0))
            else:
                for i in bad:
                    r0, a0, rc0, hr, ha = chunk[i]
                    unc_area += (2.0 * hr) * (2.0 * math.radians(ha) * max(r0, 1.0))
                    if len(uncertified) < 200:
                        uncertified.append(dict(rho=round(float(r0), 4), alpha=round(float(a0), 4),
                                                rc=round(float(rc0), 6), margin=round(float(margin[i]), 4),
                                                bound=round(float(bound[i]), 4), 层级=level))
        if cap_hit:
            break
        cells = np.asarray(nxt, dtype=float) if nxt else np.zeros((0, 5))
        level += 1
        if verbose:
            print('  [certify] level=%d next=%d certified_min=%.4f unc=%d'
                  % (level, len(cells), certified_min, len(uncertified)))
    return dict(细胞总数=total_cells, 已认证细胞=n_certified, 未认证细胞=len(uncertified),
                未认证区域面积估计_m2=round(unc_area, 3), 最大细分层级=level,
                达到细胞上限=bool(cap_hit),
                认证最小裕量_deg=round(certified_min, 6) if n_certified else None,
                绑定单元=bind, 未认证样例=uncertified[:5])


# --------------------------------------------------------------------------
# 4. C-1 稠密退化检验（numpy，5 m 网格）
# --------------------------------------------------------------------------

def dense_C1(S, step=5.0, beta_samples=8, sector_half=180.0):
    n = int(R_DOMAIN / step)
    g = np.arange(-n, n + 1) * step
    X, Y = np.meshgrid(g, g)
    IN = (X ** 2 + Y ** 2) <= R_DOMAIN ** 2
    Px = X[IN].ravel()
    Py = Y[IN].ravel()
    d, ang = dist_ang_matrices(Px, Py, S)
    in_union = (d <= R_MIN).any(axis=1)
    # 全圆扇区下：对任意 beta，"存在可检出探测点" <=> "存在距离 <= r_min 的探测点"
    ok = True
    for i in range(beta_samples):
        beta = 360.0 * i / beta_samples
        delta = np.abs(((ang - beta + 180.0) % 360.0) - 180.0)
        det = ((d <= R_MIN) & (delta <= sector_half + 1e-9)).any(axis=1)
        ok = ok and bool(np.array_equal(det, in_union))
    exc = 0 if ok else int((in_union != det).sum())
    return dict(网格步长_m=step, 采样点数=int(Px.size), beta采样=beta_samples,
                扇区半角_deg=sector_half, 逐点一致=bool(ok), 例外点=exc)


# --------------------------------------------------------------------------
# 5. 单族完整报告
# --------------------------------------------------------------------------

def verify_family(name, rings, rho_step=5.0, alpha_step_deg=1.0, do_certify=True,
                  do_convergence=True, verbose=True):
    S = build_pts(rings)
    t0 = time.time()
    rep = dict(族名=name, 点数=len(S), 环=rings)
    rep['代价模型'] = cost_model(len(S), 20)
    sw = sweep(S, rho_step, alpha_step_deg)
    rep['基础扫描'] = sw
    b = witness_beta_from_gap((sw['最坏点']['rho'] * math.cos(math.radians(sw['最坏点']['alpha'])),
                               sw['最坏点']['rho'] * math.sin(math.radians(sw['最坏点']['alpha']))), S)
    P_worst = (sw['最坏点']['rho'] * math.cos(math.radians(sw['最坏点']['alpha'])),
               sw['最坏点']['rho'] * math.sin(math.radians(sw['最坏点']['alpha'])))
    rep['最坏点见证'] = dict(beta=b, 见证经定义复核=(None if b is None else verify_witness(P_worst, S, b)))
    if do_certify:
        rep['单元认证'] = certify(S, rho_step, alpha_step_deg, verbose=False)
    if do_convergence:
        conv = {}
        for (rs, as_) in ((8.0, 2.0), (5.0, 1.0), (2.5, 0.5)):
            s2 = sweep(S, rs, as_)
            conv['rho%g_a%g' % (rs, as_)] = dict(采样点数=s2['采样点数'],
                                                 最小裕量_deg=s2['最小裕量_deg'])
        rep['网格收敛性'] = conv
    rep['耗时_s'] = round(time.time() - t0, 2)
    c = rep.get('单元认证', {})
    cm = c.get('认证最小裕量_deg')
    unc = c.get('未认证细胞')
    cap = c.get('达到细胞上限', True)
    rep['结论'] = ('PASS' if (cm is not None and cm > 0 and unc == 0 and not cap) else 'UNVERIFIED')
    if verbose:
        print('[%s] 点数=%d 最小裕量=%.3f° 认证最小裕量=%s 结论=%s (%.1fs)'
              % (name, len(S), sw['最小裕量_deg'], cm, rep['结论'], rep['耗时_s']))
    return rep


# --------------------------------------------------------------------------
# 6. 候选点集自动搜索（回答"最少需要多少点"）
# --------------------------------------------------------------------------

def ladder_candidates():
    """生成候选族：n ∈ {8,12,16,24,36} × 半径阶梯。相位交错。"""
    out = {}
    ladders = {
        'A_3r': [0.0, 900.0, 2500.0],
        'B_3r': [0.0, 1000.0, 2500.0],
        'C_3r': [0.0, 1200.0, 2500.0],
        'D_4r': [0.0, 900.0, 1500.0, 2500.0],
        'E_4r': [0.0, 1000.0, 1500.0, 2500.0],
        'F_5r': [0.0, 800.0, 1100.0, 1500.0, 2500.0],
        'G_5r': [0.0, 900.0, 1200.0, 1600.0, 2500.0],
        'H_6r': [0.0, 800.0, 1100.0, 1500.0, 2100.0, 2600.0],
        'I_6r': [0.0, 900.0, 1200.0, 1600.0, 2200.0, 2700.0],
    }
    for ln, radii in ladders.items():
        for n in (8, 12, 16, 24, 36):
            rings = [(0.0, 1, 0.0)]
            for idx, r in enumerate(radii[1:]):
                ph = (180.0 / n) * (idx % 2)
                rings.append((r, n, ph))
            out['%s_n%d' % (ln, n)] = dict(rings=rings, note='自动搜索候选')
    return out


def min_search(verbose=True):
    """系统性搜索"最少点数"的通过构型：
    阶梯 × 角向密度 -> 粗筛（10 m × 2°）-> 按点数升序精认证 -> 第一个 PASS 即为当前最小。"""
    ladders = [
        [0.0, 800.0, 1100.0, 1500.0, 2100.0, 2600.0],
        [0.0, 900.0, 1200.0, 1600.0, 2200.0, 2700.0],
        [0.0, 850.0, 1150.0, 1550.0, 2150.0, 2650.0],
        [0.0, 950.0, 1250.0, 1650.0, 2250.0, 2700.0],
        [0.0, 900.0, 1200.0, 1600.0, 2500.0],
        [0.0, 800.0, 1100.0, 1500.0, 2500.0],
        [0.0, 1000.0, 1300.0, 1700.0, 2500.0],
        [0.0, 850.0, 1200.0, 1700.0, 2300.0, 2700.0],
    ]
    cands = []
    for li, radii in enumerate(ladders):
        for n in (8, 10, 12, 14, 16, 20, 24):
            rings = [(0.0, 1, 0.0)]
            for k, r in enumerate(radii[1:]):
                rings.append((r, n, (180.0 / n) * (k % 2)))
            cands.append(dict(名='L%d_n%d' % (li, n), rings=rings,
                              点数=len(build_pts(rings))))
    cands.sort(key=lambda c: c['点数'])
    coarse = []
    for c in cands:
        S = build_pts(c['rings'])
        sw = sweep(S, 10.0, 2.0)
        c['粗筛最小裕量'] = sw['最小裕量_deg']
        coarse.append(c)
        if verbose:
            print('  [min] %-10s 点数=%3d 粗筛裕量=%8.3f°' % (c['名'], c['点数'], c['粗筛最小裕量']))
    best = None
    tried = []
    for c in sorted([x for x in coarse if x['粗筛最小裕量'] >= 8.0], key=lambda x: x['点数']):
        rep = verify_family(c['名'], c['rings'], verbose=False)
        tried.append(dict(名=c['名'], 点数=c['点数'], 结论=rep['结论'],
                          认证最小裕量=rep.get('单元认证', {}).get('认证最小裕量_deg'),
                          基础最小裕量=rep['基础扫描']['最小裕量_deg'],
                          未认证细胞=rep.get('单元认证', {}).get('未认证细胞')))
        if verbose:
            print('  [min] 认证 %-10s 点数=%3d -> %s (认证裕量=%s, 未认证细胞=%s)'
                  % (c['名'], c['点数'], tried[-1]['结论'], tried[-1]['认证最小裕量'],
                     tried[-1]['未认证细胞']))
        if rep['结论'] == 'PASS' and best is None:
            best = dict(名=c['名'], 点数=c['点数'], rings=c['rings'],
                        认证最小裕量=tried[-1]['认证最小裕量'],
                        基础最小裕量=tried[-1]['基础最小裕量'])
            break
    return dict(候选数=len(coarse), 粗筛=coarse, 精认证=tried, 最小通过构型=best)


def t5a_recompute(step=100.0):
    """T5-a 历史数字重算：60.3% / 33.4% / 93.3% 对应的三组配置。

    配置来源：05_EXPERIMENTS/scripts/_work_b26_q2.py:77 的（外环 n@a + 内环 n@a, 相位）
    判据：Q4_MVP设计.md 定理 1 的精确角隙判据（保守 A13：与 P 重合的探测点不计入）
    网格：100 m（与文档百分比隐含的分母 1009 一致）
    """
    import random  # noqa
    cases = [
        ('6@1700 + 6@700', 6, 1700.0, 6, 700.0, 28.6479),
        ('8@1700 + 8@700', 8, 1700.0, 8, 700.0, 22.9183),
        ('8@1500 + 8@2600', 8, 1500.0, 8, 2600.0, 0.0),
    ]
    out = []
    n = int(R_DOMAIN / step)
    for (nm, n1, r1, n2, r2, off) in cases:
        S = ring(n1, r1, 0.0) + ring(n2, r2, off)
        tot = 0
        bad = 0
        ex = []
        worse = 0.0
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = i * step, j * step
                if x * x + y * y > R_DOMAIN * R_DOMAIN:
                    continue
                tot += 1
                m, k, nd = margin_at((x, y), S)
                if m < 0:
                    bad += 1
                    worse = min(worse, m)
                    if len(ex) < 3:
                        ex.append(dict(P=[x, y], margin=round(m, 3), 计数点数=k, 丢弃重合=nd))
        out.append(dict(配置=nm, 点数=len(S), 采样点=tot, 不可保证点=bad,
                        不可保证比例_pct=round(100.0 * bad / tot, 2),
                        最坏裕量_deg=round(worse, 3), 样例=ex))
    doc = {'6@1700 + 6@700': 60.3, '8@1700 + 8@700': 33.4, '8@1500 + 8@2600': 93.3}
    for r in out:
        r['文档值_pct'] = doc.get(r['配置'])
        if r['文档值_pct'] is not None:
            r['差值_pct'] = round(r['不可保证比例_pct'] - r['文档值_pct'], 2)
    return dict(网格步长_m=step, 判据='定理 1 精确角隙（A13 保守）', 结果=out,
                说明='60.3/33.4/93.3 出自未归档脚本；此处为统一验证器的重算值，论文以重算值为准')


def search(rho_step=10.0, alpha_step_deg=2.0, verbose=True):
    """两级筛选：粗筛（基础扫描）-> 精认证。返回按点数升序的通过/未通过清单。"""
    cands = ladder_candidates()
    coarse = []
    for name, d in sorted(cands.items(), key=lambda kv: len(build_pts(kv[1]['rings']))):
        S = build_pts(d['rings'])
        sw = sweep(S, rho_step, alpha_step_deg)
        coarse.append(dict(族名=name, 点数=len(S), 最小裕量=sw['最小裕量_deg']))
        if verbose:
            print('  [search] %-10s 点数=%3d 粗筛最小裕量=%8.3f°' % (name, len(S), sw['最小裕量_deg']))
    good = [c for c in coarse if c['最小裕量'] >= 5.0]
    fine = []
    for c in sorted(good, key=lambda x: x['点数'])[:12]:
        rep = verify_family(c['族名'], cands[c['族名']]['rings'], verbose=False)
        fine.append(dict(族名=c['族名'], 点数=c['点数'], 结论=rep['结论'],
                         认证最小裕量=rep.get('单元认证', {}).get('认证最小裕量_deg'),
                         基础最小裕量=rep['基础扫描']['最小裕量_deg']))
        if verbose:
            print('  [search] 精认证 %-10s -> %s (认证裕量=%s)'
                  % (c['族名'], fine[-1]['结论'], fine[-1]['认证最小裕量']))
    return dict(粗筛=coarse, 精认证=fine)


# --------------------------------------------------------------------------
# 7. 主流程
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default=None)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--search', action='store_true')
    ap.add_argument('--min-search', dest='min_search', action='store_true')
    ap.add_argument('--t5a', action='store_true')
    ap.add_argument('--no-certify', action='store_true')
    ap.add_argument('--out', default=OUT_JSON)
    a = ap.parse_args()

    report = dict(生成时间=time.strftime('%Y-%m-%d %H:%M:%S'),
                  说明='Q4 证书严格验证（Stage A）。全部结果为【模型推导】+【本轮计算】，不含官方/Mock 端到端结论。',
                  参数=dict(rho_step=5.0, alpha_step=1.0, kdrop=2.0, r_min=R_MIN, R=R_DOMAIN,
                            设计余量_gamma_deg=10.0))

    if a.selftest or not a.family:
        print('=== 验证器自证（S1—S6）===')
        report['自证'] = self_test(verbose=True)
    if a.t5a:
        print('=== T5-a 历史数字重算（统一验证器）===')
        report['T5a_重算'] = t5a_recompute()
        print(json.dumps(report['T5a_重算'], ensure_ascii=False, indent=1))
    if a.selftest:
        pass
    elif a.t5a:
        pass
    else:
        print('\n=== C-1 稠密退化检验（5 m 网格，全圆扇区）===')
        fam = candidate_families()['F12_6r']
        S0 = build_pts(fam['rings'])
        report['C1_稠密退化'] = dense_C1(S0, step=5.0)
        print(json.dumps(report['C1_稠密退化'], ensure_ascii=False))

        if a.search:
            print('\n=== 候选点集搜索 ===')
            report['搜索'] = search()
        if a.min_search:
            print('\n=== 最少点数搜索 ===')
            report['最少点数搜索'] = min_search()
        families = candidate_families()
        if a.family:
            families = {a.family: families[a.family]}
        print('\n=== 候选族认证 ===')
        res = {}
        for nm, d in families.items():
            res[nm] = verify_family(nm, d['rings'], do_certify=(not a.no_certify))
            res[nm]['说明'] = d['note']
        report['候选族'] = res

    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with open(a.out, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1, default=str)
        print('\n已写入 ' + a.out)


if __name__ == '__main__':
    main()
