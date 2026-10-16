# -*- coding: utf-8 -*-
import sqlite3, json, os, re
Q = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData\formal-statistics-queue.sqlite3"
uri = "file:%s?mode=ro" % Q.replace("\\", "/")
con = sqlite3.connect(uri, uri=True, timeout=5)
cols = [d[1] for d in con.execute("PRAGMA table_info(statistics_tasks)").fetchall()]
rows = con.execute("SELECT * FROM statistics_tasks").fetchall()
print("=== formal-statistics-queue 共 %d 行 ===" % len(rows))
for r in rows:
    for c, v in zip(cols, r):
        print("  %-28s = %s" % (c, v))
    print("-" * 50)
con.close()

print("\n=== robot.py 中的 sleep / 节拍 ===")
for f in ("robot.py", "motion.py", "detect.py", "locate.py"):
    p = os.path.join(r"D:\BaiduNetdiskDownload\数学建模\04_CODE\b26", f)
    if not os.path.exists(p):
        continue
    src = open(p, encoding="utf-8").read()
    hits = [(i + 1, l.strip()) for i, l in enumerate(src.splitlines())
            if "sleep" in l or "pace" in l or "DETECT" in l or "MOVE_" in l]
    print("--- %s (%d 处) ---" % (f, len(hits)))
    for n, l in hits[:14]:
        print("   %4d: %s" % (n, l))

print("\n=== official_config.json ===")
print(open(r"D:\BaiduNetdiskDownload\数学建模\04_CODE\official_config.json", encoding="utf-8").read())
