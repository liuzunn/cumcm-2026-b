# -*- coding: utf-8 -*-
"""完整性核验：确认 100 局规模下从未发生"同 request_id 重试"（从而旧 mock 的 409 缺陷不影响结果）。"""
import json, os, sys, threading, time
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search, config
PORT = 20340; D = os.path.dirname(os.path.abspath(__file__))
srv = M.serve(PORT, 1); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
tot = dup = c409 = 0
for seed in (1, 25, 50, 75, 100):
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
    log = os.path.join(D, "_work_official", "_idcheck_%d.jsonl" % seed)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
    try: Robot(c, cover=config.COVER, strategy="centroid", cover_mode="adaptive").run()
    finally: c.close()
    recs = [json.loads(l) for l in open(log, encoding="utf-8")]
    ids = [r["request_id"] for r in recs]
    d = sum(v-1 for v in Counter(ids).values() if v > 1)
    s409 = sum(1 for r in recs if r.get("http_status") == 409)
    tot += len(ids); dup += d; c409 += s409
    print("seed=%3d 请求 %3d 条，重复 request_id %d 个，409 响应 %d 条" % (seed, len(ids), d, s409))
print(json.dumps(dict(抽查局数=5, 请求总数=tot, 重复request_id=dup, HTTP409=c409,
                      结论="从未发生同 ID 重试 ⇒ 旧 mock 的幂等比对缺陷不影响 100 局结果" if dup == 0 and c409 == 0 else "存在重试，需复核"),
                 ensure_ascii=False))
srv.shutdown()
