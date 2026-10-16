# -*- coding: utf-8 -*-
"""100 局 × 4 臂同种子配对实验（冻结配置，禁止任何算法修改）。"""
import json, math, os, sys, threading, time
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26.robot import Robot
from b26 import search, config

PORT = 20310; D = os.path.dirname(os.path.abspath(__file__))
NSEED = 100
T_975 = {99: 1.984, 36: 2.030}
T_BONF = {99: 2.365}          # Bonferroni: alpha=0.05/3 -> t(0.9833, 99)

def once(seed, cover, mode, strategy):
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
    log = os.path.join(D, "_work_b26_100_log.jsonl")
    c = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
    t0 = time.time(); err = None
    try:
        r = Robot(c, cover=cover, strategy=strategy, cover_mode=mode).run()
        r["N"] = M.STATE["arena"]["N"]
    except Exception as e:
        err = str(e)[:120]; r = None
    finally:
        c.close()
    if r is None:
        return dict(seed=seed, err=err, cleared=0, N=0, avg=0.0, virtual_time=0.0,
                    measured=0, refine_rounds=0, dist=0.0, req=c.n_req,
                    wall_s=round(time.time()-t0,2), log_kb=0.0, steps_used=0,
                    stall_trips=0, hard_cap_hit=False, stuck=[], max_sig_repeat=0)
    r["seed"] = seed; r["req"] = c.n_req
    r["wall_s"] = round(time.time()-t0, 2)
    r["log_kb"] = round(os.path.getsize(log)/1024.0, 1)
    r["avg"] = r["virtual_time"]/max(1, r["cleared"])
    r["err"] = err
    return r

def agg(rs):
    A = [x["avg"] for x in rs]
    n = len(A); m = st.mean(A); sp = st.pstdev(A); ss = st.stdev(A)
    t = T_975.get(n-1, 1.984); hw = t*sp/math.sqrt(n)
    As = sorted(A)
    def pct(p):
        k = min(len(As)-1, max(0, int(round(p/100.0*(len(As)-1)))))
        return As[k]
    cl = sum(x["cleared"] for x in rs); NN = sum(x["N"] for x in rs)
    byN = {}
    for x in rs: byN.setdefault(x["N"], []).append(x["avg"])
    return dict(局数=n, 清除比例=round(cl/NN, 6),
                全清局数="%d/%d" % (sum(1 for x in rs if x["cleared"] == x["N"]), n),
                均值s=round(m, 2), 总体标准差s=round(sp, 2), 样本标准差s=round(ss, 2),
                标准误s=round(sp/math.sqrt(n), 2),
                CI95半宽s=round(hw, 2), CI95区间=[round(m-hw, 2), round(m+hw, 2)],
                中位数s=round(st.median(A), 2), 最小s=round(min(A), 2), 最大s=round(max(A), 2),
                P90s=round(pct(90), 2), P95s=round(pct(95), 2),
                总虚拟时间均值s=round(st.mean([x["virtual_time"] for x in rs]), 1),
                检测次数=round(st.mean([x["measured"] for x in rs]), 2),
                复测轮数=round(st.mean([x["refine_rounds"] for x in rs]), 2),
                移动距离m=round(st.mean([x["dist"] for x in rs]), 1),
                HTTP请求均值=round(st.mean([x["req"] for x in rs]), 1),
                HTTP请求最大=int(max(x["req"] for x in rs)),
                单局墙钟均值s=round(st.mean([x["wall_s"] for x in rs]), 3),
                单局墙钟最大s=round(max(x["wall_s"] for x in rs), 3),
                日志体积均值KB=round(st.mean([x["log_kb"] for x in rs]), 1),
                日志体积最大KB=round(max(x["log_kb"] for x in rs), 1),
                平均步数=round(st.mean([x["steps_used"] for x in rs]), 1),
                最大步数=int(max(x["steps_used"] for x in rs)),
                停滞触发局数=sum(1 for x in rs if x["stall_trips"] > 0),
                硬上限触发局数=sum(1 for x in rs if x["hard_cap_hit"]),
                卡死频道局数=sum(1 for x in rs if x["stuck"]),
                最大重复动作次数=int(max(x["max_sig_repeat"] for x in rs)),
                清除失败合计=int(sum(x["clear_fail"] for x in rs)),
                异常局数=sum(1 for x in rs if x.get("err")),
                按源数分层={k: round(st.mean(v), 1) for k, v in sorted(byN.items())})

def paired(X, Y, key):
    """X - Y 的配对差"""
    keys = sorted(set(X) & set(Y))
    d = [X[s][key] - Y[s][key] for s in keys]
    n = len(d); m = st.mean(d); sd = st.pstdev(d); sdd = st.stdev(d)
    hw = T_975.get(n-1, 1.984)*sd/math.sqrt(n)
    hwb = T_BONF.get(n-1, 2.365)*sd/math.sqrt(n)
    win = sum(1 for v in d if v < 0); lose = sum(1 for v in d if v > 0)
    return dict(n=n, 均值差=round(m, 2), 差值标准差=round(sd, 2),
                CI95=[round(m-hw, 2), round(m+hw, 2)],
                BonferroniCI=[round(m-hwb, 2), round(m+hwb, 2)],
                Cohen_d=round(m/sdd, 3) if sdd > 0 else None,
                X更快局数=win, Y更快局数=lose, 打平=n-win-lose,
                X胜率=round(100.0*win/n, 1))

srv = M.serve(PORT, 1); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
ARMS = [("G 9点+自适应", config.COVER, "adaptive"),
        ("F 7点+自适应", search.COVER_7, "adaptive"),
        ("E 9点+固定",   config.COVER, "fixed"),
        ("D 7点+固定",   search.COVER_7, "fixed")]
SEEDS = list(range(1, NSEED+1))
res = {}; per = {}
print(json.dumps(config.describe(), ensure_ascii=False))
for nm, cover, mode in ARMS:
    rs = [once(s, cover, mode, "centroid") for s in SEEDS]
    res[nm] = agg(rs)
    per[nm] = {x["seed"]: x for x in rs}
    print(json.dumps({nm: res[nm]}, ensure_ascii=False))
# 配对比较（以 G 为基准）
pair = {}
G = per["G 9点+自适应"]
for nm in ("F 7点+自适应", "E 9点+固定", "D 7点+固定"):
    key = "G vs " + nm.split()[0]
    pair[key] = dict(
        平均时间=paired(G, per[nm], "avg"),
        移动距离=paired(G, per[nm], "dist"),
        HTTP请求=paired(G, per[nm], "req"),
        检测次数=paired(G, per[nm], "measured"))
    print(json.dumps({key: pair[key]}, ensure_ascii=False))
json.dump(dict(配置=config.describe(), 结果=res, 配对=pair,
               逐局={k: {str(s): v for s, v in d.items()} for k, d in per.items()}),
          open(os.path.join(D, "_work_b26_100.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
srv.shutdown()
print("已写入 _work_b26_100.json")
