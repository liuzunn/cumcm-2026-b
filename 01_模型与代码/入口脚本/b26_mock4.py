# -*- coding: utf-8 -*-
"""Q4 mock 模拟器（Stage B · 语义工具层，冻结包之外的新文件）

【性质】自建 mock 的**定向源语义**复现件。不是官方模拟器；不修改 04_CODE/b26/ 与任何既有脚本。
【依据】04_CODE/Q4_MVP设计.md §4.2（检测算子）/ §19（mock 架构）/ §20（C-1、C-5）
【只读导入】b26_mock_server（冻结包内的 Q3 mock）：常量（R/V/各耗时常数/NEAR/CLR）、
            误差函数 _err（保证与 Q3 mock 逐位一致，C-5a 必需）。

语义（逐条对应题面）
--------------------
/measure(pos, ch)：
    d = ||pos - g_ch||
    1) 该频道无未清除源                       -> no_signal
    2) d > r                                  -> no_signal
    3) 定向源且 pos 不在扇区 [beta-90, beta+90] -> no_signal   （含 d<=5 的情形，附件2 §2.4）
    4) d <= 5 （且在扇区内）                    -> near（不返回 svd_deg）
    5) 否则                                    -> direction + svd_deg
/clear(pos, ch)：
    成功 <=> d <= 20；**与类型、朝向无关**（附录 2(8)）；不切换测向机频道；不推进切换耗时。
计时：与 Q3 mock 完全一致（/measure = Δd/5 + 切换 + 5；/clear = Δd/5 + 3 或 5；/enter、/exit 不推进）。

已知语义边界（写入官方核对清单）
--------------------------------
距离恰为 0（探测点与源重合）时，角度无定义。本 mock 默认按字面实现为 near（atan2(0,0)=0 落在扇区内），
而 Q4 证书的保守规则 A13 规定"重合探测点不计入保证"。两者只在"探针坐标与源坐标完全相等"时出现，
概率意义上可忽略，但必须在官方演练现场核实（见 regress() 的 C5c/C5e 输出）。
"""

import argparse
import copy
import json
import math
import os
import random
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M3          # 只读导入（冻结包内文件，未修改）

R = M3.R
V = M3.V
T_MEASURE = M3.T_MEASURE
T_SWITCH = M3.T_SWITCH
T_OPTICAL = M3.T_OPTICAL
T_CLEAR = M3.T_CLEAR
NEAR = M3.NEAR
CLR = M3.CLR
CHANNELS = M3.CHANNELS
ROCKET_ERR = M3._err                   # 同址固定误差（5 m 量化），与 Q3 mock 逐位一致

SECTOR_HALF_DEG = 90.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, '05_EXPERIMENTS', 'results', '_work_b26_q4_mock4_regress.json')


# --------------------------------------------------------------------------
# 1. 几何与检测语义（纯函数，便于单元回归）
# --------------------------------------------------------------------------

def in_sector(g, s, beta_deg, sector_half_deg=SECTOR_HALF_DEG):
    """探测点 s 是否位于"以 g 为心、朝向 beta、半角 sector_half"的扇区内（闭）。"""
    dx, dy = s[0] - g[0], s[1] - g[1]
    ang = math.degrees(math.atan2(dy, dx))
    delta = (ang - beta_deg + 180.0) % 360.0 - 180.0
    return abs(delta) <= sector_half_deg + 1e-9


def new_arena4(seed=None, n=None, dir_frac=0.5, sector_half=SECTOR_HALF_DEG,
               coincident_rule='literal', radial_bias=None):
    """生成 Q4 案例。

    dir_frac      定向源比例（None 时随机）
    sector_half   扇区半角（180 = 全圆极限，C-1 用）
    radial_bias   若给定，源半径固定为该值（用于构造边界源等定向案例）
    """
    rng = random.Random(seed)
    N = n if n is not None else rng.randint(10, 16)
    srcs = {}
    for c in rng.sample(CHANNELS, N):
        if radial_bias is None:
            while True:
                x, y = rng.uniform(-R, R), rng.uniform(-R, R)
                if x * x + y * y <= R * R:
                    break
        else:
            a = rng.uniform(0, 2 * math.pi)
            x, y = radial_bias * math.cos(a), radial_bias * math.sin(a)
        typ = 'dir' if rng.random() < (0.5 if dir_frac is None else dir_frac) else 'omni'
        srcs[c] = dict(x=x, y=y, r=rng.uniform(1000.0, 1500.0), type=typ,
                       beta=rng.uniform(0.0, 360.0) if typ == 'dir' else None)
    return dict(srcs=srcs, N=N, t=0.0, pos=(0.0, 0.0), ch=1, entered=False, t0=time.time(),
                sector_half=sector_half, coincident_rule=coincident_rule)


