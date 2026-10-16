# -*- coding: utf-8 -*-
"""E-Q4 实验层运行器（Stage B · 冻结包之外的新文件）

【性质】只读取控制器与 mock，**不修改任何既有文件**（不碰 04_CODE/b26/、不碰 b26_q4.py）。
【依据】04_CODE/Q4_MVP设计.md §21（E-Q4 实验矩阵）、§22（统计口径）、02_KNOWLEDGE_BASE/H_实验方法.md
【数据口径】**全部为自建 mock4 的离线结果**，不是官方模拟器结果。

块结构
------
B1  E-Q4-10 主统计      ：G4 主臂（51 点 Q4 证书）mixed 0.5，seed 1..100
B2  E-Q4-5  场景分层    ：dir_frac = 0 / .25 / .5 / .75 / 1.0，各 30 局
B3  E-Q4-11 证书强度消融：Q3 证书（COVER_9，9 点）vs G4，同种子配对
B4  E-Q4-12 兜底链消融  ：NoSweep / NoNewProbe vs G4，同种子配对
B5  C-3     全向退化回归：dir_frac = 0，seed 1..36（清除比例、终止性指标）
B6  E-Q4-7  边界源      ：源全部位于 rho = 1800（定理 3 的临界情形），seed 1..30

正确性口径（每局都做真值核对）
    漏源数   = 结束时仍留在 mock 里的源（清除失败的源）
    误判空数 = 被控制器判空、但真值里确实有源的频道
两者都应为 0；它们比"平均时间"重要得多。
"""

import argparse
import json
import math
import os
import statistics as st
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import b26_mock4 as M4
from b26.comm import Comm
from b26_q4 import Robot4, CERT, CERT_NAME, LOG_DIR
from b26_q4_certificate import ring

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '05_EXPERIMENTS', 'results', '_work_b26_q4_exp.json')
LOG = os.path.join(LOG_DIR, '_work_b26_q4_exp_log.jsonl')
PORT = 20601

# Q3 证书（消融用）：圆心 + 8 点均匀分布于半径 1200 m
COVER9 = [(0.0, 0.0)] + ring(8, 1200.0)

# 双侧 t 分位（95%）
T975 = {29: 2.045, 35: 2.030, 49: 2.009, 59: 2.000, 79: 1.990, 99: 1.984}


# ---------------------------------------------------------------- 消融臂 ----
class Robot4NoSweep(Robot4):
    """关掉兜底③（凸集铺网清除）。"""
    def _sweep_clear(self, ch):
        return False


class Robot4NoNewProbe(Robot4):
    """关掉兜底④（换一个未用过的探测点）。"""
    def _new_probe_point(self, ch):
        return None


# ---------------------------------------------------------------- 单局 ------
def once(seed, dir_frac=0.5, cert=None, cls=Robot4, radial_bias=None):
    M4.STATE['arena'] = M4.new_arena4(seed=seed, dir_frac=dir_frac, radial_bias=radial_bias)
    M4.STATE['idem'] = {}
    arena = M4.STATE['arena']
    truth = set(arena['srcs'].keys())
    N = arena['N']
    c = Comm('http://127.0.0.1:%d' % PORT, '202612345678', LOG)
    rb = cls(c, cert=cert)
    t0 = time.time()
    err = None
    try:
        r = rb.run()
    except Exception as e:
        err = str(e)[:160]
        r = dict(cleared=0, empty=0, virtual_time=0.0, measured=0, clears=0, clear_fail=0,
                 near=0, dist=0.0, refine_rounds=0, cover_points=0, cert_points=0,
                 steps_used=0, stall_trips=0, hard_cap_hit=False, pigeon_exit=False,
                 stuck=[], max_sig_repeat=0, uniq_sig=0, sweeps=0, sweep_clears=0,
                 sweep_skipped=0, unresolved_seen=[])
    finally:
        c.close()
    alive = sorted(arena['srcs'].keys())
    r.update(seed=seed, N=N, dir_frac=dir_frac, err=err,
             漏源=alive, 漏源数=len(alive), 误判空=sorted(set(rb.empty) & truth),
             误判空数=len(set(rb.empty) & truth),
             未解决且已检出=sorted(set(getattr(rb, 'unresolved_seen', []))),
             清除比例=round(r['cleared'] / N, 6) if N else 0.0,
             avg=round(r['virtual_time'] / max(1, r['cleared']), 3),
             req=c.n_req, wall_s=round(time.time() - t0, 3),
             log_kb=round(os.path.getsize(LOG) / 1024.0, 1) if os.path.exists(LOG) else 0.0)
    return r


# ---------------------------------------------------------------- 统计 ------
def _pct(xs, p):
    a = sorted(xs)
    k = min(len(a) - 1, max(0, int(round(p / 100.0 * (len(a) - 1)))))
    return a[k]


