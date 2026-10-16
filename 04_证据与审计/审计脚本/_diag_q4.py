# -*- coding: utf-8 -*-
import sqlite3, json, os, glob
BASE = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData"
Q = os.path.join(BASE, "formal-statistics-queue.sqlite3")
con = sqlite3.connect("file:%s?mode=ro" % Q.replace("\\", "/"), uri=True, timeout=5)
cols = [d[1] for d in con.execute("PRAGMA table_info(statistics_tasks)").fetchall()]
rows = con.execute("SELECT * FROM statistics_tasks ORDER BY id").fetchall()
print("=== formal 队列共 %d 行 ===" % len(rows))
for r in rows:
    d = dict(zip(cols, r))
    print("  #%s  %s  cleared=%s  measure=%s  switch=%s  clearfail=%s  virt=%.3f s  prog=%s ms  end=%s"
          % (d["id"], d["schema_version"], d["cleared_jammer_count"], d["measure_accepted_count"],
             d["channel_switch_count"], d["clear_failure_count"],
             (d["virtual_time_us"] or 0)/1e6, d["program_run_duration_ms"], d["end_reason"]))
con.close()

print("\n=== behavior-logs 中的 formal-p4 文件 ===")
for p in sorted(glob.glob(os.path.join(BASE, "behavior-logs", "formal-p4*"))):
    print("  %-70s %8d B" % (os.path.basename(p), os.path.getsize(p)))
    if p.endswith(".result.json") or p.endswith("-attempt") or "attempt" in os.path.basename(p):
        print("     ", open(p, encoding="utf-8").read().strip())
