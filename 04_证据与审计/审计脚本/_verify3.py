# -*- coding: utf-8 -*-
import sqlite3, json, os, glob, collections
BASE = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData"
Q = os.path.join(BASE, "formal-statistics-queue.sqlite3")
con = sqlite3.connect("file:%s?mode=ro" % Q.replace("\\", "/"), uri=True, timeout=5)
cols = [d[1] for d in con.execute("PRAGMA table_info(statistics_tasks)").fetchall()]
rows = con.execute("SELECT * FROM statistics_tasks ORDER BY id").fetchall()
print("=== formal 队列共 %d 行 ===" % len(rows))
for r in rows:
    d = dict(zip(cols, r))
    print("  #%s  cleared=%-3s measure=%-4s switch=%-4s clearfail=%s  virt=%9.3f s  prog=%s ms  end=%s"
          % (d["id"], d["cleared_jammer_count"], d["measure_accepted_count"], d["channel_switch_count"],
             d["clear_failure_count"], (d["virtual_time_us"] or 0)/1e6,
             d["program_run_duration_ms"], d["end_reason"]))
con.close()

print("\n=== 本次 Q3 官方文件 ===")
for p in sorted(glob.glob(os.path.join(BASE, "behavior-logs", "formal-p3*"))):
    print("  %-58s %8d B" % (os.path.basename(p), os.path.getsize(p)))
    if p.endswith(".result.json"):
        print("     ", open(p, encoding="utf-8").read().strip())

LOG = r"D:\BaiduNetdiskDownload\数学建模\04_CODE\_work_official\official_20260911_134257.jsonl"
recs = [json.loads(l) for l in open(LOG, encoding="utf-8")]
print("\n=== 自记日志核验 ===")
print("记录数 %d  %s" % (len(recs), dict(collections.Counter(r["path"] for r in recs))))
print("非 200:", len([r for r in recs if r.get("http_status") != 200]))
print("有重试:", len([r for r in recs if r.get("retry", 0) > 0]))
ids = [r["request_id"] for r in recs]
print("request_id 唯一: %d / %d" % (len(set(ids)), len(ids)))
ent = next(r for r in recs if r["path"] == "/enter")
print("enter remaining_real_duration_s =", ent["response"]["remaining_real_duration_s"])
ex = next(r for r in recs if r["path"] == "/exit")
print("exit_reason =", ex["response"]["exit_reason"], " virt = %.3f" % ex["response"]["virtual_time_s"])
ts = [r["response"].get("virtual_time_s") for r in recs if r.get("response")]
ts = [t for t in ts if isinstance(t, (int, float))]
print("虚拟时间单调:", all(ts[i] <= ts[i+1] for i in range(len(ts)-1)))
cl = [r for r in recs if r["path"] == "/clear"]
print("clear %d 次，成功 %d 次" % (len(cl), len([r for r in cl if r["response"].get("clear_result") == "success"])))
print("已清除频道:", sorted(r["request"]["channel"] for r in cl))
