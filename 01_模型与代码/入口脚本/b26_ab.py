# -*- coding: utf-8 -*-
"""补强：基线 vs 动态选点，各 16 局，报均值±标准差（检验差异是否稳健）。"""
import json, os, sys, threading, time
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search
PORT = 20262; D = os.path.dirname(os.path.abspath(__file__))
def once(seed, strategy):
    srv = M.serve(PORT, seed); th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    time.sleep(0.2)
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", os.path.join(D, "_w.jsonl"))
    try: r = Robot(c, cover=search.COVER_7, strategy=strategy, cover_mode="adaptive").run()
    finally: c.close(); srv.shutdown(); th.join(timeout=2)
    r["N"] = M.STATE["arena"]["N"]; return r
out = {}
for stg, nm in (("centroid", "0 就近复测"), ("dynamic", "C 动态选点")):
    rs = [once(s, stg) for s in range(1, 17)]
    A = [x["virtual_time"]/max(1, x["cleared"]) for x in rs]
    Mv = [x["dist"] for x in rs]; Rf = [x["refine_rounds"] for x in rs]
    cl = sum(x["cleared"] for x in rs); N = sum(x["N"] for x in rs)
    out[nm] = dict(局数=len(rs), 清除比例=round(cl/N, 4),
                   平均定位清除时间_均值=round(st.mean(A), 1), 标准差=round(st.pstdev(A), 1),
                   最小值=round(min(A), 1), 最大值=round(max(A), 1),
                   移动距离_均值=round(st.mean(Mv), 1), 复测轮数_均值=round(st.mean(Rf), 2),
                   per_seed=[round(v, 1) for v in A])
    print(json.dumps({nm: out[nm]}, ensure_ascii=False))
json.dump(out, open(os.path.join(D, "_work_b26_ab.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
