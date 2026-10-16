# -*- coding: utf-8 -*-
import json, sqlite3, os
LOG = r"D:\BaiduNetdiskDownload\数学建模\04_CODE\_work_official\official_20260911_133821.jsonl"
recs = [json.loads(l) for l in open(LOG, encoding="utf-8")]
print("总记录数:", len(recs))
print("\n--- 前 3 条 ---")
for r in recs[:3]:
    print(json.dumps(r, ensure_ascii=False)[:900])
print("\n--- /enter 响应全文 ---")
ent = next((r for r in recs if r["path"] == "/enter"), None)
print(json.dumps(ent, ensure_ascii=False, indent=1) if ent else "NOT FOUND")
print("\n--- 最后 2 条 ---")
for r in recs[-2:]:
    print(json.dumps(r, ensure_ascii=False)[:900])
print("\n--- 时间戳跨度 ---")
ts = [r["response"].get("real_timestamp_ms") for r in recs if r.get("response")]
ts = [t for t in ts if isinstance(t, int)]
if ts:
    print("first=%d last=%d span=%.3f s" % (ts[0], ts[-1], (ts[-1]-ts[0])/1000.0))
print("\n--- sent_at 跨度 ---")
sa = [r["sent_at"] for r in recs if "sent_at" in r]
if sa:
    print("first=%.3f last=%.3f span=%.3f s" % (sa[0], sa[-1], sa[-1]-sa[0]))
print("\n--- exit ---")
ex = next((r for r in recs if r["path"] == "/exit"), None)
print(json.dumps(ex, ensure_ascii=False, indent=1) if ex else "NO /exit")
print("\n--- 路径统计 ---")
from collections import Counter
print(Counter(r["path"] for r in recs))
