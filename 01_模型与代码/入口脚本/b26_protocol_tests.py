# -*- coding: utf-8 -*-
"""协议一致性测试套件：对着 mock 模拟器逐条核对我方客户端是否按协议工作。
不在 mock 中实现的分支标为"待实测"，并写明在官方模拟器上要核对什么。"""
import http.client, json, os, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm

PORT = 20320; D = os.path.dirname(os.path.abspath(__file__))
HOST = "127.0.0.1"
RES = []

def raw(path, payload, expect=None):
    c = http.client.HTTPConnection(HOST, PORT, timeout=5)
    c.request("POST", path, body=json.dumps(payload).encode("utf-8"),
              headers={"Content-Type": "application/json"})
    r = c.getresponse(); body = r.read().decode("utf-8"); code = r.status; c.close()
    try: obj = json.loads(body)
    except Exception: obj = None
    return code, obj

def rec(name, verdict, detail):
    RES.append(dict(测试项=name, 结果=verdict, 详情=detail))
    print("%-4s %-34s %s" % (verdict, name, detail))

def reset(seed=5):
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}

srv = M.serve(PORT, 5); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
BASE = dict(arena_id="default", robot_id="202612345678")

# ---- 1) 未知字段 ----
reset(); raw("/enter", dict(BASE, request_id="e1"))
code, o = raw("/measure", dict(BASE, request_id="m1", position=dict(x=0, y=0), channel=1, foo=1))
rec("未知字段 → accepted=false", "待实测" if o and o.get("accepted") is not False else "通过",
    "HTTP %s, accepted=%s（本 mock 未实现该分支；官方需核对字段拼错时是否返回 accepted=false）" % (code, o and o.get("accepted")))

# ---- 2) arena_id 不匹配 ----
reset(); raw("/enter", dict(BASE, request_id="e1"))
code, o = raw("/measure", dict(arena_id="other", robot_id="202612345678", request_id="m1",
                               position=dict(x=0, y=0), channel=1))
rec("arena_id 错误 → accepted=false", "待实测" if o and o.get("accepted") is not False else "通过",
    "HTTP %s, accepted=%s（本 mock 未实现；官方需核对）" % (code, o and o.get("accepted")))

# ---- 3) robot_id 不匹配 ----
reset(); raw("/enter", dict(BASE, request_id="e1"))
code, o = raw("/measure", dict(arena_id="default", robot_id="999", request_id="m1",
                               position=dict(x=0, y=0), channel=1))
rec("robot_id 不匹配 → accepted=false", "待实测" if o and o.get("accepted") is not False else "通过",
    "HTTP %s, accepted=%s（本 mock 未实现；官方需核对）" % (code, o and o.get("accepted")))

# ---- 4) 幂等：同 ID 同内容 ----
reset(); raw("/enter", dict(BASE, request_id="e1"))
p = dict(BASE, request_id="idem-1", position=dict(x=0, y=0), channel=1)
c1, o1 = raw("/measure", p); c2, o2 = raw("/measure", p)
same = (o1 == o2)
c3, o3 = raw("/measure", dict(BASE, request_id="idem-2", position=dict(x=0, y=0), channel=2))
ok = same and abs(o3["virtual_time_s"] - (o2["virtual_time_s"] + 1 + 5)) < 1e-6
rec("同 ID 同内容 → 返回第一次响应且不重复推进时间", "通过" if ok else "不通过",
    "两次响应相同=%s；重放后新动作 t=%.1f（期望 %.1f）" % (same, o3["virtual_time_s"], o2["virtual_time_s"]+6))

# ---- 5) 幂等：同 ID 不同内容 → 409 ----
c4, o4 = raw("/measure", dict(BASE, request_id="idem-1", position=dict(x=9, y=9), channel=1))
rec("同 ID 不同内容 → HTTP 409", "通过" if c4 == 409 else "不通过", "HTTP %s" % c4)

# ---- 6) channel 越界 → 400 ----
c5, _ = raw("/measure", dict(BASE, request_id="bad-ch", position=dict(x=0, y=0), channel=99))
rec("channel 越界 → HTTP 400", "通过" if c5 == 400 else "不通过", "HTTP %s" % c5)

