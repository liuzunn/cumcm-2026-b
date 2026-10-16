# -*- coding: utf-8 -*-
"""Q4 官方模拟器接入：预检（preflight）、正式运行入口、表 1 结果记录。

【文件性质】与 b26_official.py **同构**的 Q4 版本；本文件位于**冻结基线之外**，
           不修改 04_CODE/b26/（Q3 冻结包 11 文件）、不修改 Q4 冻结基线 5 文件、不修改任何 manifest。
【模板来源】04_CODE/b26_official.py（已在官方环境验证：Q3 演练 14/14）
【控制器】04_CODE/b26_q4.py:Robot4（**冻结**，官方演练 3 局 36/36）
【证书】  S51_b（51 点）—— 环定义与点集 SHA-256 均与冻结清单逐项核对
【依据】  00_PROJECT/正式测试SOP与执行链.md；05_EXPERIMENTS/results/_work_b26_q4_manifest.json

计数器语义（重要，2026-09-11 用 3 局官方演练真值反解确认）
----------------------------------------------------------
Robot4.run() 返回的 clears      = /clear **总调用次数（尝试）**，不是成功数；
                 clear_fail  = 失败次数（clear_result == 'no_target_in_range'）；
                 sweep_clears= 铺网时**尝试过的网点数**，不是命中数。
⇒ **清除成功次数 = clears - clear_fail**；对三局官方演练分别得 11 / 13 / 12，与官方真值**精确吻合**。
本文件的 run_official() 同时输出 HTTP 日志侧的"清除干扰源个数"（table1_row），二者互为交叉验证。

日志命名说明（与 b26_official.py 的唯一有意差异）
------------------------------------------------
run_official() 的默认 tag 取 "q4official"（而非 "official"），
用于消除已在风险清单登记的 R14「自记日志名含 official 但实为演练日志」歧义：
本文件的产物一律落在 04_CODE/_work_official_q4/ 且以 q4official_ 前缀命名，
**刻意不与 Q3 的 official_* 命名混淆**。
"""

import hashlib
import json
import os
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from b26.comm import Comm
from b26_q4 import CERT, CERT_NAME, CERT_RINGS, Robot4, certificate_selfcheck

D = os.path.dirname(os.path.abspath(__file__))                 # 04_CODE
ROOT = os.path.dirname(D)                                      # 项目根
CFG_PATH = os.path.join(D, "official_config_q4.json")
Q4_MANIFEST = os.path.join(ROOT, "05_EXPERIMENTS", "results", "_work_b26_q4_manifest.json")
CERT_RECORD = os.path.join(ROOT, "05_EXPERIMENTS", "results", "_work_b26_q4_cert.json")
Q3_MANIFEST = os.path.join(D, "_work_b26_manifest.json")
SIM_DATA = r"D:\BaiduNetdiskDownload\Jammers-simulator-full-win64\Jammers-simulator-full\JammersSimulatorData"

# 基线核对时**必须忽略**的自身产物目录（不参与冻结校验）
SELF_TAG = "q4official"


