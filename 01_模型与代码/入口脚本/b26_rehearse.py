# -*- coding: utf-8 -*-
"""预正式测试彩排：用 mock 完整走一遍"正式测试"的流程（含表 1 填写与日志导出）。"""
import json, os, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
import b26_official as O

PORT = 20330; D = os.path.dirname(os.path.abspath(__file__))
srv = M.serve(PORT, 1); threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.4)
cfg = O.load_cfg(); cfg["base_url"] = "http://127.0.0.1:%d" % PORT
cfg["log_dir"] = "_work_official"

print("=== 彩排开始：模拟三次正式测试 ===")
rows = []
for k, seed in enumerate((101, 102, 103), 1):
    M.STATE["arena"] = M.new_arena(seed); M.STATE["idem"] = {}
    out, log = O.run_official(cfg, verbose=False, tag="pre_test%d" % k)
    out["测试案例编码"] = "MOCK-%03d" % seed
    out["真值源数"] = M.STATE["arena"]["N"]
    rows.append(out)
    print(json.dumps({("测试%d" % k): out}, ensure_ascii=False))
srv.shutdown()

print("\n=== 表 1（问题3 正式测试结果）===")
print("%-14s %-14s %-20s %-16s" % ("测试案例编码", "清除干扰源个数", "平均定位清除时间(s)", "程序运行时间(s)"))
for r in rows:
    print("%-14s %-14s %-20s %-16s" % (r["测试案例编码"], r["清除干扰源个数"],
          r["平均定位清除时间_s"], r["程序运行时间_s"]))
print("\n=== 日志导出与体积 ===")
for r in rows:
    p = os.path.join(D, cfg["log_dir"], r["日志文件"])
    print("  %-28s %8.1f KB  （2MB 上限安全倍数 %.1f×）" % (r["日志文件"], os.path.getsize(p)/1024.0,
          2048.0/(os.path.getsize(p)/1024.0)))
json.dump(rows, open(os.path.join(D, "_work_b26_rehearsal.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n彩排结果已写入 _work_b26_rehearsal.json")