# ---- 7) 坐标超范围 ----
c6, o6 = raw("/measure", dict(BASE, request_id="bad-xy", position=dict(x=3e6, y=0), channel=1))
rec("坐标 |x| > 2e6 → HTTP 400", "待实测" if c6 != 400 else "通过", "HTTP %s（本 mock 未实现；官方需核对）" % c6)

# ---- 8) /clear 不切换频道 ----
reset(); raw("/enter", dict(BASE, request_id="e1"))
_, a = raw("/measure", dict(BASE, request_id="s1", position=dict(x=0, y=0), channel=1))
_, b = raw("/clear",   dict(BASE, request_id="c1", position=dict(x=0, y=0), channel=5))
_, c = raw("/measure", dict(BASE, request_id="s2", position=dict(x=0, y=0), channel=1))
d_clear = b["virtual_time_s"] - a["virtual_time_s"]
d_after = c["virtual_time_s"] - b["virtual_time_s"]
rec("/clear 不切换测向机频道", "通过" if abs(d_after - 5.0) < 1e-6 else "不通过",
    "clear 耗时 %.0f s（应 3=未发现）；其后 measure 耗时 %.0f s（应 5=无切换）" % (d_clear, d_after))

# ---- 9) accepted=false 时 virtual_time_s=0 ----
reset()
_c, o7 = raw("/measure", dict(BASE, request_id="pre-enter", position=dict(x=0, y=0), channel=1))
rec("未 /enter 时 accepted=false 且 vt=0", "通过" if (o7 and o7.get("accepted") is False and o7.get("virtual_time_s") == 0) else "不通过",
    "accepted=%s, virtual_time_s=%s（规范：不得当作当前时刻）" % (o7 and o7.get("accepted"), o7 and o7.get("virtual_time_s")))

# ---- 10) 时间账回代（跑一整局） ----
reset(seed=9)
log = os.path.join(D, "_work_official", "_proto.jsonl"); os.makedirs(os.path.dirname(log), exist_ok=True)
from b26.robot import Robot
from b26 import search
cm = Comm("http://127.0.0.1:%d" % PORT, "202612345678", log)
try: r = Robot(cm, cover=search.COVER_9, strategy="centroid", cover_mode="adaptive").run()
finally: cm.close()
recs = [json.loads(l) for l in open(log, encoding="utf-8")]
bad = 0
import math
cur_ch = 1                       # 测向机当前频道：只由 /measure 更新；/clear 不改变它
prev_pos = (0.0, 0.0)
prev_t = 0.0
for rr in recs:
    if not rr.get("response") or rr["response"].get("accepted") is not True: continue
    pos = rr["request"].get("position")
    p = (pos["x"], pos["y"]) if pos else prev_pos
    d = math.dist(prev_pos, p)
    if rr["path"] == "/measure":
        sw = 1.0 if rr["request"].get("channel") != cur_ch else 0.0
        cost = 5.0
    elif rr["path"] == "/clear":
        sw = 0.0                                  # /clear 不产生切换耗时
        cost = 3.0 if rr["response"].get("clear_result") == "no_target_in_range" else 5.0
    else:
        sw = cost = 0.0                           # /enter、/exit 不推进虚拟时间
    exp = prev_t + d/5.0 + sw + cost
    if abs(rr["response"]["virtual_time_s"] - exp) > 1e-6: bad += 1
    prev_t = rr["response"]["virtual_time_s"]; prev_pos = p
    if rr["path"] == "/measure": cur_ch = rr["request"]["channel"]
rec("时间账回代（整局逐对核账）", "通过" if bad == 0 else "不通过",
    "%d 条请求中不平 %d 对；末次虚拟时间 %.1f s" % (len(recs), bad, recs[-1]["response"]["virtual_time_s"]))
rec("整局清除比例（mock 真值）", "通过" if r["cleared"] == M.STATE["arena"]["N"] else "不通过",
    "清除 %d / 源数 %d" % (r["cleared"], M.STATE["arena"]["N"]))

srv.shutdown()
ok = sum(1 for x in RES if x["结果"] == "通过")
tj = sum(1 for x in RES if x["结果"] == "待实测")
ng = sum(1 for x in RES if x["结果"] == "不通过")
print("\n=== 汇总：通过 %d / 待实测 %d / 不通过 %d ===" % (ok, tj, ng))
json.dump(RES, open(os.path.join(D, "_work_b26_proto_tests.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
