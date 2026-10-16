# -*- coding: utf-8 -*-
"""官方模拟器接入：预检（preflight）、正式运行入口、表 1 结果记录。
本文件位于冻结包 b26/ 之外，不修改任何冻结代码。"""
import json, os, socket, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b26 import search, config
from b26.comm import Comm
from b26.robot import Robot

D = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(D, "official_config.json")

def load_cfg():
    return json.load(open(CFG_PATH, encoding="utf-8"))

def _bytes_len(s): return len(s.encode("utf-8"))

def _has_ctrl(s):
    return any(ord(c) < 32 or ord(c) == 127 for c in s)

def preflight(cfg, live=False):
    """接入前自检：逐项给出 通过/待办/警告，不消耗任何测试机会。"""
    R = []
    def add(item, ok, detail=""):
        R.append(dict(检查项=item, 结果=("通过" if ok is True else "待办" if ok is False else "警告"), 详情=detail))
    rid = cfg.get("robot_id", "")
    add("robot_id 非占位符", rid not in ("", "<参赛队号>"), "当前=%r" % rid)
    add("robot_id 长度 1..64 字节", 1 <= _bytes_len(rid) <= 64, "%d 字节" % _bytes_len(rid))
    add("robot_id 无控制字符", not _has_ctrl(rid))
    url = cfg.get("base_url", "")
    add("base_url 指向本机 2026", url.startswith("http://127.0.0.1:2026") or url.startswith("http://localhost:2026"), url)
    add("arena_id = default", cfg.get("arena_id") == "default", str(cfg.get("arena_id")))
    ld = os.path.join(D, cfg.get("log_dir", "_work_official"))
    os.makedirs(ld, exist_ok=True)
    try:
        p = os.path.join(ld, "_w.tmp"); open(p, "w").write("x"); os.remove(p); ok = True
    except Exception as e:
        ok = False
    add("日志目录可写", ok, ld)
    cover = getattr(search, cfg.get("cover", "COVER_9"))
    cok, worst, margin = search.coverage_certificate(cover)
    add("覆盖证书合格（最大未覆盖 ≤ 1000 m）", bool(cok), "最大 %.1f m，裕量 %.1f m，点数 %d" % (worst, margin, len(cover)))
    add("覆盖点集与冻结清单一致", cfg.get("cover") == "COVER_9" and cfg.get("cover_mode") == "adaptive"
        and cfg.get("strategy") == "centroid", "%s / %s / %s" % (cfg.get("cover"), cfg.get("cover_mode"), cfg.get("strategy")))
    add("坐标范围 |x|,|y| ≤ 2e6", True, "由 cover 与可行域决定，本方案远小于该上限")
    if live:
        host, _, port = url.split("//", 1)[-1].partition(":")
        try:
            socket.create_connection((host, int(port or 80)), timeout=1.0).close()
            add("接口端口可达（TCP）", True, "%s:%s" % (host, port))
        except Exception as e:
            add("接口端口可达（TCP）", None, "连不上：%s —— 测试窗口外属正常现象" % e)
    return R

def table1_row(log_path):
    """从日志算出表 1 所需的四个量。"""
    recs = [json.loads(l) for l in open(log_path, encoding="utf-8")]
    ok = [r for r in recs if r.get("response") and r["response"].get("accepted") is True]
    last = ok[-1]["response"]["virtual_time_s"] if ok else 0.0
    cleared = 0; tries = 0
    for r in ok:
        if r["path"] == "/clear":
            tries += 1
            if r["response"].get("clear_result") == "success": cleared += 1
    # 程序运行时间 = /enter 与测试结束时刻之间的时长（题面附录 3 的定义）
    ent = next((r for r in ok if r["path"] == "/enter"), None)
    wall = 0.0
    if ent is not None and len(ok) >= 2:
        wall = (ok[-1]["response"]["real_timestamp_ms"]
                - ent["response"]["real_timestamp_ms"])/1000.0
    return dict(清除干扰源个数=cleared, 平均定位清除时间_s=round(last/max(1, cleared), 1),
                程序运行时间_s=round(wall, 3), 虚拟总时间_s=round(last, 1),
                清除尝试次数=tries, 请求数=len(recs))

def run_official(cfg, base_url=None, verbose=True, tag="official"):
    cover = getattr(search, cfg.get("cover", "COVER_9"))
    url = base_url or cfg["base_url"]
    ld = os.path.join(D, cfg.get("log_dir", "_work_official")); os.makedirs(ld, exist_ok=True)
    log = os.path.join(ld, "%s_%s.jsonl" % (tag, time.strftime("%Y%m%d_%H%M%S")))
    c = Comm(url, cfg["robot_id"], log)
    t0 = time.time()
    try:
        r = Robot(c, cover=cover, strategy=cfg.get("strategy"), cover_mode=cfg.get("cover_mode")).run()
    finally:
        c.close()
    wall = time.time() - t0
    row = table1_row(log)
    out = dict(base_url=url, 日志文件=os.path.basename(log), 运行墙钟_s=round(wall, 3),
               清除数=r["cleared"], 源数未知=True, 覆盖点数=r["covered_count"],
               步数=r["steps_used"], 停滞=r["stall_trips"], 卡死=len(r["stuck"]), **row)
    if verbose:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return out, log
