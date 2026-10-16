# -*- coding: utf-8 -*-
import json, collections
LOG = r"D:\BaiduNetdiskDownload\数学建模\04_CODE\_work_official_q4\q4official_20260911_134104.jsonl"
recs = [json.loads(l) for l in open(LOG, encoding="utf-8")]
print("总记录数:", len(recs))
print("路径统计:", dict(collections.Counter(r["path"] for r in recs)))
bad = [r for r in recs if r.get("http_status") != 200]
print("非 200 响应:", len(bad))
print("重试次数 >0 的记录:", len([r for r in recs if r.get("retry", 0) > 0]))
ids = [r["request_id"] for r in recs]
print("request_id 唯一数:", len(set(ids)), "/", len(ids))
ent = next(r for r in recs if r["path"] == "/enter")
print("enter:", json.dumps(ent["response"], ensure_ascii=False))
ex = next(r for r in recs if r["path"] == "/exit")
print("exit :", json.dumps(ex["response"], ensure_ascii=False))
ts = [r["response"].get("virtual_time_s") for r in recs if r.get("response")]
ts = [t for t in ts if isinstance(t, (int, float))]
print("虚拟时间: %.3f -> %.3f  (单调=%s)" % (ts[0], ts[-1], all(ts[i] <= ts[i+1] for i in range(len(ts)-1))))
cl = [r for r in recs if r["path"] == "/clear"]
succ = [r for r in cl if r["response"].get("clear_result") == "success"]
print("clear 调用 %d 次，成功 %d 次，失败 %d 次" % (len(cl), len(succ), len(cl)-len(succ)))
print("clear 频道:", sorted({r["request"]["channel"] for r in cl}))
ms = [r for r in recs if r["path"] == "/measure"]
print("measure 频道范围: %s .. %s" % (min(r["request"]["channel"] for r in ms), max(r["request"]["channel"] for r in ms)))
res = collections.Counter(r["response"].get("measure_result") for r in ms)
print("measure 结果分布:", dict(res))
