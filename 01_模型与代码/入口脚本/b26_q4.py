# -*- coding: utf-8 -*-
"""Q4 控制器（Stage B · 冻结包之外的新文件）

【性质】问题 4（全向+定向混合）的机器狗主控。**不修改 04_CODE/b26/、不修改任何既有脚本。**
【依据】04_CODE/Q4_MVP设计.md §12（状态机）/ §13（定位）/ §14（清除）/ §15（兜底链）/ §16（终止）/ §17（调度）/ §18（β-free）
【前置】Stage A 已 PASS：
        - 精确判据 E(S)：max_gap(D(P)) <= 180（b26_q4_certificate.py，自证 S1—S6 全通过）
        - 证书 P_cert = S51_b（51 点）：5 m 网格最小裕量 24.50°，认证最小裕量 3.687°，未认证细胞 0
        - C-1 全圆退化、C-5 mock 语义回归 9/9 PASS

设计要点（与 Q3 的差异只有一处是"算法"级的）
------------------------------------------------
1. **判空依据换成 Q4 证书**：51 个证书点全部访问过之后，"从未 dc/near 过的频道必为空"
   —— 由 E(S) >= D 保证（无论定向源朝向如何，总有一个证书点能检出它）。
2. **β-free**：不估计、不反推定向方向。dc 给出的楔形约束与朝向无关（题面附录 1(4)）；
   清除与朝向无关（附录 2(8)）。
3. **ns 不收缩 F_c**：已检出频道的 F_c 保持凸（否则 §15 的铺网可证命中失效）。
4. **清除**：diam(F_c) <= 40 m 时先试质心；失败立即用 F_c 铺网（25 m 网格 + 投影，投影到凸集
   非扩张 => 源 20 m 内必有网点 => 可证命中）。
5. **终止**：|K|=16（鸽巢）/ 全部频道已清除或已判空 / 进度驱动停滞检测（连续 STALL_LIMIT 步
   状态签名不变即强制换点）。
6. **调度**：M(t) = 未访问证书点 ∪ 可清除频道 ∪ 需复测频道；动作 = 离当前位置最近者
   （与冻结代码 b26/path.py:nearest 同一准则，无多准则打分）。
"""

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from b26 import detect, locate
from b26 import path as bpath
from b26.comm import Comm
from b26.motion import Motion, V, T_MEASURE, T_SWITCH, T_OPTICAL, T_CLEAR
from b26_q4_certificate import R_DOMAIN, R_MIN, ring

# --------------------------------------------------------------------------
# 配置（证书点集：Stage A 认证通过的 S51_b）
# --------------------------------------------------------------------------

CERT_RINGS = [(0.0, 1, 0.0), (950.0, 10, 0.0), (1250.0, 10, 18.0),
              (1650.0, 10, 0.0), (2250.0, 10, 18.0), (2700.0, 10, 0.0)]
CERT_NAME = 'S51_b（51 点，认证裕量 3.687°）'
CERT = [p for (a, n, ph) in CERT_RINGS for p in ring(n, a, ph)]

CHANNELS = list(range(1, 21))
D_THRESHOLD = 40.0          # = 2 x 清除半径 20 m（工程口径；严格阈值 20*sqrt(3)≈34.6 m）
MAX_REFINE = 4
MAX_CLEAR_TRY = 3
SWEEP_STEP = 25.0           # h/sqrt(2) = 17.68 m < 20 m
SWEEP_MAX_PTS = 200
STALL_LIMIT = 40
HARD_CAP = 3000
PROBE_QUANT = 5.0
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       '05_EXPERIMENTS', 'logs')


# --------------------------------------------------------------------------
# 控制器
# --------------------------------------------------------------------------

