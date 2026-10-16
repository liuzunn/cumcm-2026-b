# 04_CODE · 架构与模块依赖

> **冻结声明**：`b26/` 是**冻结包**，本整理轮**一字未改**。指纹见 `../05_EXPERIMENTS/results/_work_b26_manifest_v2.json`。
> **2026-09-11 更新**：补入 **Q4 模块**。Q4 冻结基线为 **5 个文件**（见 `../05_EXPERIMENTS/results/_work_b26_q4_manifest.json`），与 Q3 冻结包**分别冻结、互不覆盖**。
> **当前一致性**：Q3 11 文件 + Q4 5 文件在 2026-09-11 官方演练后复核 **0 处不符**。
> **目录平铺说明**：所有 `b26_*.py` 必须与 `b26/` **同级**，因为每个脚本都用 `sys.path.insert(0, dirname(__file__))` 定位包；把脚本放进子目录会导致 import 失败。这是**为了让代码可运行而保留的平铺结构**。

---

## 一、模块职责与依赖

`@text
                    ┌──────────────────────────────────────────┐
                    │              robot.py                     │
                    │  主控：搜索 → 发现 → 定位 → 移动 → 清除    │
                    │  （含活锁修复 + 进度驱动终止）              │
                    └───┬───────┬───────┬───────┬───────┬───────┘
                        │       │       │       │       │
              ┌─────────┘       │       │       │       └─────────┐
              ▼                 ▼       ▼       ▼                 ▼
        locate.py          detect.py  motion.py  search.py      path.py
        定位：楔形/         检测：三态   移动：      搜索：覆盖点    路径：最近
        半平面交/交集/      语义解析    虚拟时间账   + 覆盖证书      必做调度
        直径/可行域账本
              ▲                                                    │
              │                                                    │
              └────────────── select2.py ◄─────────────────────────┘
                             选点：5 种策略（当前只用 centroid）
                                       │
                                       ▼
                                  comm.py
                        通信：HTTP+JSON / 串行 / 幂等 / 重试 / 日志
                                       │
                                       ▼
                              （官方模拟器 或 b26_mock_server.py）
`@

| 模块 | 对外接口（被谁调用） | 单一职责 | 是否依赖其他模块 |
|---|---|---|---|
| `locate.py` | `Robot`（measure / 决策） | 只做几何，不知道模拟器存在 | 无 |
| `detect.py` | `Robot.measure` | 只做语义解析 | 无 |
| `motion.py` | `Robot` | 只记时间账 | 无 |
| `search.py` | `Robot.__init__`、入口脚本 | 覆盖点集 + 覆盖证书 | 无 |
| `path.py` | `Robot._run_adaptive` / `_run_fixed` | 只排序 | 无 |
| `select2.py` | `Robot._second_point` | 只选点 | `locate` |
| `comm.py` | `Robot` 全部动作 | 只收发 | 无 |
| `config.py` | 入口脚本 | 冻结配置（单一事实来源） | `search` |
| `robot.py` | 入口脚本 | **唯一做决策的地方** | 上述全部 |

**依赖方向**：`robot → {locate, detect, motion, search, path, select2, comm}`，**无循环依赖**。

---

## 二、主控内部结构

`Robot` 有三条执行路径：

| 方法 | 用途 | 说明 |
|---|---|---|
| `_run_fixed()` | 固定覆盖：先扫完覆盖点再清除 | D / E 方案 |
| `_run_adaptive()` | **自适应缺口驱动（G / F 方案）** | 覆盖点与"待清除/待复测目标"统一按最近必做调度 |
| `_refine_once()` | 对一个频道做一轮"选点 → 复测" | 被上述两者共用 |

**`_run_adaptive` 的四级决策链（活锁修复后）**：
1. 复测（有上限 `MAX_REFINE=4`）→ 2. 有限次清除尝试（`MAX_CLEAR_TRY=3`）→ 3. **铺网扫描清除**（可行域 ≤120 m 时，25 m 网格 + 投影，**可证明命中**）→ 4. **换一个没测过的探测点复测**（保证证据增长）。
**终止**：进度驱动（状态签名 = (已清除数, 已判空数, 累计观测数) 连续 40 步不变 ⇒ 判停滞并强制换点）；`HARD_CAP=3000` 仅作最后防线。

---

## 三、脚本清单

