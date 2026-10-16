# -*- coding: utf-8 -*-
"""大规模复测：按冻结配置跑 N 局，报均值 ± 标准差与 95% 置信区间。"""
import json, math, os, sys, threading, time
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search, config

PORT = 20277; D = os.path.dirname(os.path.abspath(__file__))
T95 = {30: 2.045, 36: 2.030, 40: 2.023, 50: 2.009}

def ci95(xs):
    n = len(xs); m = st.mean(xs); s = st.pstdev(xs)
    t = T95.get(n, 2.0); hw = t*s/math.sqrt(n)
    return m, s, hw, m-hw, m+hw

_SRV = M.serve(PORT, 1)
threading.Thread(target=_SRV.serve_forever, daemon=True).start()
time.sleep(0.4)

def once(seed, cover, mode, strategy):
    # 复用同一个服务实例，只重置局面，避免 Windows 上端口 TIME_WAIT 造成的假异常
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
    log = os.path.join(D, "_work_b26_freeze_log.jsonl")
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
    t0 = time.time(); r = None; err = None
    try:
        r = Robot(c, cover=cover, strategy=strategy, cover_mode=mode).run()
        r["N"] = M.STATE["arena"]["N"]
    except Exception as e:
        err = str(e)[:120]
        r = dict(cleared=0, empty=0, virtual_time=0.0, measured=0, clears=0, clear_fail=0,
                 near=0, dist=0.0, refine_rounds=0, cover_points=0, N=M.STATE["arena"]["N"])
    finally:
        c.close()
    r["seed"] = seed; r["req"] = c.n_req; r["wall_s"] = round(time.time()-t0, 2)
    r["log_kb"] = round(os.path.getsize(log)/1024.0, 1)
    r["avg"] = r["virtual_time"]/max(1, r["cleared"]); r["err"] = err
    return r

ARMS = [("G 冻结(9点+自适应)", config.COVER, "adaptive", "centroid"),
        ("F 7点+自适应",       search.COVER_7, "adaptive", "centroid"),
        ("D 7点+固定(原始)",   search.COVER_7, "fixed",    "centroid")]
SEEDS = list(range(1, 37))
out = {}; PER = {}
print(json.dumps(config.describe(), ensure_ascii=False))
for nm, cover, mode, stg in ARMS:
    rs = [once(s, cover, mode, stg) for s in SEEDS]
    good = [x for x in rs if x["avg"] > 0]
    A = [x["avg"] for x in good]; T = [x["virtual_time"] for x in good]
    m, s, hw, lo, hi = ci95(A)
    cl = sum(x["cleared"] for x in rs); NN = sum(x["N"] for x in rs)
    byN = {}
    for x in rs: byN.setdefault(x["N"], []).append(x["avg"])
    o = dict(局数=len(rs), 有效局=len(good), 清除比例=round(cl/NN, 4),
             全清局数="%d/%d" % (sum(1 for x in rs if x["cleared"] == x["N"]), len(rs)),
             平均定位清除时间_均值s=round(m, 1), 标准差s=round(s, 1),
             CI95半宽s=round(hw, 1), CI95区间=[round(lo, 1), round(hi, 1)],
             最小s=round(min(A), 1), 最大s=round(max(A), 1),
             总虚拟时间_均值s=round(st.mean(T), 1),
             检测次数=round(st.mean([x["measured"] for x in rs]), 1),
             复测轮数=round(st.mean([x["refine_rounds"] for x in rs]), 1),
             移动距离_m=round(st.mean([x["dist"] for x in rs]), 1),
             HTTP请求_均值=round(st.mean([x["req"] for x in rs]), 1),
             HTTP请求_最大=int(max(x["req"] for x in rs)),
             单局墙钟_s=round(st.mean([x["wall_s"] for x in rs]), 2),
             日志体积_KB=round(st.mean([x["log_kb"] for x in rs]), 1),
             异常局数=sum(1 for x in rs if x["err"]),
             平均步数=round(st.mean([x.get("steps_used") or 0 for x in rs]), 1),
             最大步数=int(max([x.get("steps_used") or 0 for x in rs])),
             停滞触发局数=sum(1 for x in rs if (x.get("stall_trips") or 0) > 0),
             硬上限触发局数=sum(1 for x in rs if x.get("hard_cap_hit")),
             卡死频道局数=sum(1 for x in rs if x.get("stuck")),
             清除失败合计=int(sum(x["clear_fail"] for x in rs)),
             按源数分层={k: round(st.mean(v), 1) for k, v in sorted(byN.items())})
    out[nm] = o
    PER[nm] = [dict(seed=x["seed"], N=x["N"], cleared=x["cleared"], avg=round(x["avg"],1),
                    T=round(x["virtual_time"],1), meas=x["measured"], fail=x["clear_fail"],
                    dist=round(x["dist"],1), req=x["req"], err=x["err"],
                    steps=x.get("steps_used"), stall=x.get("stall_trips"),
                    hardcap=x.get("hard_cap_hit"), stuck=len(x.get("stuck") or [])) for x in rs]
    print(json.dumps({nm: o}, ensure_ascii=False))
json.dump(out, open(os.path.join(D, "_work_b26_freeze.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(PER, open(os.path.join(D, "_work_b26_freeze_per.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写入 _work_b26_freeze.json / _work_b26_freeze_per.json")