def agg(rs, key='avg'):
    xs = [x[key] for x in rs if x.get('err') is None]
    n = len(xs)
    if n == 0:
        return dict(局数=0)
    m = st.mean(xs)
    sp = st.pstdev(xs)
    sd = st.stdev(xs) if n > 1 else 0.0
    t = T975.get(n - 1, 1.984)
    hw = t * sd / math.sqrt(n) if n > 1 else 0.0
    Ns = sum(x['N'] for x in rs)
    cl = sum(x['cleared'] for x in rs)
    byN = {}
    for x in rs:
        byN.setdefault(x['N'], []).append(x['avg'])
    return dict(局数=n, 异常局数=sum(1 for x in rs if x.get('err')),
                源数合计=Ns, 清除合计=cl,
                清除比例=round(cl / Ns, 6) if Ns else 0.0,
                全清局数='%d/%d' % (sum(1 for x in rs if x['cleared'] == x['N']), len(rs)),
                漏源合计=sum(len(x['漏源']) for x in rs),
                误判空合计=sum(len(x['误判空']) for x in rs),
                未解决已检出合计=sum(len(x.get('未解决且已检出', [])) for x in rs),
                平均s=round(m, 2), 中位数s=round(st.median(xs), 2),
                总体标准差s=round(sp, 2), 标准误s=round(sp / math.sqrt(n), 2),
                CI95=[round(m - hw, 2), round(m + hw, 2)],
                最小s=round(min(xs), 2), 最大s=round(max(xs), 2),
                P90s=round(_pct(xs, 90), 2), P95s=round(_pct(xs, 95), 2),
                总虚拟时间均值s=round(st.mean([x['virtual_time'] for x in rs]), 1),
                检测次数=round(st.mean([x['measured'] for x in rs]), 1),
                请求数=round(st.mean([x['req'] for x in rs]), 1),
                请求数最大=int(max(x['req'] for x in rs)),
                移动距离均值m=round(st.mean([x['dist'] for x in rs]), 1),
                复测轮数=round(st.mean([x['refine_rounds'] for x in rs]), 1),
                清除尝试=round(st.mean([x['clears'] for x in rs]), 1),
                清除失败=round(st.mean([x['clear_fail'] for x in rs]), 1),
                铺网次数=round(st.mean([x['sweeps'] for x in rs]), 2),
                铺网跳过=round(st.mean([x.get('sweep_skipped', 0) for x in rs]), 2),
                近距near=round(st.mean([x['near'] for x in rs]), 2),
                停滞触发局数=sum(1 for x in rs if x['stall_trips'] > 0),
                硬上限触发局数=sum(1 for x in rs if x['hard_cap_hit']),
                卡死频道局数=sum(1 for x in rs if x['stuck']),
                鸽巢提前终止局数=sum(1 for x in rs if x.get('pigeon_exit')),
                最大重复动作=int(max(x['max_sig_repeat'] for x in rs)),
                日志均值KB=round(st.mean([x['log_kb'] for x in rs]), 1),
                日志最大KB=round(max(x['log_kb'] for x in rs), 1),
                墙钟均值s=round(st.mean([x['wall_s'] for x in rs]), 3),
                墙钟最大s=round(max(x['wall_s'] for x in rs), 3),
                按源数分层={k: round(st.mean(v), 1) for k, v in sorted(byN.items())})


def paired(A, B, key='avg'):
    """A - B 的同种子配对（只比较两臂都有效的局）。"""
    ka = {x['seed']: x for x in A}
    kb = {x['seed']: x for x in B}
    seeds = sorted(set(ka) & set(kb))
    d = [ka[s][key] - kb[s][key] for s in seeds]
    n = len(d)
    if n < 2:
        return dict(n=n)
    m = st.mean(d)
    sd = st.stdev(d)
    t = T975.get(n - 1, 1.984)
    hw = t * sd / math.sqrt(n)
    win = sum(1 for v in d if v < 0)
    lose = sum(1 for v in d if v > 0)
    return dict(n=n, 均值差=round(m, 2), CI95=[round(m - hw, 2), round(m + hw, 2)],
                Cohen_d=round(m / sd, 3) if sd > 0 else None,
                A胜局=win, B胜局=lose, 打平=n - win - lose, A胜率=round(100.0 * win / n, 1))


