# -*- coding: utf-8 -*-
"""只读查询模拟器机会账。"""
import sqlite3, os, json
BASE = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData"
for nm in ("formal-statistics-queue.sqlite3", "practice-statistics-queue.sqlite3"):
    p = os.path.join(BASE, nm)
    uri = "file:%s?mode=ro" % p.replace("\\", "/")
    try:
        con = sqlite3.connect(uri, uri=True, timeout=5)
        cur = con.cursor()
        tabs = [r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("### %s" % nm)
        print("   tables:", tabs)
        for t in tabs:
            n = cur.execute("SELECT COUNT(*) FROM \"%s\"" % t).fetchone()[0]
            print("   %-28s rows = %d" % (t, n))
            cols = [d[1] for d in cur.execute("PRAGMA table_info(\"%s\")" % t).fetchall()]
            print("      cols:", cols)
            for row in cur.execute("SELECT * FROM \"%s\" LIMIT 10" % t).fetchall():
                print("      ", row)
        con.close()
    except Exception as e:
        print("### %s  ERROR: %s" % (nm, e))
    print()
