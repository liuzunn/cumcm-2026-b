# -*- coding: utf-8 -*-
"""主控：搜索 → 发现信号 → 定位 → 移动 → 清除。
新增：① 用 select2 的理论选点策略做第二测点；② 覆盖方案可选 7 点/9 点固定 或 自适应缺口驱动。"""
import math
from . import locate, detect, search, path, select2
from .comm import Comm
from .motion import Motion, V, T_MEASURE, T_SWITCH, T_OPTICAL, T_CLEAR

CHANNELS = list(range(1, 21))
D_THRESHOLD = 40.0
MAX_REFINE = 4
# —— 本轮最小修复引入的边界常量（只用于"保证终止"，不改变 G 的核心算法）——
MAX_CLEAR_TRY = 3      # 同一目标连续清除尝试上限，超过即转入兜底
SWEEP_DIAM = 120.0     # 可行域直径 ≤ 该值时才允许"铺网扫描清除"
SWEEP_STEP = 25.0      # 网格间距；投影到凸集非扩张 ⇒ 真实源 20 m 内必有网点
SWEEP_MAX = 25         # 单次兜底扫描的最大清除次数
STALL_LIMIT = 40       # 连续多少步"状态无变化"即判定停滞
HARD_CAP = 3000        # 最后防线（正常情况永远不该触发）

class Robot:
    def __init__(self, comm, cover=None, strategy="perp547", cover_mode="fixed", verbose=False):
        self.c = comm
        self.cover = list(cover or search.COVER_7)
        self.strategy = strategy
        self.cover_mode = cover_mode
        self.m = Motion(); self.L = locate.Ledger(CHANNELS)
        self.cleared, self.empty = set(), set()
        self.first = {}                 # channel -> (首个测点, 第一个示向度)
        self.refines = {}               # channel -> 已复测轮数
        self.verbose = verbose
        self.t = 0.0; self.n_meas = 0; self.n_clear = 0; self.n_fail = 0; self.n_near = 0
        self.covered_points = 0
        self.sel_travel = 0.0           # 选点策略额外移动距离
        # —— 本轮最小修复新增的可观测状态 ——
        self.clear_fail_cnt = {}        # 每频道的连续清除失败次数
        self.probe_seen = {}            # 每频道已用过的探测点（量化），保证兜底不重复
        self.stuck = set()              # 兜底也推不动的频道（正常应为空）
        self.stall_trips = []           # 停滞检测触发记录（门禁 2 的证据）
        self.hard_cap_hit = False
        self.steps_used = 0
        self.covered_count = 0
        self.sig_repeat = {}            # 动作签名 → 出现次数（门禁 2）
        self.max_sig_repeat = 0

    def log(self, *a):
        if self.verbose: print(*a)

    # ---------- 原语 ----------
    def measure(self, pos, ch):
        r = self.c.measure(pos, ch); self.t = r["virtual_time_s"]; self.n_meas += 1
        z, th = detect.parse(r)
        self.m.apply(pos, channel_after=ch)
        if z == detect.DC:
            self.L.on_direction(ch, pos, th)
            self.first.setdefault(ch, (pos, th))
        elif z == detect.NS:
            self.L.on_no_signal(ch, pos)
        return z, th

    def clear(self, pos, ch):
        r = self.c.clear(pos, ch); self.t = r["virtual_time_s"]; self.n_clear += 1
        ok = (r.get("clear_result") == "success")
        self.m.apply(pos)
        if ok: self.cleared.add(ch); self.L.on_cleared(ch)
        else:  self.n_fail += 1
        return ok

    def unresolved(self):
        return [c for c in CHANNELS if c not in self.cleared and c not in self.empty]

    def _second_point(self, ch, F):
        """按选定策略给出第二测点；返回 None 表示退回"移到区域中心" """
        if self.strategy is None: return None
        s1, th1 = self.first.get(ch, (None, None))
        if s1 is None: return None
        try:
            return select2.pick(self.strategy, s1, th1, F)
        except Exception:
            return None

    def _refine_once(self, ch, use_selector=True):
        """对频道 ch 做一轮"选点 → 复测"。返回 True 表示已清除。"""
        F = self.L.region(ch)
        if self.L.is_degenerate(ch) or not F: return False
        cen = self.L.point(ch)
        q = cen
        if use_selector:
            s2 = self._second_point(ch, F)
            if s2 is not None and abs(s2[0]) <= 2e6 and abs(s2[1]) <= 2e6:
                self.sel_travel += math.dist(self.m.pos, s2) - math.dist(self.m.pos, cen)
                q = s2
        z, _ = self.measure(q, ch)
        self.refines[ch] = self.refines.get(ch, 0) + 1
        if z == detect.NR:
            self.n_near += 1
            return self.clear(q, ch)
        if z == detect.NS and q != cen:
            z2, _ = self.measure(cen, ch)          # 回退：策略点测不到就回到区域中心
            self.refines[ch] += 1
            if z2 == detect.NR: return self.clear(cen, ch)
        return False

    # ---------- 固定覆盖：先扫完再清 ----------
    def _run_fixed(self):
        for i, q in enumerate(path.order_nearest(self.m.pos, self.cover)):
            self.covered_points += 1
            live = self.unresolved()
            for ch in sorted(live):
                z, _ = self.measure(q, ch)
                if z == detect.NR:
                    self.n_near += 1
                    self.clear(q, ch)
        for ch in self.unresolved():
            if ch not in self.L.seen_dc: self.empty.add(ch)
        for ch in [c for c in self.unresolved() if c in self.L.seen_dc]:
            for it in range(MAX_REFINE):
                if ch in self.cleared: break
                D = self.L.diam(ch); cen = self.L.point(ch)
                if cen is None: self.empty.add(ch); break
                if D <= D_THRESHOLD or it == MAX_REFINE-1:
                    if not self.clear(cen, ch):
                        self._refine_once(ch, use_selector=False)
                        cen2 = self.L.point(ch)
                        if cen2: self.clear(cen2, ch)
                    break
                if self._refine_once(ch, use_selector=(it == 0)): break