class Robot4:
    def __init__(self, comm, cert=None, verbose=False):
        self.c = comm
        self.cert = list(cert if cert is not None else CERT)
        self.verbose = verbose
        self.m = Motion()
        # 可行域账本（凸多边形），初值 = 目标圆域的外切 72 边形
        self.F = {c: locate.disk_poly(0.0, 0.0, R_DOMAIN) for c in CHANNELS}
        self.probes = {c: [] for c in CHANNELS}
        self.seen_signal = set()      # 收到过 dc 或 near 的频道（非空证据）
        self.cleared = set()
        self.empty = set()
        self.first = {}
        self.refines = {}
        self.clear_fail_cnt = {}
        self.probe_seen = {}
        self.stuck = set()
        self.stall_trips = []
        self.hard_cap_hit = False
        self.pigeon_exit = False
        self.steps_used = 0
        self.covered_count = 0
        self.sig_repeat = {}
        self.max_sig_repeat = 0
        self.t = 0.0
        self.n_meas = 0
        self.n_clear = 0
        self.n_fail = 0
        self.n_near = 0
        self.n_sweep = 0
        self.n_sweep_clear = 0
        self.sweep_skipped = 0

    def log(self, *a):
        if self.verbose:
            print(*a)

    # ---------- 原语 ----------
    def measure(self, pos, ch):
        r = self.c.measure(pos, ch)
        self.t = r['virtual_time_s']
        self.n_meas += 1
        z, th = detect.parse(r)
        self.m.apply(pos, channel_after=ch)
        self.probes[ch].append(pos)
        if z == detect.DC:
            self.seen_signal.add(ch)
            w = locate.wedge_poly(pos, th, R_DOMAIN)
            newF = locate.intersect(self.F[ch], w)
            if newF:
                newF = locate.clip_disk(newF, pos[0], pos[1], 1500.0)
            if newF and len(newF) >= 3:
                self.F[ch] = newF
            # 浮点退化：保留上一轮 F_c（不据此判空）
            self.first.setdefault(ch, (pos, th))
        elif z == detect.NR:
            self.seen_signal.add(ch)
            self.n_near += 1
        return z, th

    def clear(self, pos, ch):
        r = self.c.clear(pos, ch)
        self.t = r['virtual_time_s']
        self.n_clear += 1
        ok = (r.get('clear_result') == 'success')
        self.m.apply(pos)
        if ok:
            self.cleared.add(ch)
            self.F[ch] = []
        else:
            self.n_fail += 1
        return ok

    def unresolved(self):
        return [c for c in CHANNELS if c not in self.cleared and c not in self.empty]

    def diam(self, ch):
        return locate.diameter(self.F[ch])

    def cen(self, ch):
        return locate.centroid(self.F[ch])

    # ---------- 定位/复测 ----------
    def _refine_once(self, ch):
        F = self.F[ch]
        if not F or len(F) < 3:
            return False
        q = locate.centroid(F)
        if q is None:
            return False
        z, _ = self.measure(q, ch)
        self.refines[ch] = self.refines.get(ch, 0) + 1
        if z == detect.NR:
            return self.clear(q, ch)
        return False

    # ---------- 兜底一：凸集内铺网清除（可证命中） ----------
    def _net_points(self, F, step=SWEEP_STEP, bucket=2.0):
        """在 F_c 的**主轴坐标系** (u,v) 内铺方网格并投影到 F_c。

        为什么用主轴坐标：轴对齐包围盒对"斜置的细长楔形"会膨胀成一个大方块
        （1500 m 长的 2 度楔形 -> 1100x1100 的包围盒 -> 上千个网点），而在主轴系内
        只需 length/step x width/step 个网点（约 120 个）。

        可证性：任意 q ∈ F_c 在 (u,v) 网格中存在网点 g 使 ||g-q|| <= step/sqrt(2)；
        投影到凸集非扩张 => ||proj_F(g) - q|| <= step/sqrt(2) = 17.68 m < 20 m（清除半径）。
        """
        vs = F
        m = len(vs)
        best = (-1.0, None, None)
        for i in range(m):
            for j in range(i + 1, m):
                d = math.dist(vs[i], vs[j])
                if d > best[0]:
                    best = (d, vs[i], vs[j])
        _, A, B = best
        ux, uy = B[0] - A[0], B[1] - A[1]
        L = math.hypot(ux, uy)
        if L < 1e-9:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = ux / L, uy / L
        vx, vy = -uy, ux
        us = [p[0] * ux + p[1] * uy for p in vs]
        vv = [p[0] * vx + p[1] * vy for p in vs]
        pts = []
        seen = set()
        u = min(us)
        while u <= max(us) + 1e-9:
            v = min(vv)
            while v <= max(vv) + 1e-9:
                q = locate.project(F, (u * ux + v * vx, u * uy + v * vy))
                k = (round(q[0] / bucket), round(q[1] / bucket))
                if k not in seen:
                    seen.add(k)
                    pts.append(q)
                v += step
            u += step
        return pts

    def _sweep_clear(self, ch):
        """凸集内铺网清除。**只有网点数 <= SWEEP_MAX_PTS 时才执行**，以保证
        "每个执行的铺网都是可证命中"（超出上限则跳过，改走复测/换点；记 sweep_skipped）。"""
        F = self.F[ch]
        if not F or len(F) < 3:
            return False
        pts = self._net_points(F)
        if len(pts) == 0:
            return False
        if len(pts) > SWEEP_MAX_PTS:
            self.sweep_skipped += 1
            return False
        pts.sort(key=lambda p: math.dist(p, self.m.pos))
        self.n_sweep += 1
        for q in pts:
            self.n_sweep_clear += 1
            if self.clear(q, ch):
                return True
        return False

    # ---------- 兜底二：换一个未用过的探测点（证据严格增长） ----------
    def _new_probe_point(self, ch):
        F = self.F[ch]
        if not F or len(F) < 3:
            return None
        hist = self.probe_seen.setdefault(ch, set())
        c = locate.centroid(F)
        cands = []
        if c:
            cands.append(c)
            cands.extend(sorted(F, key=lambda v: -math.dist(v, c)))
            cands.extend([((c[0] + v[0]) / 2.0, (c[1] + v[1]) / 2.0) for v in F])
        for q in cands:
            k = (round(q[0] / PROBE_QUANT), round(q[1] / PROBE_QUANT))
            if k not in hist:
                hist.add(k)
                return q
        return None

    # ---------- 主循环 ----------
    def run(self):
        e = self.c.enter()
        self.log('[enter] remaining=%s' % e.get('remaining_real_duration_s'))
        covered = set()
        steps = 0
        stall = 0
        last_prog = None
        while True:
            if len(self.cleared) >= 16:          # §16(a) 鸽巢：N <= 16，清满 16 即为全部清除
                self.pigeon_exit = True
                break
            steps += 1
            acts = []
            for i, q in enumerate(self.cert):
                if i not in covered:
                    acts.append(('cover', q, None, i))
            for ch in self.unresolved():
                if ch not in self.seen_signal:
                    continue
                F = self.F[ch]
                if not F or len(F) < 3:
                    continue
                p = locate.centroid(F)
                if p is None:
                    continue
                acts.append(('clear' if locate.diameter(F) <= D_THRESHOLD else 'refine', p, ch, None))
            if not acts:
                break
            kind, pos, ch, ci = bpath.nearest(self.m.pos, acts)
            sig = (kind, ch, (round(pos[0]), round(pos[1])))
            self.sig_repeat[sig] = self.sig_repeat.get(sig, 0) + 1
            if self.sig_repeat[sig] > self.max_sig_repeat:
                self.max_sig_repeat = self.sig_repeat[sig]

            if kind == 'cover':
                covered.add(ci)
                self.covered_count += 1
                for x in sorted(self.unresolved()):
                    F = self.F[x]
                    if x in self.seen_signal and F and len(F) >= 3 \
                            and locate.diameter(F) <= D_THRESHOLD:
                        continue                      # 已可清除，不再浪费一次检测
                    z, _ = self.measure(pos, x)
                    if z == detect.NR:                # <=5 m 且在扇区内 => 原地清除必成
                        self.clear(pos, x)
            elif kind == 'clear':
                if not self.clear(pos, ch):
                    self.clear_fail_cnt[ch] = self.clear_fail_cnt.get(ch, 0) + 1
                    # §14：质心失败 -> 立即在 F_c 内铺网（投影到凸集非扩张 => 可证命中）
                    # 失败后必须改变候选点，禁止原地重试
                    if not self._sweep_clear(ch):
                        self._refine_once(ch)
                        p2 = self.cen(ch)
                        if p2:
                            self.clear(p2, ch)
            else:                                     # refine
                if self.refines.get(ch, 0) < MAX_REFINE:
                    self._refine_once(ch)
                elif self.clear_fail_cnt.get(ch, 0) < MAX_CLEAR_TRY:
                    if not self.clear(pos, ch):
                        self.clear_fail_cnt[ch] = self.clear_fail_cnt.get(ch, 0) + 1
                else:
                    if not self._sweep_clear(ch):     # 可证命中
                        q = self._new_probe_point(ch)
                        if q is not None:
                            z, _ = self.measure(q, ch)
                            self.refines[ch] = self.refines.get(ch, 0) + 1
                            if z == detect.NR:
                                self.clear(q, ch)
                        else:
                            self.stuck.add(ch)

            # 证书点全部访问过 => 从未 dc/near 的频道判空（E(S) >= D）
            if len(covered) == len(self.cert):
                for c in self.unresolved():
                    if c not in self.seen_signal:
                        self.empty.add(c)

            # 进度驱动终止
            prog = (len(self.cleared), len(self.empty),
                    sum(len(v) for v in self.probes.values()))
            if prog == last_prog:
                stall += 1
            else:
                stall = 0
                last_prog = prog
            if stall >= STALL_LIMIT:
                self.stall_trips.append((steps, tuple(sorted(self.unresolved()))))
                moved = False
                for c in sorted([x for x in self.unresolved() if x in self.seen_signal]):
                    q = self._new_probe_point(c)
                    if q is not None:
                        z, _ = self.measure(q, c)
                        moved = True
                        if z == detect.NR:
                            self.clear(q, c)
                        break
                if not moved:
                    break
                stall = 0
            if steps >= HARD_CAP:
                self.hard_cap_hit = True
                break

        self.steps_used = steps
        for c in self.unresolved():
            if c not in self.seen_signal:
                self.empty.add(c)
        self.c.exit()
        # 防御性报告：已检出但最终仍未清除的频道（正常应为空；非空即为丢源）
        self.unresolved_seen = sorted([c for c in self.unresolved() if c in self.seen_signal])
        return dict(cleared=len(self.cleared), empty=len(self.empty),
                    unresolved_seen=self.unresolved_seen,
                    virtual_time=self.t, measured=self.n_meas, clears=self.n_clear,
                    clear_fail=self.n_fail, near=self.n_near, dist=self.m.dist,
                    refine_rounds=sum(self.refines.values()),
                    cover_points=self.covered_count, cert_points=len(self.cert),
                    steps_used=self.steps_used, stall_trips=len(self.stall_trips),
                    hard_cap_hit=self.hard_cap_hit, pigeon_exit=self.pigeon_exit,
                    stuck=sorted(self.stuck),
                    max_sig_repeat=self.max_sig_repeat, uniq_sig=len(self.sig_repeat),
                    sweeps=self.n_sweep, sweep_clears=self.n_sweep_clear,
                    sweep_skipped=self.sweep_skipped)


