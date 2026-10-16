# -*- coding: utf-8 -*-
"""本地 mock 模拟器：严格按附件1/附件2 的计时与幂等规则实现 4 个端点，用于离线联调。
注意：这是本队自建的复现件，不是官方模拟器。"""
import json, math, random, hashlib, time
from http.server import BaseHTTPRequestHandler, HTTPServer

R = 1800.0; V = 5.0; T_MEASURE = 5.0; T_SWITCH = 1.0; T_OPTICAL = 3.0; T_CLEAR = 2.0
NEAR = 5.0; CLR = 20.0
CHANNELS = list(range(1, 21))
STATE = {}

def _err(x, y):
    k = "%d_%d" % (round(x / 5.0), round(y / 5.0))
    return (int(hashlib.md5(k.encode()).hexdigest()[:8], 16) % 20001) / 10000.0 - 1.0

def new_arena(seed=None):
    rng = random.Random(seed)
    N = rng.randint(10, 16)
    srcs = {}
    for c in rng.sample(CHANNELS, N):
        while True:
            x, y = rng.uniform(-R, R), rng.uniform(-R, R)
            if x * x + y * y <= R * R: break
        srcs[c] = dict(x=x, y=y, r=rng.uniform(1000.0, 1500.0))
    return dict(srcs=srcs, N=N, t=0.0, pos=(0.0, 0.0), ch=1, entered=False, t0=time.time())

def measure(arena, pos, ch):
    t = 0.0
    t += math.dist(arena["pos"], pos) / V
    if arena["ch"] != ch: t += T_SWITCH
    t += T_MEASURE
    arena["t"] += t; arena["pos"] = pos; arena["ch"] = ch
    s = arena["srcs"].get(ch)
    if s is None: return "no_signal", None
    d = math.dist(pos, (s["x"], s["y"]))
    if d > s["r"]: return "no_signal", None
    if d <= NEAR: return "near", None
    a = math.degrees(math.atan2(s["y"] - pos[1], s["x"] - pos[0])) % 360.0
    return "direction", round((a + _err(pos[0], pos[1])) % 360.0, 2)

def clear(arena, pos, ch):
    t = math.dist(arena["pos"], pos) / V
    s = arena["srcs"].get(ch)
    ok = s is not None and math.dist(pos, (s["x"], s["y"])) <= CLR
    t += (T_OPTICAL + T_CLEAR) if ok else T_OPTICAL
    arena["t"] += t; arena["pos"] = pos          # /clear 不切换频道
    if ok: del arena["srcs"][ch]
    return "success" if ok else "no_target_in_range"

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # 支持持久连接，避免本地端口被 TIME_WAIT 耗尽
    def log_message(self, *a): pass
    def _send(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def _bad(self, msg): self._send(400, {"error": msg})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try: body = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception: return self._bad("bad json")
        path = self.path
        if path not in ("/enter", "/measure", "/clear", "/exit"): return self._send(404, {"error": "unknown"})
        ar = STATE["arena"]
        rid = body.get("request_id")
        if not rid: return self._bad("missing request_id")
        # 幂等
        cache = STATE["idem"]
        key = json.dumps(body, sort_keys=True)      # 规范化后的请求体，用作幂等比对
        if rid in cache:
            old, resp = cache[rid]
            if old == key: return self._send(200, resp)
            return self._send(409, {"error": "request_id reused with different body"})
        def accept(resp):
            cache[rid] = (key, resp)
            self._send(200, resp)
        if path == "/enter":
            if ar["entered"]: return accept({"accepted": False, "real_timestamp_ms": int(time.time()*1000), "virtual_time_s": 0})
            ar["entered"] = True
            return accept({"accepted": True, "real_timestamp_ms": int(time.time()*1000), "virtual_time_s": 0.0,
                           "max_virtual_duration_s": 360000, "max_real_duration_s": 1200,
                           "remaining_real_duration_s": 1200})
        if not ar["entered"]: return accept({"accepted": False, "real_timestamp_ms": int(time.time()*1000), "virtual_time_s": 0})
        if path == "/exit":
            ar["entered"] = False
            return accept({"accepted": True, "real_timestamp_ms": int(time.time()*1000),
                           "virtual_time_s": round(ar["t"], 6), "exit_reason": "user_exit"})
        pos = body.get("position", {}); ch = body.get("channel")
        if ch is None or not (1 <= int(ch) <= 20): return self._bad("bad channel")
        p = (float(pos.get("x", 0.0)), float(pos.get("y", 0.0)))
        if path == "/measure":
            z, svd = measure(ar, p, int(ch))
            o = {"accepted": True, "real_timestamp_ms": int(time.time()*1000),
                 "virtual_time_s": round(ar["t"], 6), "measure_result": z}
            if z == "direction": o["svd_deg"] = svd
            return accept(o)
        if path == "/clear":
            r = clear(ar, p, int(ch))
            return accept({"accepted": True, "real_timestamp_ms": int(time.time()*1000),
                           "virtual_time_s": round(ar["t"], 6), "clear_result": r})

def serve(port, seed=None):
    STATE["arena"] = new_arena(seed); STATE["idem"] = {}
    return HTTPServer(("127.0.0.1", port), Handler)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 20260
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
    srv = serve(port, seed); print("mock simulator on http://127.0.0.1:%d" % port, flush=True)
    srv.serve_forever()
