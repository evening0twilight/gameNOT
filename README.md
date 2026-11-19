# 夜潮事务所

一支小型救援队在洪水中的城市值班 24 天。白天要判断机器预告、决定先救谁和怎样撤离。晚上可以休息、培养伙伴、安排下次出勤，也能把时间花在故事或社区。游戏支持简体中文、繁體中文和 English。

**2026-11-19 Windows 候选 p4release-20261119，正式发行暂缓。** 本轮修复从现场到营地的操作和读档问题，调整后续教学、战术预览和结局回看，复核三语剧情，并换入六首可循环的离线配乐。开发机已从新周目逐日运行到结局。用户已确认在 Windows 上完成本包实测。目标参考机量化指标与多人试玩仍待验收。

- [本轮改动与游戏画面](docs/p4-release-20261119/review.md) · [玩法和操作](docs/p4-release-20261119/guide.txt) · [五分钟配乐试听](outputs/p4release-20261119-audio-score.mp3)
- [八名伙伴与三条连续周目](docs/p4-release-20261119/campaign.md) · [96 节点剧情审读](docs/p4-release-20261119/story-review.md)
- [当前验收状态](docs/p4-release-20261119/release-status.md) · [Windows 参考机与试玩记录](docs/p4-release-20261119/windows-review.md) · [构建收据](docs/p4release-20261119-build.json)
- [开发入口与复现命令](docs/NEXT_AGENT_HANDOFF.md)。ZIP 保存在构建机，仓库保留同版本源码、素材与收据。

24张主线、12张支线、96节点、8固定人物。角色按主线结算加入；训练、约定、带教与接应使用真实项目、资源和任务贡献。三难度为从容、标准、严峻。存档runtime_revision=8兼容2–8；旧任务沿用原部署数值，不重发历史奖励。

当前版本使用 `python3 tools/check_product018.py --full --jobs 3 --report-prefix p4release-20261119` 检查，用 `python3 tools/build_windows_product018.py --candidate p4release-20261119 --review-dir docs/p4-release-20261119` 打包。新克隆也用默认检查，按[清理记录](docs/product018-cleanup.md)区分已移除的历史路径与意外缺失；现存受保护文件仍逐一校验。旧检查和打包入口只对应历史阶段。

旧报告、构建收据与冻结定稿保留。之前“整体实现完成”的结论已撤回；复查原始发现见 [复查记录](docs/baseline018-product-reassessment.txt)。本轮修正情况以新报告为准。2026-11-11用户授权将源码、素材与文档直接提交到远程 `main`；未发布商店或GitHub Release。

以下保留设计入口与历史阶段记录。

- [当前设计与验收手册](outputs/full-game-design.html)
- [开发前审查报告](outputs/predevelopment-review.html)
- [人物剧本全文](outputs/character-script-final.html)
- [唯一设计入口](game/data/final_design/design_manifest.json)
- [迁移校验记录](docs/migration-0.18.json)
- [技术决策与执行规范](docs/technical-decisions.txt)
- [运行时接口契约（待实现）](docs/contracts/runtime-v1.json)
- [技术准备验证记录](docs/technical-validation.json)
- [Windows 实机记录](docs/windows-test-record.json)
- [技术准备交接说明（历史）](docs/technical-setup-handoff.txt)

历史 P2：同一正式工程完成 M01–M06 / S01–S03、陈砚、训练与带教、第一章人物/关系故事和社区回访，并集成半写实人物与六地点场景素材。

- [P2 验证范围](docs/p2-validation.txt)
- [P2 构建与真实哈希](docs/p2-validation.json)
- [P2 Windows 实机待验证](docs/p2-windows-checklist.txt)

P1 Windows 已按用户报告通过；P2 新包的 Windows 实机、H01 新人试玩及美术验收独立待验证。以下 P1 记录保留为历史证据。

目录说明：