# ---------- 自适应缺口驱动：覆盖点与清除动作统一按最近调度 ----------
    def _new_probe_point(self, ch):
        """在可行域内取一个"没测过"的探测点 —— 保证证据集严格增长（从而状态必然改变）。
        对全向源：只要探测点落在可行域内且可行域直径 ≤ 1000 m，就不可能返回 no_signal，
        因此必然得到 direction 或 near，即状态一定推进。"""
        F = self.L.region(ch)
        if not F or len(F) < 3: return None
        hist = self.probe_seen.setdefault(ch, set())
        c = locate.centroid(F)
        cands = []
        if c: cands.append(c)
        if c: cands.extend(sorted(F, key=lambda v: -math.dist(v, c)))
        if c: cands.extend([((c[0]+v[0])/2.0, (c[1]+v[1])/2.0) for v in F])
        for q in cands:
            k = (round(q[0]/5.0), round(q[1]/5.0))
            if k not in hist:
                hist.add(k); return q
        return None

    def _sweep_clear(self, ch):
        """兜底：可行域足够小时，在其内部铺一张 ≤25 m 间距的网并逐点清除。
        投影到凸集是非扩张的 ⇒ 真实源 20 m 内必有网中一点 ⇒ 必定命中。"""
        F = self.L.region(ch)
        if not F or len(F) < 3: return False
        D = locate.diameter(F)
        if D > SWEEP_DIAM: return False
        xs = [v[0] for v in F]; ys = [v[1] for v in F]
        pts = []; seen = set()
        x = min(xs)
        while x <= max(xs) + 1e-9:
            y = min(ys)
            while y <= max(ys) + 1e-9:
                q = locate.project(F, (x, y))
                k = (round(q[0]/2.0), round(q[1]/2.0))
                if k not in seen:
                    seen.add(k); pts.append(q)
                y += SWEEP_STEP
            x += SWEEP_STEP
        pts.sort(key=lambda p: math.dist(p, self.m.pos))
        for q in pts[:SWEEP_MAX]:
            if self.clear(q, ch): return True
        return False

    def _run_adaptive(self):
        covered = set(); steps = 0; stall = 0
        last_prog = None
        if self.verbose:
            print("  [adaptive] 进度驱动主循环启动")
        while True:
            steps += 1
            acts = []
            for i, q in enumerate(self.cover):
                if i not in covered: acts.append(("cover", q, None))
            for ch in self.unresolved():
                if ch not in self.L.seen_dc: continue
                if self.L.is_degenerate(ch): continue
                p = self.L.point(ch)
                if p is None: continue
                acts.append(("clear" if self.L.diam(ch) <= D_THRESHOLD else "refine", p, ch))
            if not acts:
                if len(covered) == len(self.cover): break
                continue
            kind, pos, ch = path.nearest(self.m.pos, acts)
            # —— 门禁 2 的运行时证据：同一 (动作, 频道, 量化位置) 的重复次数 ——
            sig = (kind, ch, (round(pos[0]), round(pos[1])))
            self.sig_repeat[sig] = self.sig_repeat.get(sig, 0) + 1
            if self.sig_repeat[sig] > self.max_sig_repeat:
                self.max_sig_repeat = self.sig_repeat[sig]
            if kind == "cover":
                i = self.cover.index(pos); covered.add(i); self.covered_points += 1
                for x in sorted(self.unresolved()):
                    z, _ = self.measure(pos, x)
                    if z == detect.NR:
                        self.n_near += 1; self.clear(pos, x)
            elif kind == "clear":
                if not self.clear(pos, ch):
                    self.clear_fail_cnt[ch] = self.clear_fail_cnt.get(ch, 0) + 1
                    self._refine_once(ch, use_selector=False)
                    p2 = self.L.point(ch)
                    if p2: self.clear(p2, ch)
            else:
                # ① 先复测（有上限）
                if self.refines.get(ch, 0) < MAX_REFINE:
                    self._refine_once(ch, use_selector=(self.refines.get(ch, 0) == 0))
                else:
                    # ② 复测到上限：允许有限次清除尝试，失败后必须改变候选点（禁止原地重试）
                    if self.clear_fail_cnt.get(ch, 0) < MAX_CLEAR_TRY:
                        if not self.clear(pos, ch):
                            self.clear_fail_cnt[ch] = self.clear_fail_cnt.get(ch, 0) + 1
                    else:
                        # ③ 兜底一：可行域够小 ⇒ 铺网扫描清除（可证明必中）
                        if not self._sweep_clear(ch):
                            # ④ 兜底二：在可行域内换一个没测过的点复测（证据必然增长）
                            q = self._new_probe_point(ch)
                            if q is not None:
                                z, _ = self.measure(q, ch)
                                self.refines[ch] = self.refines.get(ch, 0) + 1
                                if z == detect.NR: self.clear(q, ch)
                            else:
                                self.stuck.add(ch)
            if len(covered) == len(self.cover):
                for c in self.unresolved():
                    if c not in self.L.seen_dc or self.L.is_degenerate(c): self.empty.add(c)
            # ---------- 进度驱动终止：只看"是否真的取得了进展" ----------
            prog = (len(self.cleared), len(self.empty),
                    sum(len(v) for v in self.L.probes.values()))
            if prog == last_prog:
                stall += 1
            else:
                stall = 0; last_prog = prog
            if stall >= STALL_LIMIT:
                self.stall_trips.append((steps, tuple(sorted(self.unresolved()))))
                moved = False
                for c in sorted([x for x in self.unresolved() if x in self.L.seen_dc]):
                    q = self._new_probe_point(c)
                    if q is not None:
                        z, _ = self.measure(q, c); moved = True
                        if z == detect.NR: self.clear(q, c)
                        break
                if not moved: break
                stall = 0
            if steps >= HARD_CAP:
                self.hard_cap_hit = True; break
        self.steps_used = steps; self.covered_count = len(covered)
    def run(self):
        e = self.c.enter()
        self.log("[enter] remaining=%s" % e.get("remaining_real_duration_s"))
        if self.cover_mode == "adaptive": self._run_adaptive()
        else: self._run_fixed()
        # 收尾：仍未解决且从未测到方向的频道判空（由覆盖证书保证）
        for c in self.unresolved():
            if c not in self.L.seen_dc: self.empty.add(c)
        self.c.exit()
        return dict(cleared=len(self.cleared), empty=len(self.empty),
                    virtual_time=self.t, measured=self.n_meas, clears=self.n_clear,
                    clear_fail=self.n_fail, near=self.n_near, dist=self.m.dist,
                    refine_rounds=sum(self.refines.values()),
                    sel_travel=self.sel_travel, cover_points=self.covered_points,
                    steps_used=self.steps_used, covered_count=self.covered_count,
                    stall_trips=len(self.stall_trips), hard_cap_hit=self.hard_cap_hit,
                    stuck=sorted(self.stuck), max_sig_repeat=self.max_sig_repeat,
                    uniq_sig=len(self.sig_repeat))