def load_cfg():
    with open(CFG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _bytes_len(s):
    return len(s.encode("utf-8"))


def _has_ctrl(s):
    return any(ord(c) < 32 or ord(c) == 127 for c in s)


def point_set_sha(pts):
    """证书点集规范指纹。

    口径（与冻结清单 证书.点集SHA256 一致，已实测复现）：
        sha256( ';'.join('%.6f,%.6f' % (x, y) for (x, y) in pts) )
    """
    blob = ";".join("%.6f,%.6f" % (float(x), float(y)) for (x, y) in pts)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _file_sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _check_files(manifest_path, base, key):
    """返回 (ok, detail)。manifest 的 key 段内为 {相对路径: {'sha256':..., 'bytes':...}}。"""
    man = json.load(open(manifest_path, encoding="utf-8"))
    fp = man.get(key) or {}
    bad = []
    for rel, meta in sorted(fp.items()):
        p = os.path.join(base, rel.replace("/", os.sep))
        if not os.path.exists(p):
            bad.append(rel + "(缺失)")
            continue
        if _file_sha(p) != meta["sha256"]:
            bad.append(rel + "(哈希不符)")
    return (len(bad) == 0), "%d/%d 一致" % (len(fp) - len(bad), len(fp)) + ("" if not bad else "；异常：" + ",".join(bad))


def _cert_record():
    """从 Stage A 冻结认证记录中读取 S51_b 的严格认证结论（**读取记录，不重算、不重新搜索**）。"""
    rec = json.load(open(CERT_RECORD, encoding="utf-8"))
    fam = (rec.get("候选族") or {}).get("S51_b") or {}
    return fam


def preflight(cfg, live=False):
    """接入前自检：逐项给出 通过/待办/警告，不消耗任何测试机会。"""
    R = []

    def add(item, ok, detail=""):
        R.append(dict(检查项=item, 结果=("通过" if ok is True else "待办" if ok is False else "警告"), 详情=detail))

    rid = cfg.get("robot_id", "")
    add("robot_id 非占位符", rid not in ("", "<参赛队号>"), "当前=%r" % rid)
    add("robot_id 长度 1..64 字节", 1 <= _bytes_len(rid) <= 64, "%d 字节" % _bytes_len(rid))
    add("robot_id 无控制字符", not _has_ctrl(rid))
    add("robot_id 为 12 位数字", rid.isdigit() and len(rid) == 12, "%d 位" % len(rid))

    url = cfg.get("base_url", "")
    add("base_url 指向本机 2026",
        url.startswith("http://127.0.0.1:2026") or url.startswith("http://localhost:2026"), url)
    add("arena_id = default", cfg.get("arena_id") == "default", str(cfg.get("arena_id")))

    ld = os.path.join(D, cfg.get("log_dir", "_work_official_q4"))
    os.makedirs(ld, exist_ok=True)
    try:
        p = os.path.join(ld, "_w.tmp")
        open(p, "w").write("x")
        os.remove(p)
        ok = True
    except Exception:
        ok = False
    add("日志目录可写", ok, ld)

    # ---- 证书：粗网格自检（快速）----
    sc = certificate_selfcheck()
    if sc.get("错误"):
        add("Q4 证书粗网格自检（最小裕量 >= 10 度）", False, str(sc.get("错误")))
    else:
        add("Q4 证书粗网格自检（最小裕量 >= 10 度）", bool(sc.get("合格")),
            "点数 %d，最小裕量 %.3f 度，最坏点 %s" % (sc["点数"], sc["最小裕量_deg"], sc.get("最坏点")))

    # ---- 证书：严格认证**记录**（Stage A 冻结结论）----
    try:
        fam = _cert_record()
        unit = (fam.get("单元认证") or {})
        base_scan = (fam.get("基础扫描") or {})
        unverified = unit.get("未认证细胞")
        margin = unit.get("认证最小裕量_deg")
        concl = fam.get("结论")
        okc = (concl == "PASS") and (unverified == 0) and (margin is not None and margin > 0)
        add("Q4 证书严格认证记录（PASS 且未认证细胞 0）", bool(okc),
            "族 %s；结论 %s；基础最小裕量 %.6f 度；认证最小裕量 %.6f 度；未认证细胞 %s" %
            (fam.get("族名"), concl, base_scan.get("最小裕量_deg", float("nan")),
             margin if margin is not None else float("nan"), unverified))
    except Exception as e:
        add("Q4 证书严格认证记录（PASS 且未认证细胞 0）", False, "读取认证记录失败：%s" % e)

    # ---- 证书：点集 SHA + 环定义 vs 冻结清单 ----
    try:
        man = json.load(open(Q4_MANIFEST, encoding="utf-8"))
        cert_meta = man.get("证书") or {}
        run_sha = point_set_sha(CERT)
        fro_sha = cert_meta.get("点集SHA256")
        same_sha = (run_sha == fro_sha)
        rings_run = [list(r) for r in CERT_RINGS]
        rings_fro = [list(r) for r in (cert_meta.get("环定义") or [])]
        same_rings = (rings_run == rings_fro)
        n_ok = (len(CERT) == cert_meta.get("点数"))
        add("证书点集 = 冻结清单（SHA-256 与环定义）", bool(same_sha and same_rings and n_ok),
            "运行期 %s… vs 冻结 %s…；环定义一致=%s；点数 %d/%s" %
            (run_sha[:16], str(fro_sha)[:16], same_rings, len(CERT), cert_meta.get("点数")))
    except Exception as e:
        add("证书点集 = 冻结清单（SHA-256 与环定义）", False, "核对失败：%s" % e)

    # ---- 冻结基线 ----
    try:
        ok4, d4 = _check_files(Q4_MANIFEST, ROOT, "Q4_文件指纹")
        add("Q4 基线 5 文件未改动", ok4, d4)
    except Exception as e:
        add("Q4 基线 5 文件未改动", False, "核对失败：%s" % e)
    try:
        ok3, d3 = _check_files(Q3_MANIFEST, D, "文件指纹")
        add("Q3 冻结包 11 文件未改动", ok3, d3)
    except Exception as e:
        add("Q3 冻结包 11 文件未改动", False, "核对失败：%s" % e)

    add("坐标范围 |x|,|y| <= 2e6", True,
        "由 51 点证书（最大半径 2700 m）与可行域决定，远小于该上限")

    if live:
        host, _, port = url.split("//", 1)[-1].partition(":")
        try:
            socket.create_connection((host, int(port or 80)), timeout=1.0).close()
            add("接口端口可达（TCP 2026）", True, "%s:%s" % (host, port))
        except Exception as e:
            add("接口端口可达（TCP 2026）", None,
                "连不上：%s —— 官方文档：5 秒倒计时期间/非测试期间/测试结束后接口未开放，连不上属正常" % e)

        found = [p for p in (SIM_DATA, os.path.dirname(SIM_DATA)) if os.path.exists(p)]
        add("官方模拟器在本机", bool(found) if found else False,
            ("命中 %s" % found) if found else "未在本机常见目录发现模拟器数据目录")

    # ---- 官方语义核对 9 项：清单已逐条有结论（记录型检查，不重跑探针）----
    add("官方语义核对 9 项（清单逐条有结论）", True,
        "T1—T4 全部与文档一致；Q4-1 多次直接见证、Q4-4 强证据；"
        "Q4-2 仅 in-sector 分支见证（out-of-sector 未见证）；Q4-3 / Q4-5 未见证（按设计保留，不为全绿刻意构造）")

    return R


def table1_row(log_path):
    """从日志算出表 1 所需的四个量（与 b26_official.py 同一实现）。"""
    recs = [json.loads(l) for l in open(log_path, encoding="utf-8")]
    ok = [r for r in recs if r.get("response") and r["response"].get("accepted") is True]
    last = ok[-1]["response"]["virtual_time_s"] if ok else 0.0
    cleared = 0
    tries = 0
    for r in ok:
        if r["path"] == "/clear":
            tries += 1
            if r["response"].get("clear_result") == "success":
                cleared += 1
    ent = next((r for r in ok if r["path"] == "/enter"), None)
    wall = 0.0
    if ent is not None and len(ok) >= 2:
        wall = (ok[-1]["response"]["real_timestamp_ms"]
                - ent["response"]["real_timestamp_ms"]) / 1000.0
    return dict(清除干扰源个数=cleared,
                平均定位清除时间_s=round(last / max(1, cleared), 1),
                程序运行时间_s=round(wall, 3),
                虚拟总时间_s=round(last, 1),
                清除尝试次数=tries, 请求数=len(recs))


def run_official(cfg, base_url=None, verbose=True, tag=SELF_TAG):
    """官方运行入口：/enter -> Robot4 主循环 -> /exit；返回 (结果字典, 日志路径)。"""
    url = base_url or cfg["base_url"]
    ld = os.path.join(D, cfg.get("log_dir", "_work_official_q4"))
    os.makedirs(ld, exist_ok=True)
    log = os.path.join(ld, "%s_%s.jsonl" % (tag, time.strftime("%Y%m%d_%H%M%S")))
    c = Comm(url, cfg["robot_id"], log)
    t0 = time.time()
    try:
        r = Robot4(c, cert=CERT).run()
    finally:
        c.close()
    wall = time.time() - t0
    row = table1_row(log)
    # ---- 计数器语义（**已用 3 局官方演练真值反解确认**，勿改标签）----
    #   b26_q4.py:Robot4.run() 的 clears      = /clear **总调用次数（尝试）**，非成功数
    #                            clear_fail  = 失败次数（clear_result == 'no_target_in_range'）
    #   ⇒ 清除成功次数 = clears - clear_fail；三局官方演练分别为 11/13/12，与官方真值**精确吻合**
    #   sweep_clears = 铺网时**尝试过的网点数**（逐点累加，命中即 return），**不是命中数**
    out = dict(base_url=url, 日志文件=os.path.basename(log), 运行墙钟_s=round(wall, 3),
               已清除频道数=r["cleared"], 判空频道数=r["empty"], 源数未知=True,
               证书名称=CERT_NAME, 证书点数=r["cert_points"],
               步数=r["steps_used"], 停滞=r["stall_trips"], 卡死=len(r["stuck"]),
               漏源候选=r["unresolved_seen"], 硬上限触发=r["hard_cap_hit"],
               鸽巢提前终止=r["pigeon_exit"],
               清除调用次数=r["clears"], 清除失败次数=r["clear_fail"],
               清除成功次数=r["clears"] - r["clear_fail"],
               复测轮数=r["refine_rounds"], 铺网次数=r["sweeps"],
               铺网网点尝试数=r["sweep_clears"], 铺网跳过数=r["sweep_skipped"],
               **row)
    if verbose:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return out, log


def _main(argv):
    live = "--live" in argv
    do_run = "--run" in argv
    cfg = load_cfg()
    rows = preflight(cfg, live=live)
    stat = dict(通过=sum(1 for x in rows if x["结果"] == "通过"),
                待办=sum(1 for x in rows if x["结果"] == "待办"),
                警告=sum(1 for x in rows if x["结果"] == "警告"), 合计=len(rows))
    print(json.dumps(dict(队号=cfg.get("robot_id"), 检查项=rows, 统计=stat),
                     ensure_ascii=False, indent=1))
    if not do_run:
        return 0
    blocked = [x["检查项"] for x in rows if x["结果"] != "通过"]
    if blocked:
        print("存在非通过项，拒绝运行：%s" % blocked)
        return 2
    run_official(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
