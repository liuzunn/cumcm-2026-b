# -*- coding: utf-8 -*-
"""门禁 2 补充：统计 36 局的动作签名重复次数。"""
import os, sys, threading, time, json
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import config, search
PORT = 20298; D = os.path.dirname(os.path.abspath(__file__))
srv = M.serve(PORT, 1); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
res = {}
for nm, cover, mode in (("G 9点+自适应", config.COVER, "adaptive"),
                        ("F 7点+自适应", search.COVER_7, "adaptive"),
                        ("D 7点+固定",   search.COVER_7, "fixed")):
    ms = []; us = []; stp = []
    for seed in range(1, 37):
        M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
        c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", os.path.join(D, "_w_v.jsonl"))
        try: r = Robot(c, cover=cover, strategy="centroid", cover_mode=mode).run()
        finally: c.close()
        ms.append(r["max_sig_repeat"]); us.append(r["uniq_sig"]); stp.append(r["steps_used"])
    res[nm] = dict(最大重复动作次数=int(max(ms)), 平均最大重复=round(st.mean(ms), 2),
                   平均唯一签名数=round(st.mean(us), 1), 平均步数=round(st.mean(stp), 1))
    print(json.dumps({nm: res[nm]}, ensure_ascii=False))
srv.shutdown()
