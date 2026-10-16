# -*- coding: utf-8 -*-
"""端到端联调：启动 mock 模拟器 → 跑一局机器狗程序 → 打印统计。"""
import json, os, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search

PORT = 20260
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
COVER = search.COVER_9 if (len(sys.argv) > 2 and sys.argv[2] == "9") else search.COVER_7
D = os.path.dirname(os.path.abspath(__file__))

ok, worst, margin = search.coverage_certificate(COVER)
print("覆盖证书：最大未覆盖距离 %.1f m，裕量 %.1f m，合格=%s（点数 %d）" % (worst, margin, ok, len(COVER)))

srv = M.serve(PORT, SEED)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.4)
log = os.path.join(D, "_work_b26_robot_log.jsonl")
c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
try:
    r = Robot(c, cover=COVER, verbose=False).run()
finally:
    c.close(); srv.shutdown()
print(json.dumps(dict(seed=SEED, 覆盖点数=len(COVER), 源总数=M.STATE["arena"]["N"],
                      清除数=r["cleared"], 判空数=r["empty"],
                      清除比例=round(r["cleared"]/M.STATE["arena"]["N"], 4),
                      虚拟总时间_s=round(r["virtual_time"], 1),
                      平均定位清除时间_s=round(r["virtual_time"]/max(1, r["cleared"]), 1),
                      检测次数=r["measured"], 清除尝试=r["clears"], 清除失败=r["clear_fail"],
                      移动距离_m=round(r["dist"], 1), HTTP请求数=c.n_req,
                      日志行数=sum(1 for _ in open(log, encoding="utf-8"))),
                 ensure_ascii=False, indent=1))