def detect4(arena, pos, ch):
    """返回 (measure_result, svd_deg or None)。纯语义函数，不改状态。"""
    s = arena['srcs'].get(ch)
    if s is None:
        return 'no_signal', None
    d = math.dist(pos, (s['x'], s['y']))
    if d > s['r']:
        return 'no_signal', None
    dir_like = (s['type'] == 'dir') and (arena['sector_half'] < 180.0)
    if dir_like and not in_sector((s['x'], s['y']), pos, s['beta'], arena['sector_half']):
        return 'no_signal', None
    if d <= NEAR and (d > 1e-12 or arena.get('coincident_rule', 'literal') == 'literal'):
        return 'near', None
    if d <= 1e-12 and arena.get('coincident_rule', 'literal') == 'strict':
        return 'no_signal', None
    a = math.degrees(math.atan2(s['y'] - pos[1], s['x'] - pos[0])) % 360.0
    return 'direction', round((a + ROCKET_ERR(pos[0], pos[1])) % 360.0, 2)


def measure4(arena, pos, ch):
    """推进虚拟时间并返回 (measure_result, svd_deg)。"""
    t = math.dist(arena['pos'], pos) / V
    if arena['ch'] != ch:
        t += T_SWITCH
    t += T_MEASURE
    arena['t'] += t
    arena['pos'] = pos
    arena['ch'] = ch
    return detect4(arena, pos, ch)


def clear4(arena, pos, ch):
    """推进虚拟时间并返回 clear_result。与类型/朝向无关；不切换频道。"""
    t = math.dist(arena['pos'], pos) / V
    s = arena['srcs'].get(ch)
    ok = (s is not None) and math.dist(pos, (s['x'], s['y'])) <= CLR
    t += (T_OPTICAL + T_CLEAR) if ok else T_OPTICAL
    arena['t'] += t
    arena['pos'] = pos
    if ok:
        del arena['srcs'][ch]
    return 'success' if ok else 'no_target_in_range'


# --------------------------------------------------------------------------
# 2. HTTP 层（与 Q3 mock 同构：串行、幂等、400/404/409）
# --------------------------------------------------------------------------

class Handler4(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _bad(self, msg):
        self._send(400, {'error': msg})

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(n).decode('utf-8'))
        except Exception:
            return self._bad('bad json')
        path = self.path
        if path not in ('/enter', '/measure', '/clear', '/exit'):
            return self._send(404, {'error': 'unknown'})
        ar = STATE['arena']
        rid = body.get('request_id')
        if not rid:
            return self._bad('missing request_id')
        cache = STATE['idem']
        key = json.dumps(body, sort_keys=True)
        if rid in cache:
            old, resp = cache[rid]
            if old == key:
                return self._send(200, resp)
            return self._send(409, {'error': 'request_id reused with different body'})

        def accept(resp):
            cache[rid] = (key, resp)
            self._send(200, resp)

        if path == '/enter':
            if ar['entered']:
                return accept({'accepted': False, 'real_timestamp_ms': int(time.time() * 1000),
                               'virtual_time_s': 0})
            ar['entered'] = True
            return accept({'accepted': True, 'real_timestamp_ms': int(time.time() * 1000),
                           'virtual_time_s': 0.0, 'max_virtual_duration_s': 360000,
                           'max_real_duration_s': 1200, 'remaining_real_duration_s': 1200})
        if not ar['entered']:
            return accept({'accepted': False, 'real_timestamp_ms': int(time.time() * 1000),
                           'virtual_time_s': 0})
        if path == '/exit':
            ar['entered'] = False
            return accept({'accepted': True, 'real_timestamp_ms': int(time.time() * 1000),
                           'virtual_time_s': round(ar['t'], 6), 'exit_reason': 'user_exit'})
        pos = body.get('position', {})
        ch = body.get('channel')
        if ch is None or not (1 <= int(ch) <= 20):
            return self._bad('bad channel')
        p = (float(pos.get('x', 0.0)), float(pos.get('y', 0.0)))
        if path == '/measure':
            z, svd = measure4(ar, p, int(ch))
            o = {'accepted': True, 'real_timestamp_ms': int(time.time() * 1000),
                 'virtual_time_s': round(ar['t'], 6), 'measure_result': z}
            if z == 'direction':
                o['svd_deg'] = svd
            return accept(o)
        if path == '/clear':
            r = clear4(ar, p, int(ch))
            return accept({'accepted': True, 'real_timestamp_ms': int(time.time() * 1000),
                           'virtual_time_s': round(ar['t'], 6), 'clear_result': r})


