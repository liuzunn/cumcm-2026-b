# 文件迁移表 MIGRATION

> 本轮为**整理轮**：只移动、建目录、写索引，**未修改任何文件内容**。
> 完整机读版：`../05_EXPERIMENTS/_MIGRATION_RAW.json`（共 94 条）。

## 一、迁移汇总

| 目标目录 | 条目数 |
|---|---|
| `03_MODEL/` | 5 |
| `04_CODE/` | 18 |
| `05_EXPERIMENTS/` | 5 |
| `05_EXPERIMENTS/results/` | 15 |
| `05_EXPERIMENTS/figures/` | 2 |
| `05_EXPERIMENTS/logs/` | 5 |
| `05_EXPERIMENTS/logs/official/` | 10 |
| `05_EXPERIMENTS/scripts/` | 13 |
| `06_PROMPTS/` | 11 |
| `07_OFFICIAL/` | 1 |
| `09_ARCHIVE/历史诊断与中间版本/` | 9 |
| **合计** | **94** |

## 二、逐项迁移表

### → `03_MODEL/`（5 项）

| 原路径 | 现路径 |
|---|---|
| `2026B_创新设计报告.md` | `03_MODEL/2026B_创新设计报告.md` |
| `2026B_模型建立与求解报告.md` | `03_MODEL/2026B_模型建立与求解报告.md` |
| `2026B_模型选型报告.md` | `03_MODEL/2026B_模型选型报告.md` |
| `2026B_赛题分析报告.md` | `03_MODEL/2026B_赛题分析报告.md` |
| `2026B_问题1-2_定位模型与检测点优化.md` | `03_MODEL/2026B_问题1-2_定位模型与检测点优化.md` |

### → `04_CODE/`（18 项）

| 原路径 | 现路径 |
|---|---|
| `2026B_第五六阶段_代码与联调说明.md` | `04_CODE/2026B_第五六阶段_代码与联调说明.md` |
| `b26` | `04_CODE/b26` |
| `b26_100.py` | `04_CODE/b26_100.py` |
| `b26_ab.py` | `04_CODE/b26_ab.py` |
| `b26_ab3.py` | `04_CODE/b26_ab3.py` |
| `b26_ab4.py` | `04_CODE/b26_ab4.py` |
| `b26_compare.py` | `04_CODE/b26_compare.py` |
| `b26_freeze.py` | `04_CODE/b26_freeze.py` |
| `b26_freeze_manifest.py` | `04_CODE/b26_freeze_manifest.py` |
| `b26_gate2.py` | `04_CODE/b26_gate2.py` |
| `b26_idcheck.py` | `04_CODE/b26_idcheck.py` |
| `b26_mock_server.py` | `04_CODE/b26_mock_server.py` |
| `b26_official.py` | `04_CODE/b26_official.py` |
| `b26_protocol_tests.py` | `04_CODE/b26_protocol_tests.py` |
| `b26_rehearse.py` | `04_CODE/b26_rehearse.py` |
| `b26_run.py` | `04_CODE/b26_run.py` |
| `b26_verify_fix.py` | `04_CODE/b26_verify_fix.py` |
| `official_config.json` | `04_CODE/official_config.json` |

### → `05_EXPERIMENTS/`（5 项）

| 原路径 | 现路径 |
|---|---|
| `2026B_冻结与大规模复测报告.md` | `05_EXPERIMENTS/2026B_冻结与大规模复测报告.md` |
| `2026B_数据处理报告.md` | `05_EXPERIMENTS/2026B_数据处理报告.md` |
| `2026B_最小修复与同种子回归报告.md` | `05_EXPERIMENTS/2026B_最小修复与同种子回归报告.md` |
| `2026B_理论接入与对照实验报告.md` | `05_EXPERIMENTS/2026B_理论接入与对照实验报告.md` |
| `2026B_锁版与100局配对实验报告.md` | `05_EXPERIMENTS/2026B_锁版与100局配对实验报告.md` |

### → `05_EXPERIMENTS/results/`（15 项）

