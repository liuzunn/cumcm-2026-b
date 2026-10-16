# -*- coding: utf-8 -*-
import sqlite3, os, glob, json
BASE = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData"
Q = os.path.join(BASE, "formal-statistics-queue.sqlite3")
con = sqlite3.connect("file:%s?mode=ro" % Q.replace("\\", "/"), uri=True, timeout=5)
cols = [d[1] for d in con.execute("PRAGMA table_info(statistics_tasks)").fetchall()]
rows = con.execute("SELECT * FROM statistics_tasks ORDER BY id").fetchall()
print("formal 队列 = %d 行" % len(rows))
print("state 全 confirmed:", all(dict(zip(cols, r))["state"] == "confirmed" for r in rows))
print("end_reason 全 user_exit:", all(dict(zip(cols, r))["end_reason"] == "user_exit" for r in rows))
con.close()
p = os.path.join(BASE, "practice-statistics-queue.sqlite3")
c2 = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True, timeout=5)
print("practice 队列 = %d 行（未变）" % c2.execute("SELECT COUNT(*) FROM practice_statistics_tasks").fetchone()[0])
c2.close()

print("\n=== 六份加密日志 ===")
tot = 0
for pat in ("formal-p3-*", "formal-p4-*"):
    for f in sorted(glob.glob(os.path.join(BASE, "behavior-logs", pat))):
        if f.endswith(".jlog"):
            n = os.path.getsize(f); tot += n
            print("  %-52s %8d B" % (os.path.basename(f), n))
print("  合计 %.1f KB（单份上限 2 MB）" % (tot/1024))

print("\n=== 六份官方 result.json ===")
for pat in ("formal-p3-*", "formal-p4-*"):
    for f in sorted(glob.glob(os.path.join(BASE, "behavior-logs", pat))):
        if f.endswith(".result.json"):
            d = json.load(open(f, encoding="utf-8"))
            print("  p%s  formal_index=%s  %s" % (d["problem_no"], d["formal_index"], d["case_code"]))