STATE = {}


def serve4(port, arena):
    STATE['arena'] = arena
    STATE['idem'] = {}
    return HTTPServer(('127.0.0.1', port), Handler4)


# --------------------------------------------------------------------------
# 3. 回归套件（C-5a ~ C-5h、C-1a / C-1b、计时）
# --------------------------------------------------------------------------

from b26_q4_certificate import detects, R_MIN          # 独立第二条路径（定义级算子）


def _grid(step, rmax):
    n = int(rmax / step)
    return [(i * step, j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)]


def c5a_omni_bitwise(seeds=(1, 2, 3), step=100.0, rmax=2100.0):
    """C-5a：全向 arena 上 mock4 与冻结 Q3 mock 的 /measure 逐点一致（含 svd_deg）。"""
    pts = _grid(step, rmax)
    tot = 0
    diff = 0
    ex = []
    for sd in seeds:
        a3 = M3.new_arena(sd)
        a4 = dict(srcs={c: dict(x=s['x'], y=s['y'], r=s['r'], type='omni', beta=None)
                        for c, s in a3['srcs'].items()},
                  N=a3['N'], t=0.0, pos=(0.0, 0.0), ch=1, entered=True, t0=0.0,
                  sector_half=SECTOR_HALF_DEG, coincident_rule='literal')
        for (x, y) in pts:
            for ch in CHANNELS:
                r3 = M3.measure(a3, (x, y), ch)
                r4 = measure4(a4, (x, y), ch)
                tot += 1
                if r3 != r4:
                    diff += 1
                    if len(ex) < 5:
                        ex.append(dict(种子=sd, P=[x, y], 频道=ch, Q3=r3, Q4=r4))
    return dict(名称='C-5a 全向逐点一致（vs 冻结 Q3 mock）', 用例数=tot, 不一致数=diff,
                样例=ex, 结论=('PASS' if diff == 0 else 'FAIL'))