| 原路径 | 现路径 |
|---|---|
| `_work_b26_100.json` | `05_EXPERIMENTS/results/_work_b26_100.json` |
| `_work_b26_ab.json` | `05_EXPERIMENTS/results/_work_b26_ab.json` |
| `_work_b26_ab3.json` | `05_EXPERIMENTS/results/_work_b26_ab3.json` |
| `_work_b26_ab4.json` | `05_EXPERIMENTS/results/_work_b26_ab4.json` |
| `_work_b26_cmp.json` | `05_EXPERIMENTS/results/_work_b26_cmp.json` |
| `_work_b26_cmp_log.txt` | `05_EXPERIMENTS/results/_work_b26_cmp_log.txt` |
| `_work_b26_freeze.json` | `05_EXPERIMENTS/results/_work_b26_freeze.json` |
| `_work_b26_freeze.txt` | `05_EXPERIMENTS/results/_work_b26_freeze.txt` |
| `_work_b26_freeze_per.json` | `05_EXPERIMENTS/results/_work_b26_freeze_per.json` |
| `_work_b26_manifest.json` | `05_EXPERIMENTS/results/_work_b26_manifest.json` |
| `_work_b26_manifest_v2.json` | `05_EXPERIMENTS/results/_work_b26_manifest_v2.json` |
| `_work_b26_modes.json` | `05_EXPERIMENTS/results/_work_b26_modes.json` |
| `_work_b26_proto_tests.json` | `05_EXPERIMENTS/results/_work_b26_proto_tests.json` |
| `_work_b26_rehearsal.json` | `05_EXPERIMENTS/results/_work_b26_rehearsal.json` |
| `_work_b26_summary.json` | `05_EXPERIMENTS/results/_work_b26_summary.json` |

### → `05_EXPERIMENTS/figures/`（2 项）

| 原路径 | 现路径 |
|---|---|
| `_work_b26_locate.png` | `05_EXPERIMENTS/figures/_work_b26_locate.png` |
| `_work_b26_qc.png` | `05_EXPERIMENTS/figures/_work_b26_qc.png` |

### → `05_EXPERIMENTS/logs/`（5 项）

| 原路径 | 现路径 |
|---|---|
| `_work_b26_100_log.jsonl` | `05_EXPERIMENTS/logs/_work_b26_100_log.jsonl` |
| `_work_b26_cmp_log.jsonl` | `05_EXPERIMENTS/logs/_work_b26_cmp_log.jsonl` |
| `_work_b26_demo_log.jsonl` | `05_EXPERIMENTS/logs/_work_b26_demo_log.jsonl` |
| `_work_b26_freeze_log.jsonl` | `05_EXPERIMENTS/logs/_work_b26_freeze_log.jsonl` |
| `_work_b26_robot_log.jsonl` | `05_EXPERIMENTS/logs/_work_b26_robot_log.jsonl` |

### → `05_EXPERIMENTS/logs/official/`（10 项）

| 原路径 | 现路径 |
|---|---|
| `_work_official/_idcheck_1.jsonl` | `05_EXPERIMENTS/logs/official/_idcheck_1.jsonl` |
| `_work_official/_idcheck_100.jsonl` | `05_EXPERIMENTS/logs/official/_idcheck_100.jsonl` |
| `_work_official/_idcheck_25.jsonl` | `05_EXPERIMENTS/logs/official/_idcheck_25.jsonl` |
| `_work_official/_idcheck_50.jsonl` | `05_EXPERIMENTS/logs/official/_idcheck_50.jsonl` |
| `_work_official/_idcheck_75.jsonl` | `05_EXPERIMENTS/logs/official/_idcheck_75.jsonl` |
| `_work_official/_proto.jsonl` | `05_EXPERIMENTS/logs/official/_proto.jsonl` |
| `_work_official/pre_test1_20260910_204116.jsonl` | `05_EXPERIMENTS/logs/official/pre_test1_20260910_204116.jsonl` |
| `_work_official/pre_test1_20260910_204124.jsonl` | `05_EXPERIMENTS/logs/official/pre_test1_20260910_204124.jsonl` |
| `_work_official/pre_test2_20260910_204124.jsonl` | `05_EXPERIMENTS/logs/official/pre_test2_20260910_204124.jsonl` |
| `_work_official/pre_test3_20260910_204124.jsonl` | `05_EXPERIMENTS/logs/official/pre_test3_20260910_204124.jsonl` |

### → `05_EXPERIMENTS/scripts/`（13 项）

