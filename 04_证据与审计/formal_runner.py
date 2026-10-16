# -*- coding: utf-8 -*-
"""正式测试自动接管器（SOP 第 4-7 步 + 第 9-11 步）。
⛔ 本脚本【不执行】SOP 第 1/2/3 步（启动、登录、点「正式测试」）—— 那三步必须人工。
用法：
    python _teach/formal_runner.py --problem 3 --wait      # 布好监听，就绪即自动接管
    python _teach/formal_runner.py --problem 4 --wait
"""
import argparse, http.client, json, os, sqlite3, sys, time, datetime

PROJ = r"D:\BaiduNetdiskDownload\数学建模"
CODE = os.path.join(PROJ, "04_CODE")
sys.path.insert(0, CODE)
QUEUE = (r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full"
         r"\JammersSimulatorData\formal-statistics-queue.sqlite3")
HOST, PORT = "127.0.0.1", 2026


def queue_rows():
    uri = "file:%s?mode=ro" % QUEUE.replace("\\", "/")
    try:
        con = sqlite3.connect(uri, uri=True, timeout=5)
        n = con.execute("SELECT COUNT(*) FROM statistics_tasks").fetchone()[0]
        con.close()
        return n
    except Exception as e:
        return "ERR:%s" % e


def stamp():
    return datetime.datetime.now().strftime("%H:%M:%S")


def probe():
    """就绪探针：arena_id 非法 -> 协议上永不执行、不改状态。"""
    body = json.dumps(dict(arena_id="__ready_probe__", robot_id="202606036029",
                           request_id="ready-probe"), ensure_ascii=False).encode("utf-8")
    c = http.client.HTTPConnection(HOST, PORT, timeout=3)
    try:
        c.request("POST", "/enter", body=body,
                  headers={"Content-Type": "application/json"})
        r = c.getresponse()
        code = r.status
        data = json.loads(r.read().decode("utf-8"))
    finally:
        try: c.close()
        except Exception: pass
    return (code == 200 and data.get("accepted") is False), code, data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", type=int, choices=[3, 4], required=True)
    ap.add_argument("--wait", action="store_true", help="轮询等待接口就绪后再接管")
    ap.add_argument("--timeout", type=int, default=1800, help="等待就绪的上限秒数")
    a = ap.parse_args()

    n0 = queue_rows()
    print("[%s] problem=%d  起始 formal 队列行数 = %s" % (stamp(), a.problem, n0), flush=True)

    if a.wait:
        t0 = time.time(); tick = 0
        while time.time() - t0 < a.timeout:
            try:
                ok, code, data = probe()
            except Exception:
                ok = False
            tick += 1
            if ok:
                print("[%s] 接口已就绪（探针 HTTP %d, accepted=false）—— 立即接管" %
                      (stamp(), code), flush=True)
                break
            if tick % 15 == 1:
                print("[%s] 等待窗口就绪 ... %ds" % (stamp(), int(time.time() - t0)), flush=True)
            time.sleep(2)
        else:
            print("[%s] 超时未就绪，退出（未消耗任何机会）" % stamp(), flush=True)
            return 2

    # ---- SOP 第 5/6/7 步：控制器内自动完成 /enter -> 主循环 -> /exit ----
    print("[%s] 启动控制器 ..." % stamp(), flush=True)
    if a.problem == 3:
        import b26_official as M
    else:
        import b26_q4_official as M
    t1 = time.time()
    out, log = M.run_official(M.load_cfg())
    wall = time.time() - t1
    print("[%s] 控制器结束，墙钟 %.1f s" % (stamp(), wall), flush=True)
    print("RESULT_JSON " + json.dumps(out, ensure_ascii=False), flush=True)

    n1 = queue_rows()
    print("[%s] 结束 formal 队列行数 = %s（新增 %s）" %
          (stamp(), n1, (n1 - n0) if isinstance(n1, int) and isinstance(n0, int) else "?"),
          flush=True)
    print("[%s] 日志 = %s" % (stamp(), log), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
