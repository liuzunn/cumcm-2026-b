# 04_CODE · 运行说明

## 一、环境

- Python 3（本机为 Anaconda），需要 `numpy`、`matplotlib`（仅分析与绘图脚本需要）
- 无其他第三方依赖；通信使用标准库 `http.client`

## 二、常用命令（**必须在 `04_CODE/` 目录下执行**）

`@bash
cd 04_CODE

# ① 快速试跑一局（7 点覆盖，用于冒烟测试）
python b26_run.py 7 7

# ② 预正式测试彩排：3 局 + 自动生成表 1 + 导出日志
python b26_rehearse.py

# ③ 协议一致性测试（11 条）
python b26_protocol_tests.py

# ④ 官方接入预检（不消耗测试机会）
python -c "import b26_official as O,json; print(json.dumps(O.preflight(O.load_cfg()),ensure_ascii=False,indent=1))"

# ⑤ 门禁 2：动作签名重复次数
python b26_gate2.py

# ⑥ 冻结指纹
python b26_freeze_manifest.py

# —— Q4（离线 / mock）——
python b26_q4.py --selfcheck                 # Q4 证书自检（期望：最小裕量 28.314 度，合格 true）
python b26_q4.py --smoke --seeds 1,2,3,4,5   # Q4 控制器冒烟（非实验）
python b26_q4_certificate.py                 # 证书算子自证套件 S1—S6
python b26_q4_verify.py                      # 证书严格验证 + 最少点数搜索
python b26_mock4.py --timing                 # mock4 语义回归 C-5/C-1（9 项）
python b26_q4exp.py                          # E-Q4 实验矩阵（616 局，约 3 分钟）
`@

## 三、官方模拟器接入

1. 编辑 `official_config.json`，把 `robot_id` 改成**真实参赛队号**；
2. 确认 `base_url` = `http://127.0.0.1:2026`（官方默认端口）；
3. 启动官方模拟器并登录，等待界面显示接口就绪；
4. 在测试窗口内调用 `b26_official.run_official(cfg)` 或直接跑彩排脚本。

**正式测试流程与红线**见 `../07_OFFICIAL/操作手册.md`；**完整 12 步 SOP 与人工/自动边界**见 `../00_PROJECT/正式测试SOP与执行链.md`。

### 三之二、Q3 官方演练 / 正式测试命令（**已在官方环境验证**）

`@bash
cd 04_CODE
# ① 静态预检（不消耗任何机会）
python -c 'import b26_official as O, json; print(json.dumps(O.preflight(O.load_cfg()), ensure_ascii=False, indent=1))'
# ② 演练 / 正式运行（就绪后 5 分钟内执行）
python -c "import b26_official as O; out, log = O.run_official(O.load_cfg())"
# ③ 从日志算表 1 四列（正式测试后）
python -c "import b26_official as O, json; print(json.dumps(O.table1_row('日志路径.jsonl'), ensure_ascii=False))"
`@

> ✅ **2026-09-11 实测**：Q3 官方演练 1 局 → 清除 **14/14**，**145/145** 请求 HTTP 200 + accepted，**0 个 4xx/5xx**，0 重试，停滞/卡死 0/0。见 `../07_OFFICIAL/2026B_Q3_官方演练报告.md`。

### 三之三、Q4 官方入口

`@bash
cd 04_CODE
# ✅ 脚本已于 2026-09-11 建立（以 b26_official.py 为模板，不重构）
python b26_q4_official.py                 # 静态预检 14 项（不消耗机会）
python b26_q4_official.py --live          # 含端口/模拟器检查，共 16 项
python b26_q4_official.py --run --live    # ★ 仅在获得授权且窗口就绪后：预检通过才运行

# 或按 SOP 直接调用：
python -c "import b26_q4_official as M, json; out, log = M.run_official(M.load_cfg())"
`@

## 四、已知路径注意事项 **[待确认]**

| # | 事项 | 说明 |
|---|---|---|
| 1 | 脚本把输出写在**自身所在目录**（`dirname(__file__)`） | 从 `04_CODE/` 运行 ⇒ 新生成的日志/结果会落在 `04_CODE/`；**历史实验数据已归档到 `../05_EXPERIMENTS/`**，两者不要混淆 |
| 2 | `official_config.json` 的 `log_dir` 是相对路径 `_work_official` | 同上，会相对脚本目录解析 |
| 3 | 是否把输出目录改为指向 `../05_EXPERIMENTS/` | **本轮为"只整理不改动"，未修改任何脚本**；如需改动请新开一轮并记录到 DECISIONS |
| 4 | **Q3 自记日志命名歧义（R14）** | `run_official()` 默认 `tag="official"`，因此**演练**日志也命名为 `official_<时间戳>.jsonl`（如 `official_20260911_102332.jsonl`，实为 **演练**，`formal_index=null`）。**打包支撑材料时必须逐个核对 `formal_index`**，勿凭文件名判断 |

## 五、可运行性核验

本整理轮**移动后已做过冒烟测试**：从 `04_CODE/` 执行 `python b26_run.py 7 7`，
结果 **清除 12 / 源数 12，清除比例 1.0，虚拟总时间 6336.6 s**，与移动前一致 ⇒ **移动未破坏可运行性**。
（该次冒烟产生的日志已归档到 `../05_EXPERIMENTS/logs/_work_b26_robot_log.jsonl`。）