| 脚本 | 类别 | 作用 |
|---|---|---|
| `b26_mock_server.py` | 测试替身 | 自建 mock 模拟器（**不是官方**） |
| `b26_run.py` | 入口 | 快速试跑一局 |
| `b26_official.py` | 入口 | **官方接入：预检 + 运行 + 表 1 计算** |
| `b26_rehearse.py` | 入口 | 预正式测试彩排（3 局 + 表 1 + 日志） |
| `b26_protocol_tests.py` | 工具 | 协议一致性测试 11 条 |
| `b26_idcheck.py` | 工具 | request_id 唯一性核验 |
| `b26_freeze_manifest.py` | 工具 | 冻结指纹（SHA-256） |
| `b26_verify_fix.py` | 工具 | 修复后被卡死种子的定点验证 |
| `b26_gate2.py` | 工具 | 门禁 2：动作签名重复次数统计 |
| `b26_freeze.py` | 实验 | 复测（可配 36/100 局） |
| `b26_100.py` | 实验 | **100 局 × 4 臂配对实验** |
| `b26_compare.py` | 实验 | 覆盖方案四臂对照（8 局） |
| `b26_ab.py` | 实验 | 选点对照：基线 vs 动态（16 局） |
| `b26_ab3.py` | 实验 | 选点对照：基线 / 动态 / 动态含路程（16 局） |
| `b26_ab4.py` | 实验 | 选点对照：窄不确定集版本（16 局） |
| `official_config.json` | 配置 | **Q3** 官方接入参数（队号 **202606036029** 已填；COVER_9 / adaptive / centroid） |
| `official_config_q4.json` | 配置 | **Q4** 官方接入参数（队号已填；CERT_S51B / 51 点 / adaptive / `b26_q4.Robot4`） |
| `b26_q4_certificate.py` | **Q4 冻结** | 证书算子 + 自证套件 **S1—S6** |
| `b26_q4_verify.py` | **Q4 冻结** | 严格验证器（5 m 网格 + 近临界自适应细分 + Lipschitz 认证）+ 最少点数搜索 + T5-a 重算 |
| `b26_mock4.py` | **Q4 冻结** | Q4 定向源 mock + C-5/C-1 语义回归（**9/9 PASS**） |
| `b26_q4.py` | **Q4 冻结** | **Q4 控制器**（Stage B，已在官方环境 3 局验证） |
| `b26_q4exp.py` | **Q4 冻结** | E-Q4 实验矩阵运行器（616 局） |
| `Q4_MVP设计.md` | 设计 | Q4 设计稿 + 审计（66 KB，28 节 / 3 个 Gate / 12 条审计发现） |
| `b26_q4_official.py` | 入口 | **Q4 官方入口**（preflight + run_official + table1_row）；以 `b26_official.py` 为模板，静态 14/14、mock4 干跑 13/13 通过 |

---

## 四、冻结包文件指纹（v2）

| 文件 | SHA-256（前 16 位） |
|---|---|
| `b26/__init__.py` | `b67016a3d39c364a` |
| `b26/config.py` | `1b08897fb000e277` |
| `b26/locate.py` | `a03d3fe57d5f5cf1` |
| `b26/detect.py` | `d3e911baf0582742` |
| `b26/motion.py` | `dc1864b369dc9968` |
| `b26/search.py` | `bf22029809f7dcea` |
| `b26/path.py` | `314a4e604c23c4bd` |
| `b26/select2.py` | `ed36022093fea6d6` |
| `b26/comm.py` | `c5a44beddc1618d4` |
| `b26/robot.py` | `1763c34c7171e16b` |
| `b26_mock_server.py` | （v2 中已更新，见 manifest_v2） |

---

## 五、Q4 模块与依赖

`@text
                      ┌──────────────────────────────────────────┐
                      │        b26_q4.py  ·  Robot4（控制器）      │
                      │  状态机 + 最近必做调度 + β-free + 铺网兜底  │
                      └───┬────────┬────────┬────────┬───────────┘
                          │        │        │        │
              ┌───────────┘        │        │        └────────────┐
              ▼                    ▼        ▼                     ▼
   b26_q4_certificate.py    b26/locate.py  b26/comm.py   b26/search.py
   证书算子 + S1—S6 自证      楔形交 / 可行域   HTTP/JSON     COVER_9 覆盖
              │                                  │
              ▼                                  ▼
   b26_q4_verify.py                    （官方模拟器 或 b26_mock4.py）
   严格验证 + 最少点数搜索
              │
              ▼
   b26_q4exp.py  ← E-Q4 实验矩阵（616 局）
`@

| Q4 模块 | 职责 | 依赖 | 冻结 |
|---|---|---|---|
| `b26_q4_certificate.py` | 证书算子（E(S) 判据实现）+ 自证套件 S1—S6 | 无 | ✅ |
| `b26_q4_verify.py` | 严格认证（5 m × 1° 网格 + 自适应细分 + Lipschitz）+ 最少点数搜索 + T5-a 重算 | 证书算子 | ✅ |
| `b26_mock4.py` | 定向源语义 mock（扇区判定 / 三义 no_signal）+ C-5/C-1 回归 | 无（独立于 Q3 mock） | ✅ |
| `b26_q4.py` | **控制器**：51 点证书巡访 + 楔形交定位 + 凸集铺网兜底 + 进度驱动终止 | `b26/`（复用 Q3 冻结包） | ✅ |
| `b26_q4exp.py` | E-Q4 实验矩阵（B1—B6，616 局） | 控制器 + mock4 | ✅ |
| `b26_q4_official.py` | Q4 官方入口（preflight + run_official + table1_row） | `b26_q4`（控制器）、manifest（冻结核对） | ✅ 已建立（非冻结） |

> **Q4 复用 Q3 冻结包**：`b26_q4.py` 直接使用 `b26/locate.py`（楔形交）、`b26/comm.py`（通信）、`b26/search.py`（覆盖）。因此**改 Q3 冻结包同样会破坏 Q4 结论**。
