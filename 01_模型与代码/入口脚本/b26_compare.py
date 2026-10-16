# -*- coding: utf-8 -*-
"""三种选点策略 × 覆盖方案 的对照实验（走真实 HTTP 链路 + mock 模拟器）。"""
import json, os, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search

PORT = 20261
D = os.path.dirname(os.path.abspath(__file__))

def once(seed, strategy, cover, mode, verbose=False):
    srv = M.serve(PORT, seed)
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    time.sleep(0.25)
    log = os.path.join(D, "_work_b26_cmp_log.jsonl")
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
    try:
        r = Robot(c, cover=cover, strategy=strategy, cover_mode=mode, verbose=verbose).run()
    finally:
        c.close(); srv.shutdown(); th.join(timeout=2)
    r["N"] = M.STATE["arena"]["N"]; r["req"] = c.n_req
    return r

def batch(name, seeds, strategy, cover, mode):
    rs = [once(s, strategy, cover, mode) for s in seeds]
    n = len(rs)
    cl = sum(x["cleared"] for x in rs); N = sum(x["N"] for x in rs)
    return dict(方案=name, 局数=n, 清除比例=round(cl/N, 4),
                全清局数="%d/%d" % (sum(1 for x in rs if x["cleared"] == x["N"]), n),
                平均定位清除时间_s=round(sum(x["virtual_time"] for x in rs)/max(1, cl), 1),
                总虚拟时间_s=round(sum(x["virtual_time"] for x in rs)/n, 1),
                检测次数=round(sum(x["measured"] for x in rs)/n, 1),
                复测轮数=round(sum(x["refine_rounds"] for x in rs)/n, 1),
                清除失败=round(sum(x["clear_fail"] for x in rs)/n, 2),
                移动距离_m=round(sum(x["dist"] for x in rs)/n, 1),
                HTTP请求=round(sum(x["req"] for x in rs)/n, 1))

if __name__ == "__main__":
    seeds = list(range(1, 9))
    out = []
    print("=== 实验一：第二个检测点选点策略对照（覆盖方案固定为 7 点）===")
    for stg, nm in (("centroid", "0 就近复测(基线)"), ("fixed90", "A 固定90°"), ("perp547", "B 54.7°(√2d)"), ("dynamic", "C 动态选点")):
        r = batch(nm, seeds, stg, search.COVER_7, "fixed"); out.append(r)
        print(json.dumps(r, ensure_ascii=False))
    print("\n=== 实验二：覆盖方案（选点策略固定为实验一最优者）===")
    best = "dynamic"
    for cover, mode, nm in ((search.COVER_7, "fixed", "D 7点固定"),
                            (search.COVER_9, "fixed", "E 9点固定(裕量173m)"),
                            (search.COVER_7, "adaptive", "F 自适应缺口驱动"),
                            (search.COVER_9, "adaptive", "G 9点+自适应")):
        r = batch(nm, seeds, best, cover, mode); out.append(r)
        print(json.dumps(r, ensure_ascii=False))
    json.dump(out, open(os.path.join(D, "_work_b26_cmp.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n结果已写入 _work_b26_cmp.json")