# --------------------------------------------------------------------------
# 证书自检（可选；粗网格快速核对，正式认证见 b26_q4_verify.py）
# --------------------------------------------------------------------------

def certificate_selfcheck(cert=None, rho_step=25.0, alpha_step_deg=3.0):
    S = cert if cert is not None else CERT
    try:
        import numpy as np
    except Exception:
        return dict(错误='numpy 不可用')
    rhos = np.arange(0.0, R_DOMAIN + 1e-9, rho_step)
    alphas = np.arange(0.0, 360.0, alpha_step_deg)
    ar = np.radians(alphas)
    ca, sa = np.cos(ar), np.sin(ar)
    Sx = np.asarray([p[0] for p in S])
    Sy = np.asarray([p[1] for p in S])
    worst = 1e9
    wp = None
    for rho in rhos:
        Px, Py = rho * ca, rho * sa
        dx = Sx[None, :] - Px[:, None]
        dy = Sy[None, :] - Py[:, None]
        d = np.hypot(dx, dy)
        ang = np.degrees(np.arctan2(dy, dx)) % 360.0
        keep = (d <= R_MIN) & (d > 1e-6)
        k = keep.sum(axis=1)
        a = np.sort(np.where(keep, ang, np.nan), axis=1)
        m = a.shape[1]
        diffs = np.nan_to_num(np.diff(a, axis=1), nan=0.0)
        idx = np.arange(m - 1)[None, :]
        ok = idx < (k - 1)[:, None]
        mg = np.where(ok, diffs, 0.0).max(axis=1)
        kk = np.maximum(k, 1)
        last = np.nan_to_num(a[np.arange(len(kk)), kk - 1], nan=0.0)
        wrap = np.where(k >= 2, a[:, 0] + 360.0 - last, 360.0)
        mg = np.where(k >= 2, np.maximum(mg, wrap), 360.0)
        marg = 180.0 - mg
        i = int(np.argmin(marg))
        if marg[i] < worst:
            worst = float(marg[i])
            wp = dict(rho=float(rho), alpha=float(alphas[i]))
    return dict(证书=CERT_NAME, 点数=len(S), 网格='%g m x %g deg' % (rho_step, alpha_step_deg),
                最小裕量_deg=round(worst, 4), 最坏点=wp,
                合格=bool(worst >= 10.0),
                说明='粗网格快速自检；严格认证见 b26_q4_verify.py（5 m + 自适应细分 + Lipschitz）')