- `game/`：同一正式游戏工程、冻结设计数据、24日战役与界面实现。
- `work/`：离线设计验证工具、历史快照、本地引擎。`work/toolchain/`不纳入Git。
- `outputs/`：当前文档与验证证据，包含历史大体积推演记录；大于1MiB的既有JSON已作哈希校验压缩归档，原件可按需恢复，清理时只删除已校验的重复原件。

当前工程、0.18文档和回归依赖已迁入。旧位置仍保留382个未下载的历史研究网页、旧预览及引擎安装压缩包云端占位文件；它们不属于当前源码/回归依赖，明细记录在迁移报告中。本地可用的引擎本体已迁入并被Git忽略。

在仓库根目录验证迁移后的设计工具：

```sh
python3 work/predevelopment-review/verify.py
```

0.18文件中的`design_only`与“暂不开发”记录是审查当时的历史状态。最新授权和当前工作阶段见本README及交接说明；迁移不会为修改阶段标记而重写已冻结的设计证据。

历史技术准备检查：`python3 tools/check.py --engine`；只检查设计与参考规则时省略 `--engine`。通过 `GODOT` 指定锁定版本的引擎路径。Windows 构建：`python3 tools/build_windows.py`，缺模板先运行 `python3 tools/bootstrap.py templates`。

归档原件可用 `python3 tools/evidence.py` 从 `archives/evidence/` 恢复。冻结检查包含“运行时代码未变”断言，后续玩法实现用新检查入口；原0.18设计文件仍保留历史授权标记。

用户已确认 macOS 开发、Windows 11 x64／键鼠／简体中文首发，并已有 Windows 测试电脑。本机检查、跨平台导出和 Windows 实机验收分别记录；远程 CI 尚未运行。

Windows x64 导出已通过，全包模板SHA256与导出资源包独立启动已验证；Windows实机与性能仍待测。游戏源码中的空嵌套 Git 元数据已备份到忽略目录，当前由仓库根目录统一管理。

历史清理：已删除可恢复的大 JSON 原件及旧虚拟环境/预览缓存。检查会自动恢复所需归档；运行 `python3 tools/evidence.py --prune` 可在全量校验后再次清理重复原件。明细见 [清理记录](docs/history-cleanup.json)。

补充：[工程资料对照与硬件准备](docs/engineering-reference-review.txt)，包含官方/GDQuest/GitHub/Steamworks/社区skills的采纳记录及分层硬件验证计划。

Windows导出环境已补齐：[导出验证记录](docs/windows-export-validation.json)。用户已授权新对话开始P1，沿用本项目打通战斗→结算→营地→存读档→下一任务，见[交接说明](docs/p1-handoff.txt)。

当前开发状态（2026-11-04）：正式工程已接入 M01→结算→营地→存读档→M02 基础闭环。
当前检查：`python3 tools/check.py --engine`（1172项参考检查，明确排除2条历史源码冻结门禁）。
[P1验证与范围限制](docs/p1-development-validation.txt)。Windows构建入口仍为 `python3 tools/build_windows.py`。
本构建不是全部0.18规则/完整产品验收；未完成的专长、社会归因、撤销和Windows实机等见验证记录。

P1扩展已接入：首发三人的专长与成长被动、有向关系事件/具体承诺补救、双人协作及整组战术撤销。
[扩展验证、存档兼容与Windows实机清单](docs/p1-expanded-validation.txt)。旧基础版报告仅作为历史记录。
后续可视验证请运行 `Godot --path game --screen 1 --script tests/gui_external.gd`，该入口会确认并选择非主显示器。

2026-11-05：补录[正式界面与国际化计划](docs/ui-localization-plan.txt)。当前仍为工程UI；i18n此前未落实，以上是待实施计划，不是完成声明。

P1 视觉版：已接入首发三人立绘/棋子、渡轮与诊所材质、营地插画及动作反馈。范围与测试记录见 [视觉版记录](docs/p1-visual-validation.txt)，构建后运行 `python3 tools/package_p1.py` 生成 `build/night-tide-windows-p1-visual.zip`。
