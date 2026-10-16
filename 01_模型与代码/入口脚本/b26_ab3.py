# -*- coding: utf-8 -*-
"""三臂补强：基线 / 动态(只看精度) / 动态(含路程项)，各 16 局。"""
import json, os, sys, threading, time
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search
PORT = 20263; D = os.path.dirname(os.path.abspath(__file__))
def once(seed, strategy):
    srv = M.serve(PORT, seed); th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    time.sleep(0.2)
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", os.path.join(D, "_w.jsonl"))
    try: r = Robot(c, cover=search.COVER_7, strategy=strategy, cover_mode="adaptive").run()
    finally: c.close(); srv.shutdown(); th.join(timeout=2)
    r["N"] = M.STATE["arena"]["N"]; return r
out = {}
for stg, nm in (("centroid","0 就近复测(基线)"), ("dynamic","C 动态(只看精度)"), ("dynamicT","C2 动态(含路程项)")):
    rs = [once(s, stg) for s in range(1, 17)]
    A = [x["virtual_time"]/max(1, x["cleared"]) for x in rs]
    out[nm] = dict(清除比例=round(sum(x["cleared"] for x in rs)/sum(x["N"] for x in rs), 4),
                   均值=round(st.mean(A),1), 标准差=round(st.pstdev(A),1),
                   最小=round(min(A),1), 最大=round(max(A),1),
                   移动距离=round(st.mean([x["dist"] for x in rs]),1),
                   复测轮数=round(st.mean([x["refine_rounds"] for x in rs]),2))
    print(json.dumps({nm: out[nm]}, ensure_ascii=False))
json.dump(out, open(os.path.join(D,"_work_b26_ab3.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