| 原路径 | 现路径 |
|---|---|
| `_work_b26_acct.py` | `05_EXPERIMENTS/scripts/_work_b26_acct.py` |
| `_work_b26_cover.py` | `05_EXPERIMENTS/scripts/_work_b26_cover.py` |
| `_work_b26_datagen.py` | `05_EXPERIMENTS/scripts/_work_b26_datagen.py` |
| `_work_b26_dir.py` | `05_EXPERIMENTS/scripts/_work_b26_dir.py` |
| `_work_b26_exp.py` | `05_EXPERIMENTS/scripts/_work_b26_exp.py` |
| `_work_b26_geom.py` | `05_EXPERIMENTS/scripts/_work_b26_geom.py` |
| `_work_b26_q1b.py` | `05_EXPERIMENTS/scripts/_work_b26_q1b.py` |
| `_work_b26_q1b4.py` | `05_EXPERIMENTS/scripts/_work_b26_q1b4.py` |
| `_work_b26_q2.py` | `05_EXPERIMENTS/scripts/_work_b26_q2.py` |
| `_work_b26_qc.py` | `05_EXPERIMENTS/scripts/_work_b26_qc.py` |
| `_work_b26_solve.py` | `05_EXPERIMENTS/scripts/_work_b26_solve.py` |
| `_work_b26_solve4.py` | `05_EXPERIMENTS/scripts/_work_b26_solve4.py` |
| `_work_b26_solve5.py` | `05_EXPERIMENTS/scripts/_work_b26_solve5.py` |

### → `06_PROMPTS/`（11 项）

| 原路径 | 现路径 |
|---|---|
| `2026B_各子问题建模提示词.md` | `06_PROMPTS/2026B_各子问题建模提示词.md` |
| `2026B_提示词_官方模拟器接入准备.md` | `06_PROMPTS/2026B_提示词_官方模拟器接入准备.md` |
| `2026B_提示词_最小修复与同种子回归.md` | `06_PROMPTS/2026B_提示词_最小修复与同种子回归.md` |
| `2026B_提示词_锁版与100局配对实验.md` | `06_PROMPTS/2026B_提示词_锁版与100局配对实验.md` |
| `2026B_提示词①_冻结方案与大规模复测.md` | `06_PROMPTS/2026B_提示词①_冻结方案与大规模复测.md` |
| `2026B_提示词③_理论接入与对照实验.md` | `06_PROMPTS/2026B_提示词③_理论接入与对照实验.md` |
| `2026B_第三阶段_创新设计提示词.md` | `06_PROMPTS/2026B_第三阶段_创新设计提示词.md` |
| `2026B_第五阶段_模型建立与求解提示词.md` | `06_PROMPTS/2026B_第五阶段_模型建立与求解提示词.md` |
| `2026B_第四阶段_数据处理提示词.md` | `06_PROMPTS/2026B_第四阶段_数据处理提示词.md` |
| `2026B_自用提示词.md` | `06_PROMPTS/2026B_自用提示词.md` |
| `2026B_问题1-2与实现_自用提示词.md` | `06_PROMPTS/2026B_问题1-2与实现_自用提示词.md` |

### → `07_OFFICIAL/`（1 项）

| 原路径 | 现路径 |
|---|---|
| `2026B_官方模拟器接入准备.md` | `07_OFFICIAL/2026B_官方模拟器接入准备.md` |

### → `09_ARCHIVE/历史诊断与中间版本/`（9 项）

| 原路径 | 现路径 |
|---|---|
| `_work_b26_q1b2.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_q1b2.py` |
| `_work_b26_q1b3.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_q1b3.py` |
| `_work_b26_runner.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_runner.py` |
| `_work_b26_runner2.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_runner2.py` |
| `_work_b26_runner3.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_runner3.py` |
| `_work_b26_runner4.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_runner4.py` |
| `_work_b26_solve2.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_solve2.py` |
| `_work_b26_solve3.py` | `09_ARCHIVE/历史诊断与中间版本/_work_b26_solve3.py` |
| `b26_diag.py` | `09_ARCHIVE/历史诊断与中间版本/b26_diag.py` |

## 三、未移动的文件（有意保留原位）

| 路径 | 原因 |
|---|---|
| `2026/` | 题目原件（PDF/DOCX），用户原始资料 |
| `数学建模竞赛知识库/` | 用户既有知识库（122 文件），只读引用 |
| `1992年-2025年数模国赛真题+优秀论文（按年份分类）/` | 用户原始资料 |
| `_work_extract/ 等 _work_* 目录` | 既有抽取/中间产物，本项目只读取 |
| `AI+数学建模提示词汇总！/、2026国赛论文写作模版/、备战资料/、统计建模大赛答辩PPT模板/` | 用户原始资料 |
| `.obsidian/` | 编辑器配置 |