# ---------------------------------------------------------------- 主流程 ----
def run_block(name, seeds, cert=None, cls=Robot4, dir_frac=0.5, radial_bias=None, verbose=True):
    rows = []
    for s in seeds:
        rows.append(once(s, dir_frac=dir_frac, cert=cert, cls=cls, radial_bias=radial_bias))
    a = agg(rows)
    if verbose:
        print('[%s] 局数=%d 清除比例=%.4f 全清=%s 漏源=%d 误判空=%d 平均=%.1fs 最大=%.1fs '
              '停滞=%d 硬上限=%d 卡死=%d 最大重复=%d 墙钟max=%.2fs'
              % (name, a['局数'], a['清除比例'], a['全清局数'], a['漏源合计'], a['误判空合计'],
                 a['平均s'], a['最大s'], a['停滞触发局数'], a['硬上限触发局数'],
                 a['卡死频道局数'], a['最大重复动作'], a['墙钟最大s']))
    return a, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--blocks', default='B1,B2,B3,B4,B5,B6')
    a = ap.parse_args()
    n_main = 12 if a.quick else 100
    n_strat = 6 if a.quick else 30
    n_omni = 6 if a.quick else 36
    n_edge = 6 if a.quick else 30
    blocks = set(a.blocks.split(','))
    os.makedirs(LOG_DIR, exist_ok=True)

    srv = M4.serve4(PORT, M4.new_arena4(seed=1, dir_frac=0.5))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)

    rep = dict(生成时间=time.strftime('%Y-%m-%d %H:%M:%S'),
               口径='自建 mock4 离线结果（**不是官方模拟器**）；控制器 b26_q4.py，证书 ' + CERT_NAME,
               主证书=dict(点数=len(CERT), 名称=CERT_NAME),
               消融证书=dict(点数=len(COVER9), 名称='Q3 证书 COVER_9'),
               规模=dict(B1=n_main, B2=n_strat, B3=n_main, B4=n_main, B5=n_omni, B6=n_edge))
    t_all = time.time()
    R = {}

    if 'B1' in blocks:
        print('=== B1 E-Q4-10 主统计（G4 主臂，mixed 0.5，seed 1..%d）===' % n_main)
        a1, r1 = run_block('B1 G4-mixed', list(range(1, n_main + 1)))
        rep['B1_主统计'] = a1
        R['G4'] = r1

    if 'B2' in blocks:
        print('\n=== B2 E-Q4-5 场景分层（dir_frac 扫描，seed 1..%d）===' % n_strat)
        strat = {}
        for df in (0.0, 0.25, 0.5, 0.75, 1.0):
            aa, _ = run_block('B2 dir=%.2f' % df, list(range(1, n_strat + 1)), dir_frac=df)
            strat['dir_frac=%.2f' % df] = aa
        rep['B2_场景分层'] = strat

    if 'B3' in blocks:
        print('\n=== B3 E-Q4-11 证书强度消融（Q3 证书 9 点 vs Q4 证书 51 点）===')
        a3, r3 = run_block('B3 Q3CERT', list(range(1, n_main + 1)), cert=COVER9)
        rep['B3_证书消融_Q3证书'] = a3
        if 'G4' in R:
            rep['B3_配对_vs_主臂'] = dict(
                平均时间=paired(R['G4'], r3, 'avg'),
                清除数=paired(R['G4'], r3, 'cleared'),
                漏源数=paired(R['G4'], r3, '漏源数'))

    if 'B4' in blocks:
        print('\n=== B4 E-Q4-12 兜底链消融（关铺网 / 关换点）===')
        a4, r4 = run_block('B4 NoSweep', list(range(1, n_main + 1)), cls=Robot4NoSweep)
        a5, r5 = run_block('B4 NoNewProbe', list(range(1, n_main + 1)), cls=Robot4NoNewProbe)
        rep['B4_兜底消融_关铺网'] = a4
        rep['B4_兜底消融_关换点'] = a5
        if 'G4' in R:
            rep['B4_配对_关铺网'] = dict(平均时间=paired(R['G4'], r4, 'avg'),
                                        清除数=paired(R['G4'], r4, 'cleared'))
            rep['B4_配对_关换点'] = dict(平均时间=paired(R['G4'], r5, 'avg'),
                                        清除数=paired(R['G4'], r5, 'cleared'))

    if 'B5' in blocks:
        print('\n=== B5 C-3 全向退化回归（dir_frac = 0，seed 1..%d）===' % n_omni)
        a6, _ = run_block('B5 全向', list(range(1, n_omni + 1)), dir_frac=0.0)
        rep['B5_C3全向退化'] = a6

    if 'B6' in blocks:
        print('\n=== B6 E-Q4-7 边界源（全部源位于 rho = 1800，seed 1..%d）===' % n_edge)
        a7, _ = run_block('B6 边界源', list(range(1, n_edge + 1)), radial_bias=1800.0)
        rep['B6_边界源'] = a7

    srv.shutdown()
    rep['总耗时_s'] = round(time.time() - t_all, 1)
    rep['逐局明细'] = {k: v for k, v in R.items()}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
    print('\n已写入 ' + a.out + '（总耗时 %.1f s）' % rep['总耗时_s'])


if __name__ == '__main__':
    main()
