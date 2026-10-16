# -*- coding: utf-8 -*-
"""模拟器通信模块：HTTP + JSON，串行、request_id 幂等、断线复用原 ID 重试、全量落盘日志。"""
import json, os, time, http.client
MAX_RETRY = 3

class Comm:
    """HTTP+JSON 客户端。使用**持久连接**：减少连接数与本地端口占用，
    这也是与官方模拟器长时间联调时更稳妥的做法。"""
    def __init__(self, base_url, robot_id, log_path):
        self.base = base_url.rstrip("/"); self.robot_id = robot_id
        u = self.base.split("//", 1)[-1]
        host, _, port = u.partition(":")
        self.host = host; self.port = int(port or 80)
        self.log_path = log_path; self.seq = 0; self.n_req = 0
        self._sent = {}          # request_id -> (payload, response)
        self._conn = None
        self._fh = open(log_path, "w", encoding="utf-8")
    def close(self):
        try:
            if self._conn: self._conn.close()
        except Exception: pass
        self._fh.close()
    def _next_id(self, tag):
        self.seq += 1
        return "%s-%d" % (tag, self.seq)
    def post(self, path, payload, request_id):
        """串行发送；网络异常时复用原 request_id 与原内容重试。"""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last = None
        for attempt in range(MAX_RETRY):
            t0 = time.time()
            try:
                if self._conn is None:
                    self._conn = http.client.HTTPConnection(self.host, self.port, timeout=5)
                self._conn.request("POST", path, body=body,
                                   headers={"Content-Type": "application/json"})
                r = self._conn.getresponse()
                code = r.status; data = json.loads(r.read().decode("utf-8"))
                self.n_req += 1
                self._log(dict(seq=self.seq, request_id=request_id, path=path,
                               http_status=code, sent_at=round(t0, 3),
                               request=payload, response=data, retry=attempt))
                if code != 200 or data.get("accepted") is not True:
                    raise RuntimeError("未执行：HTTP %s, accepted=%s" % (code, data.get("accepted")))
                return data
            except Exception as e:               # 连不上 / 未开放 / 业务拒绝
                last = e
                try:
                    if self._conn: self._conn.close()
                except Exception: pass
                self._conn = None
                time.sleep(0.05)
        raise RuntimeError("请求失败（已重试 %d 次）：%s" % (MAX_RETRY, last))
    def _log(self, rec):
        self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); self._fh.flush()
    # ---- 四条指令 ----
    def enter(self):
        rid = self._next_id("enter")
        p = dict(arena_id="default", robot_id=self.robot_id, request_id=rid)
        self._sent[rid] = (p, None)
        return self.post("/enter", p, rid)
    def measure(self, pos, channel):
        rid = self._next_id("measure")
        p = dict(arena_id="default", robot_id=self.robot_id, request_id=rid,
                 position=dict(x=float(pos[0]), y=float(pos[1])), channel=int(channel))
        return self.post("/measure", p, rid)
    def clear(self, pos, channel):
        rid = self._next_id("clear")
        p = dict(arena_id="default", robot_id=self.robot_id, request_id=rid,
                 position=dict(x=float(pos[0]), y=float(pos[1])), channel=int(channel))
        return self.post("/clear", p, rid)
    def exit(self):
        rid = self._next_id("exit")
        p = dict(arena_id="default", robot_id=self.robot_id, request_id=rid)
        return self.post("/exit", p, rid)
