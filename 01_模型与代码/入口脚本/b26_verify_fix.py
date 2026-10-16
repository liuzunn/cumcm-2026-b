# -*- coding: utf-8 -*-
"""修复后定点验证：跑此前卡死的 3 个 seed，看门禁 1/2 是否通过。"""
import os, sys, threading, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search, config
PORT = 20295; D = os.path.dirname(os.path.abspath(__file__))
srv = M.serve(PORT, 1); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
for seed in (8, 30, 17):
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", os.path.join(D, "_w_v.jsonl"))
    try:
        r = Robot(c, cover=config.COVER, strategy="centroid", cover_mode="adaptive").run()
        N = M.STATE["arena"]["N"]
    finally:
        c.close()
    print(json.dumps(dict(seed=seed, N=N, cleared=r["cleared"], 清除比例=round(r["cleared"]/N,4),
        虚拟时间_s=round(r["virtual_time"],1), 平均_s=round(r["virtual_time"]/max(1,r["cleared"]),1),
        步数=r["steps_used"], 覆盖点=r["covered_count"], 停滞触发=r["stall_trips"],
        硬上限触发=r["hard_cap_hit"], 卡死频道=r["stuck"], 清除失败=r["clear_fail"],
        HTTP请求=c.n_req), ensure_ascii=False))
srv.shutdown()