# --------------------------------------------------------------------------
# 冒烟测试（非实验：只验证控制器可端到端运行）
# --------------------------------------------------------------------------

def smoke(seeds=(1, 2, 3), dir_frac=0.5, port=20501, verbose=True, detail=False):
    import threading
    import b26_mock4 as M4
    os.makedirs(LOG_DIR, exist_ok=True)
    log = os.path.join(LOG_DIR, '_work_b26_q4_smoke_log.jsonl')
    srv = M4.serve4(port, M4.new_arena4(seed=seeds[0], dir_frac=dir_frac))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    rows = []
    for sd in seeds:
        M4.STATE['arena'] = M4.new_arena4(seed=sd, dir_frac=dir_frac)
        M4.STATE['idem'] = {}
        c = Comm('http://127.0.0.1:%d' % port, '202612345678', log)
        t0 = time.time()
        err = None
        try:
            r = Robot4(c, verbose=False).run()
        except Exception as e:
            err = str(e)[:200]
            r = dict(cleared=0, empty=0, virtual_time=0.0, measured=0, clears=0, clear_fail=0,
                     near=0, dist=0.0, refine_rounds=0, cover_points=0, steps_used=0,
                     stall_trips=0, hard_cap_hit=False, stuck=[], max_sig_repeat=0,
                     uniq_sig=0, sweeps=0, sweep_clears=0, cert_points=len(CERT))
        finally:
            c.close()
        N = M4.STATE['arena']['N']
        r['seed'] = sd
        r['N'] = N
        r['真值核对'] = ('清除数=源数' if r['cleared'] == N else '清除数!=源数(丢源)') + \
                        ('/判空=20-N' if r['empty'] == 20 - N else '/判空!=20-N(误判空)')
        r['日志KB'] = round(os.path.getsize(log) / 1024.0, 1) if os.path.exists(log) else 0.0
        r['req'] = c.n_req
        r['wall_s'] = round(time.time() - t0, 3)
        r['avg'] = round(r['virtual_time'] / max(1, r['cleared']), 1)
        r['err'] = err
        rows.append(r)
        if verbose:
            print('  冒烟 seed=%d N=%2d 清除=%2d 判空=%2d 虚拟=%8.1f s 平均=%7.1f s 检测=%3d 请求=%3d '
                  '停滞=%d 卡死=%d 铺网=%d 鸽巢=%s 日志=%.1fKB 墙钟=%.2fs  [%s] %s'
                  % (sd, N, r['cleared'], r['empty'], r['virtual_time'], r['avg'],
                     r['measured'], r['req'], r['stall_trips'], len(r['stuck']),
                     r.get('sweeps', 0), r.get('pigeon_exit'), r.get('日志KB', 0.0), r['wall_s'],
                     r['真值核对'], r['err'] or ''))
        if detail:
            print('    ' + json.dumps({k: v for k, v in r.items() if k != 'err'},
                                      ensure_ascii=False))
    srv.shutdown()
    return rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--selfcheck', action='store_true')
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--dir-frac', type=float, default=0.5)
    ap.add_argument('--detail', action='store_true')
    a = ap.parse_args()
    print('=== Q4 证书自检 ===')
    print(json.dumps(certificate_selfcheck(), ensure_ascii=False))
    if a.selfcheck:
        sys.exit(0)
    if a.smoke:
        seeds = tuple(int(x) for x in a.seeds.split(',') if x.strip())
        print('\n=== 冒烟测试（非实验，仅验证可运行）dir_frac=%.2f ===' % a.dir_frac)
        rows = smoke(seeds=seeds, dir_frac=a.dir_frac, detail=a.detail)
        ok = all((r['err'] is None) and r['cleared'] + r['empty'] == 20 for r in rows)
        print('\n冒烟结论：%s' % ('PASS（每局均无异常且 已清除+已判空 = 20）' if ok else 'FAIL'))