def c5b_dir_vs_definition(n=20000, seed=5):
    """C-5b：定向源语义 vs 证书模块的定义级算子 detects()（两条原理不同的路径）。"""
    rng = random.Random(seed)
    mm = 0
    near_bad = 0
    svd_bad = 0
    tot = 0
    ex = []
    for _ in range(n):
        gx, gy = rng.uniform(-R, R), rng.uniform(-R, R)
        r = rng.uniform(1000.0, 1500.0)
        beta = rng.uniform(0.0, 360.0)
        px, py = rng.uniform(-2500.0, 2500.0), rng.uniform(-2500.0, 2500.0)
        ar = dict(srcs={7: dict(x=gx, y=gy, r=r, type='dir', beta=beta)}, sector_half=90.0,
                  coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
        z, svd = detect4(ar, (px, py), 7)
        det = detects((gx, gy), (px, py), beta, r)
        tot += 1
        if (z != 'no_signal') != det:
            mm += 1
            if len(ex) < 5:
                ex.append(dict(P=[px, py], g=[gx, gy], beta=beta, r=r, mock=z, 定义=det))
        d = math.dist((px, py), (gx, gy))
        if z == 'near' and d > NEAR + 1e-9:
            near_bad += 1
        if z == 'direction':
            true_a = math.degrees(math.atan2(gy - py, gx - px)) % 360.0
            err = ((svd - true_a + 180.0) % 360.0) - 180.0
            # 题面误差界为 [-1,1]（对真值误差）；附件2 要求 svd_deg 保留两位小数，
            # 故上报值的隐含误差可达 1 + 0.005（四舍五入），公差按此设定。
            if abs(err) > 1.0 + 0.005 + 1e-9:
                svd_bad += 1
    ok = (mm == 0 and near_bad == 0 and svd_bad == 0)
    return dict(名称='C-5b 定向语义 vs 定义级算子', 用例数=tot, 语义不一致=mm,
                near越界数=near_bad, 误差超限次数=svd_bad, 样例=ex,
                误差公差='1.0 + 0.005（附件2 两位小数四舍五入）',
                结论=('PASS' if ok else 'FAIL'))


def c5c_boundary_source():
    """C-5c：边界源（rho=1800）朝区域外：区域内探测点应全部 no_signal；越界探测点可检出。"""
    g = (R, 0.0)
    beta = 0.0
    ar = dict(srcs={3: dict(x=g[0], y=g[1], r=1500.0, type='dir', beta=beta)}, sector_half=90.0,
              coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
    inside = [p for p in _grid(100.0, R) if math.hypot(p[0], p[1]) <= R]
    det_in = 0
    coincident = []
    for p in inside:
        z, _ = detect4(ar, p, 3)
        if z != 'no_signal':
            det_in += 1
            coincident.append(dict(P=p, 结果=z, d=round(math.dist(p, g), 6)))
    outside = [(2000.0, 0.0), (2100.0, 0.0), (1900.0, 200.0), (2500.0, 0.0), (1850.0, -100.0)]
    det_out = []
    for p in outside:
        z, svd = detect4(ar, p, 3)
        det_out.append(dict(P=p, d=round(math.dist(p, g), 2), 结果=z, svd=svd))
    ok = (det_in <= 1) and all(o['结果'] == 'direction' for o in det_out)
    return dict(名称='C-5c 边界源（rho=1800，beta 朝外）', 区域内探测点=len(inside),
                区域内被检出=det_in, 区域外探测点=det_out,
                备注='区域内唯一例外应为"与源重合"的探测点（字面语义返回 near，A13 保守规则不计入保证）',
                结论=('PASS' if ok else 'FAIL'))


def c5d_out_of_region_probe():
    """C-5d：越界探测点的检测与计时（Δd/5，附件 2 §1.1）。"""
    ar = new_arena4(seed=11, n=1, dir_frac=1.0, radial_bias=1000.0)
    ch = list(ar['srcs'].keys())[0]
    s = ar['srcs'][ch]
    s['r'] = 1500.0
    # 沿源的径向再向外 1200 m => 探测点位于目标区域之外，且距源 1200 m <= r
    ang = math.atan2(s['y'], s['x'])
    p = (s['x'] + 1200.0 * math.cos(ang), s['y'] + 1200.0 * math.sin(ang))
    s['beta'] = math.degrees(math.atan2(p[1] - s['y'], p[0] - s['x']))   # 朝向该探测点
    d = math.dist(p, (s['x'], s['y']))
    sw = 1.0 if ar['ch'] != ch else 0.0
    exp_t = math.dist((0.0, 0.0), p) / V + sw + T_MEASURE
    z, svd = measure4(ar, p, ch)
    return dict(名称='C-5d 越界探测点', 探测点=[round(p[0], 2), round(p[1], 2)],
                探针半径=round(math.hypot(p[0], p[1]), 1), 距源=round(d, 2), 结果=z,
                频道切换计费_s=sw, 虚拟时间=round(ar['t'], 4), 期望时间=round(exp_t, 4),
                结论=('PASS' if (z in ('direction', 'near') and abs(ar['t'] - exp_t) < 1e-9) else 'FAIL'))


def c5e_near_semantics():
    """C-5e：near 的扇区前提（≤5 m 且在扇区内 -> near；≤5 m 且扇区外 -> no_signal）。"""
    ar = dict(srcs={3: dict(x=0.0, y=0.0, r=1500.0, type='dir', beta=0.0)}, sector_half=90.0,
              coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
    # 期望值由题面规则直接给出：d<=5 且在扇区[b-90,b+90]内 -> near；d<=5 但扇区外 -> no_signal
    cases = [((3.0, 0.0), 'near'),        # d=3.0，方位 0°，在扇区内
             ((-3.0, 0.0), 'no_signal'),  # d=3.0，方位 180°，扇区外（关键 Q4 语义）
             ((0.0, 3.0), 'near'),        # d=3.0，方位 90°（端点，闭区间）
             ((0.0, -3.0), 'near'),       # d=3.0，方位 -90°（端点，闭区间）
             ((-3.0, -0.001), 'no_signal'),
             ((-3.0, 3.0), 'no_signal'),  # d=4.24，方位 135°，扇区外
             ((-4.9, 0.0), 'no_signal'),  # d=4.9，方位 180°，扇区外
             ((2.9, 2.9), 'near')]        # d=4.10，方位 45°，扇区内
    rows = []
    ok = True
    for (p, exp) in cases:
        z, _ = detect4(ar, p, 3)
        good = (z == exp)
        ok = ok and good
        rows.append(dict(P=p, 期望=exp, 实测=z, 通过=good))
    return dict(名称='C-5e near 的扇区前提（附件2 §2.4）', 用例=rows,
                结论=('PASS' if ok else 'FAIL'))


def c5f_clear_direction_independent():
    """C-5f：/clear 与朝向无关 + 半径边界 + 重复清除 + 计时。"""
    ar = dict(srcs={3: dict(x=0.0, y=0.0, r=1500.0, type='dir', beta=0.0),
                    4: dict(x=1000.0, y=0.0, r=1500.0, type='dir', beta=180.0)},
              sector_half=90.0, coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
    r1 = clear4(ar, (-15.0, 0.0), 3)                     # 扇区正后方（beta=0 的背面）
    t1 = ar['t']
    r2 = clear4(ar, (-15.0, 0.0), 3)                     # 重复清除
    r3 = clear4(ar, (1030.0, 0.0), 4)                    # 距离 30 m > 20
    r4 = clear4(ar, (990.0, 0.0), 4)                     # 距离 -10 m <= 20
    ok = (r1 == 'success' and r2 == 'no_target_in_range' and r3 == 'no_target_in_range'
          and r4 == 'success')
    return dict(名称='C-5f clear 与朝向无关', 扇区背面清除=r1, 重复清除=r2, 超距清除=r3,
                对侧清除=r4, 清除成功虚拟时间=round(t1, 4),
                结论=('PASS' if ok else 'FAIL'))


def c5g_time_accounting(port=20401):
    """C-5g：HTTP 全链路时间账（对齐附件 2 §10 的示例）。"""
    import http.client
    ar = new_arena4(seed=3, n=12, dir_frac=0.5)
    srv = serve4(port, ar)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    time.sleep(0.3)

    def post(path, payload):
        c = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
        c.request('POST', path, body=json.dumps(payload).encode('utf-8'),
                  headers={'Content-Type': 'application/json'})
        r = c.getresponse()
        o = json.loads(r.read().decode('utf-8'))
        c.close()
        return r.status, o

    base = dict(arena_id='default', robot_id='202612345678')
    seq = [
        ('/enter', dict(base, request_id='e1'), 0.0),
        ('/measure', dict(base, request_id='m1', position=dict(x=300, y=400), channel=1), 105.0),
        ('/measure', dict(base, request_id='m2', position=dict(x=300, y=400), channel=2), 111.0),
        ('/clear', dict(base, request_id='c1', position=dict(x=300, y=0), channel=3), 194.0),
        ('/measure', dict(base, request_id='m3', position=dict(x=300, y=0), channel=2), 199.0),
        ('/exit', dict(base, request_id='x1'), 199.0),
    ]
    rows = []
    ok = True
    for (path, payload, exp) in seq:
        st, o = post(path, payload)
        vt = o.get('virtual_time_s')
        good = (st == 200 and o.get('accepted') is True and abs(vt - exp) < 1e-6)
        ok = ok and good
        rows.append(dict(指令=path, 期望时刻=exp, 实测=vt, HTTP=st, 通过=good))
    srv.shutdown()
    return dict(名称='C-5g 时间账（HTTP 全链路，附件2 §10 示例）', 序列=rows,
                结论=('PASS' if ok else 'FAIL'))


def c5h_protocol(port=20402):
    """C-5h：幂等 / 409 / 400 / 未 enter（与 Q3 协议测试同口径）。"""
    import http.client
    ar = new_arena4(seed=4, n=10, dir_frac=0.5)
    srv = serve4(port, ar)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)

    def raw(payload, path='/measure'):
        c = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
        c.request('POST', path, body=json.dumps(payload).encode('utf-8'),
                  headers={'Content-Type': 'application/json'})
        r = c.getresponse()
        code = r.status
        try:
            o = json.loads(r.read().decode('utf-8'))
        except Exception:
            o = None
        c.close()
        return code, o

    base = dict(arena_id='default', robot_id='202612345678')
    rows = []
    code, o = raw(dict(base, request_id='pre', position=dict(x=0, y=0), channel=1))
    rows.append(dict(项='未 /enter 时 accepted=false 且 vt=0',
                     通过=bool(o and o.get('accepted') is False and o.get('virtual_time_s') == 0),
                     详情=str(o)))
    raw(dict(base, request_id='e1'), '/enter')
    p = dict(base, request_id='i1', position=dict(x=10, y=10), channel=1)
    _, o1 = raw(p)
    _, o2 = raw(p)
    rows.append(dict(项='同 ID 同内容 -> 返回首次响应（不重复推进时间）', 通过=(o1 == o2), 详情='两次响应相同'))
    c3, _ = raw(dict(base, request_id='i1', position=dict(x=99, y=99), channel=1))
    rows.append(dict(项='同 ID 不同内容 -> HTTP 409', 通过=(c3 == 409), 详情='HTTP %s' % c3))
    c4, _ = raw(dict(base, request_id='bad', position=dict(x=0, y=0), channel=77))
    rows.append(dict(项='channel 越界 -> HTTP 400', 通过=(c4 == 400), 详情='HTTP %s' % c4))
    srv.shutdown()
    return dict(名称='C-5h 协议一致性（Q3 -> Q4 无退化）', 行=rows,
                结论=('PASS' if all(r['通过'] for r in rows) else 'FAIL'))


def c1_full_circle(n=20000, seed=9, step=20.0):
    """C-1：全圆极限。C-1a 语义等价；C-1b 算子等价（r 固定为 r_min）。"""
    rng = random.Random(seed)
    mm = 0
    near_bad = 0
    for _ in range(n):
        gx, gy = rng.uniform(-R, R), rng.uniform(-R, R)
        r = rng.uniform(1000.0, 1500.0)
        beta = rng.uniform(0.0, 360.0)
        px, py = rng.uniform(-2500.0, 2500.0), rng.uniform(-2500.0, 2500.0)
        ar = dict(srcs={5: dict(x=gx, y=gy, r=r, type='dir', beta=beta)}, sector_half=180.0,
                  coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
        z, _ = detect4(ar, (px, py), 5)
        d = math.dist((px, py), (gx, gy))
        if (z != 'no_signal') != (d <= r):
            mm += 1
        if (z == 'near') != (d <= NEAR):
            near_bad += 1
    a_ok = (mm == 0 and near_bad == 0)
    # C-1b：算子层等价（固定 r = r_min）
    S = [(1500.0, 0.0), (-1500.0, 0.0), (0.0, 1500.0), (0.0, -1500.0), (1000.0, 1000.0)]
    pts = [p for p in _grid(step, R) if math.hypot(p[0], p[1]) <= R]
    exc = 0
    for P in pts:
        ar = dict(srcs={c: dict(x=P[0], y=P[1], r=R_MIN, type='dir', beta=0.0) for c in (1,)},
                  sector_half=180.0, coincident_rule='literal', pos=(0.0, 0.0), t=0.0, ch=1)
        hit = any(detect4(ar, s, 1)[0] != 'no_signal' for s in S)
        union = any(math.dist(P, s) <= R_MIN for s in S)
        if hit != union:
            exc += 1
    b_ok = (exc == 0)
    return dict(名称='C-1 全圆极限退化', C1a_用例=n, C1a_语义不一致=mm, C1a_near不一致=near_bad,
                C1b_采样点=len(pts), C1b_例外=exc, C1b_网格步长=step,
                结论=('PASS' if (a_ok and b_ok) else 'FAIL'))


def regress(out_json=OUT_JSON, verbose=True):
    t_all = time.time()
    rep = dict(生成时间=time.strftime('%Y-%m-%d %H:%M:%S'),
               说明=('b26_mock4 自建 mock 的定向源语义回归。**不是官方模拟器**；'
                     '本报告只证明 mock 与 Q4 设计一致，以及 Q3->Q4 无语义退化，'
                     '不能证明官方语义一致（官方仍需现场核对）。'),
               常量=dict(R=R, V=V, NEAR=NEAR, CLR=CLR, T_MEASURE=T_MEASURE, T_SWITCH=T_SWITCH,
                         T_OPTICAL=T_OPTICAL, T_CLEAR=T_CLEAR, SECTOR_HALF_DEG=SECTOR_HALF_DEG))
    blocks = []
    for fn in (c5a_omni_bitwise, c5b_dir_vs_definition, c5c_boundary_source,
               c5d_out_of_region_probe, c5e_near_semantics, c5f_clear_direction_independent,
               c5g_time_accounting, c5h_protocol, c1_full_circle):
        t0 = time.time()
        try:
            r = fn()
        except Exception as e:
            r = dict(名称=fn.__name__, 结论='FAIL', 异常=str(e)[:200])
        r['耗时_s'] = round(time.time() - t0, 3)
        blocks.append(r)
        if verbose:
            print('[%s] %s (%.2fs)' % (r.get('结论'), r.get('名称'), r['耗时_s']))
    rep['回归项'] = blocks
    allpass = all(b.get('结论') == 'PASS' for b in blocks)
    rep['总体结论'] = 'PASS' if allpass else 'FAIL'
    rep['总耗时_s'] = round(time.time() - t_all, 3)
    rep['官方仍待核对（本回归无法覆盖）'] = [
        'T1 未知字段返回语义', 'T2 arena_id 错误', 'T3 robot_id 不匹配', 'T4 坐标越界',
        'Q4-1 定向源在扇区外返回 no_signal（且不返回 svd_deg）',
        'Q4-2 距离 <= 5 m 且在扇区外时返回 no_signal 而非 near',
        'Q4-3 扇区端点（|phi-beta| = 90 度）是否算在覆盖内（按"含"实现）',
        'Q4-4 /clear 对定向源在扇区外是否仍成功（按"与朝向无关"实现）',
        'Q4-5 探测点与源重合（距离 0）时的返回语义（本 mock 按字面返回 near；证书按 A13 保守不计入）',
    ]
    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
        if verbose:
            print('已写入 ' + out_json)
    return rep


def _timing_probe(port=20403, n_req=200):
    """计时探针：本地回环 HTTP 往返开销（仅记录，不外推到官方/控制器）。"""
    import http.client
    ar = new_arena4(seed=21, n=12, dir_frac=0.5)
    srv = serve4(port, ar)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    base = dict(arena_id='default', robot_id='202612345678')
    t0 = time.time()
    c.request('POST', '/enter', body=json.dumps(dict(base, request_id='e1')).encode('utf-8'),
              headers={'Content-Type': 'application/json'})
    c.getresponse().read()
    for i in range(n_req):
        pl = dict(base, request_id='p%d' % i, position=dict(x=float(i % 50), y=float(i % 37)),
                  channel=1 + (i % 20))
        c.request('POST', '/measure', body=json.dumps(pl).encode('utf-8'),
                  headers={'Content-Type': 'application/json'})
        c.getresponse().read()
    dt = time.time() - t0
    c.close()
    srv.shutdown()
    return dict(请求数=n_req + 1, 总墙钟_s=round(dt, 4), 单请求均值_ms=round(1000.0 * dt / (n_req + 1), 4),
                说明='仅本地回环 mock 开销；**不得**外推为官方 Q4 控制器或正式测试的性能')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_JSON)
    ap.add_argument('--timing', action='store_true')
    a = ap.parse_args()
    r = regress(out_json=a.out)
    if a.timing:
        r['计时探针'] = _timing_probe()
        print(json.dumps(r['计时探针'], ensure_ascii=False, indent=1))
    print('\n=== 总体：%s ===' % r['总体结论'])
