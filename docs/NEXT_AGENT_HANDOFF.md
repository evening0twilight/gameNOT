# 接手入口：夜潮事务所 0.18

更新：2026-11-11（Asia/Singapore）。本文件用于没有聊天历史、通过 API key 账号接手的开发代理。先读本文件，随后按第 5 节继续。仓库：<https://github.com/evening0twilight/gameNOT>，当前用户明确要求直接提交/推送 `main`；本次没有创建其他项目或发布商店版本。

## 1. 用户的目标和不能重犯的问题

用户要按已经定稿的 **0.18 做完整最终游戏**。此前多次把“局部实现、跑通测试、有动画”称作完成，用户明确否定。人物获取、培养、关系、战术和剧情必须在同一周目里真实关联。不能以文件数量或测试通过证明玩法、美术、难度和易用性已经符合定稿。

现阶段是 **P4 产品对齐与最终验收收尾，仍未通过最终验收**。不是重新设计、另做演示，也不是直接进入发行。用户已有 Windows 电脑，并已报告验证过上一份 Windows 包；后续候选包仍由用户按约定实测，不再索要远程入口。没有使用 API 的运行时功能，现有游戏与素材不依赖任何模型账号或密钥。

用户授权把工程推到远程 main，并在验证 Windows 包后授权清理本机安装包和冗余文件。详见 [2026-11-11 清理记录](product018-cleanup.md)。游戏规则、剧本权威数据和运行素材未改。

## 2. 先读哪些文件，谁是权威

依次阅读：

1. `game/data/final_design/design_manifest.json` → 其 `authority` 指向的 `release_baseline.json`：唯一 0.18 权威。生成视图必须与其中 domains 一致，禁止改定稿来迎合现有实现。
2. `docs/product018-alignment.txt`：2026-11-07 产品修正，R01–R06、A–D的实际范围与局限。
3. `docs/product018-validation.txt`、`docs/product018-validation.json`、`docs/product018-build.json`：本轮证据、构建与未验收内容。
4. `docs/baseline018-product-reassessment.txt`：撤回过度完成声明时发现的缺口。保留了发现时的状态，不应把其“尚未修复”全部当作今天仍未修，也不能忽略它的关闭条件。
5. `docs/baseline018-alignment.txt/json`：更早的31项规则/保存修正。
6. `docs/product018-player-guide.txt`：玩家应实际走得通的玩法和操作流程。
7. `game/data/final_design/release_scope.json` 与 `acceptance.json`：产品清单和最终验收门槛，使用前核对 manifest 的生成视图映射。

README下半部、P1/P2/P3/P4旧报告、technical-setup-handoff、p1/p3-handoff中“当前阶段”“下一步”等属于历史记录；冲突时以本文件与冻结0.18为准。冻结文档里的 `design_only`/“暂不开发”是历史阶段标记，不撤销用户后来明确的开发授权。

## 3. 当前实际有什么

同一 Godot 工程 `game/`，GDScript、Compatibility，锁定 Godot `4.7.2.stable.official.ed1daf0bf`。Windows 11 x64、键鼠、简体中文；macOS为开发环境。

- 24日、24主线+12支线、96故事节点、8固定人物，三难度从容/标准/严峻；第24日终战后进入结局。
- 初始林岚/许舟/苏棠；M04/M07/M10/M13/M16结算后分别加入陈砚/叶禾/贺鸣/莫遥/江朔，失败不取消固定入队。
- 真实出勤草案、装备/后勤、训练/休息/治疗/带教、实际贡献、方向关系与具体保障、个人计划履约、接应改派、设施、世界与人物收束，共用正式状态/保存规则。
- 本轮新接入登场对话/下一次阵容选择、培养比较、城市事实与出发前真实地图预览、关系事件原因卡、逐页剧情/摘要选择、休养和来信呈现事实的持久化。来信不冒充共同经历或发亲近奖励。
- 有沿路径移动、转向、搬运、攻击/推撞、受击、施工、机器/目标反馈；动画暂停/跳过不再结算。6种音乐用途与独立音量；8人新服装/表情图集、8剧情背景、48图标。素材在仓库，不需要重新生成才能运行。
- `runtime_revision=8`，兼容2–8；旧在途任务保留部署数值，不补发奖励。

关键位置：

| 工作 | 入口 |
| --- | --- |
| UI/指令预览提交 | `game/scripts/app/main.gd`、`session.gd` |
| 人物/准备/培养/关系界面 | `game/scripts/presentation/campaign_screens.gd` |
| 人物叙事和逐页呈现 | `journey_presentation.gd`、`story_screen.gd`（同上目录） |
| 补充演出配置/来信/休养文本 | `game/data/presentation/character_journey.json` |
| 状态规则/获取/成长 | `game/scripts/domain/campaign_rules.gd`、`crew_journey.gd`、`chapter_one.gd`、`full_campaign.gd` |
| 剧情/缺席事实/评价 | `chapter_stories.gd`、`story_delivery.gd`、`appraisal.gd`（同上目录） |
| 保存/迁移 | `game/scripts/infrastructure/campaign_store.gd` |
| 棋盘/动作/声音/素材 | `game/scripts/presentation/tactical_board.gd`、`action_feedback.gd`、`audio_controller.gd`、`visual_assets.gd` |
| 本轮资源和来源 | `game/assets/product018/`、`docs/product018-image-prompts.json`、`product018-audio.json`、`product018-icons.json`、`asset-register.csv` |

## 4. 已有证据与准确边界

2026-11-07最后游戏源代码与构建收据哈希一致，2026-11-11清理前再次核对。以下保留原始证据；清理后复查单独记录在清理记录中。

- `outputs/product018-checks.json`：29组完整检查，加最后界面/本地化补查2组。36图×2环境×3难度=216条有限脚本路径，4条现场操作、4条世界路线、4种24日培养/轮换策略。
- `outputs/product018-crew-campaign.json`：真实获取/培养/轮换/逐日保存读取的24日周目，八人第一专长均实际使用。**不是八人所有第二专长的连续周目覆盖，也不是最优策略或真人平衡证明。**
- `outputs/baseline018-linked-campaign.json` 与 day06/day18/day24存档：真实共同贡献→陈砚带教，林岚计划兑现→独立职业方向，苏棠/江朔协商+两次贡献→支付2物资改派出口。
- `outputs/product018-story-coverage.json`：54人物/关系/生活节点的当面/休养/来信及选项呈现、保存、回看、奖励约束，共4161断言。另42社区/章节点由既有检查覆盖；没有完整逐页真人审读96节点，也未穷举所有人物组合。
- `outputs/product018-visual-review.json` 与 `product018-*.png`：隐藏原生根窗口，通过实际GPU SubViewport复查12幅1280×720界面/动作画面。`product018-movement.mp4`是实际已提交移动的渲染帧慢放、无音轨，**不是Windows实机或输入延迟证据**。
- 2026-11-07 Windows 包已按授权删除。清理前核对本机 ZIP 的 114470678 bytes 和 SHA256 `b88172277556b058b07b67fd39174521cfd16d567d65bbfc5bdd009c24a65a11`，与 [原构建收据](product018-build.json) 一致。
- 2026-11-11 用户报告 Windows 包已经验证过。没有随报告取得逐项测试记录、测试端包哈希或性能数据。原构建收据的 `windows_native_tested=false` 记录的是当时构建端未做原生测试；真人完整体验和 P4 最终验收仍未完成。

## 5. 下一步从这里继续：P4-018-01 剩余差异闭环

**接手后的第一项工作是对照0.18清单核查剩余产品差异，而不是重建核心框架、直接发行、再补几个动画后宣称完成。**

1. 建立逐项剩余项表（可以新建 `docs/p4-018-remaining.md`）：每项写权威字段、当前生产入口、实际玩家行为、证据、未满足部分和关闭条件。沿用R01–R06/A–D编号；已修项复核证据，发现回归再打开。
2. 优先核对已知仍不充分的内容：
   - 8人正/侧/三分之二设定、轮廓与96px辨识；当前是图集，并未交付完整独立三视设定板。服装图与表情特写分开显示，**不能声称已完成定稿要求的分层脸部复用成品**。核查后完成或取得用户对具体替代方案的明确认可，不能自行算作验收。
   - 初始3人的首次接触目前已在默认阵容，直接选择主要是保持阵容/查看档案；后加入人物可以替换下次阵容。检查是否真正满足“外形、说话方式、一次有用选择、日常反差”，不要把已读介绍当有用玩法选择。
   - 8人各等级专长的普通方案对比、可遇到的使用场景与机会成本；补缺失的实际玩法证据。既有首专长覆盖不能代替全部养成体验。
   - 96节点所有适用正常/重伤/离队/知情分支的实际台词与选择、身体动作、摘要和回看，特别是只做过规则覆盖的42节点。不要把“文本非空”当内容合格。
   - 12地点套件、敌人/居民/棋子、48图标的真实用途和辨识；核查按钮/引导、难度披露、夜间安排的信息负担。既有截图和资源数量只作线索。
3. 对确认的缺口直接在正式工程修复；按变化做相关规则/剧情/布局检查，并实际看对应界面。新截图优先使用正式连续周目存档，隔离夹具必须标明，不能灌经验后称真实成长。
4. 实现对齐后进入 **P4-018-02 Windows候选包与用户实测**：全量检查、导出新包、记录源代码与包哈希，按 `docs/baseline018-windows-checklist.txt` 请用户后续实测并记录问题。沿用用户已说好的方式，不再索要远程入口。
5. 最后 **P4-018-03 体验/性能/审美验收**：对照 `acceptance.json`，取得目标8GB机器1080p性能、冷启动/输入反馈、连续2小时内存、新人试玩、人物辨识和音乐听感的真实证据。未达到就继续修，缺证据就标待验收。全项具备才能关闭P4；未经授权不发布商店。

用户希望持续推进，不要每修一项就问要不要继续。不要用“完整战役可执行”替换“与定稿完整一致且验收通过”。必须需要用户的输入时，指出具体尚缺事实；可独立进行的实现继续做。

## 6. 新账号/新克隆如何启动

```sh
git clone https://github.com/evening0twilight/gameNOT.git
cd gameNOT
```

代码、运行资源、冻结设计、工具、压缩设计证据、当前与关键历史报告都在 Git。Windows 安装包不在 Git，本机旧包也已删除；需要时按下面命令生成新包。MP4、关键截图与构建收据仍在 Git。未创建 GitHub Release。

Linux（适合API代理/CI，无第三方Python包）：

```sh
python3 tools/bootstrap.py linux
python3 tools/bootstrap.py templates
export GODOT="$PWD/work/toolchain/linux/Godot_v4.7.2-stable_linux.x86_64"
python3 tools/check_product018.py --full
python3 tools/build_windows_product018.py
```

Windows PowerShell（Python已安装）：

```powershell
python tools/bootstrap.py windows
python tools/bootstrap.py templates
$env:GODOT = (Resolve-Path 'work/toolchain/windows/Godot_v4.7.2-stable_win64.exe').Path
python tools/check_product018.py --full
python tools/build_windows_product018.py
```

原 macOS 工作机：`/Users/a1-6/projects/person/gameNOT`；默认引擎为 `work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot`，已安装的 Windows 导出模板仍可离线使用。新 Mac 需自行准备锁定版本并使用 `GODOT` 指向可执行文件；bootstrap 当前没有 macOS 引擎下载目标。

默认检查应报告 244/287 个受保护路径已核验、43 个已按清理清单移除，`history.missing=[]`、`history.complete=false`。其中 36 张重复截图有受保护的同字节原图，原图缺失或损坏会报错；恢复旧路径时也必须通过原 SHA256。兼容参数 `--allow-missing-history` 仅可容许未记入清单且被 Git 排除的旧 ZIP/AVI 缺失；当前新克隆不需要它。

当前入口是 `check_product018.py` / `build_windows_product018.py`。旧 `check.py`、`build_windows.py`、baseline018、p4-tuning入口只对应历史阶段。CI已换到当前入口，仅PR和手动触发；**本次直接推main不自动运行CI，不能声称远程CI通过**。

全量检查会重写当前输出日志/周目记录；重建会覆盖当前product018包和收据。修改前保存必要旧证据，不覆盖冻结保护文件；新一轮产品验收应使用独立报告名。Godot源码变动后，构建要求与全量检查的源文件哈希一致。

图形检查：原工作机不要占用用户主显示器，曾指定的外屏目前不可假定存在。可用 `game/tests/product018_offscreen_review.gd`（隐藏根窗口的GPU截图）或先确认可用外屏；headless通过不等于视觉验收。无GPU环境只跑规则，把视觉验证明确留待有图形环境完成。

## 7. 可以直接交给下一位代理的指令

> 请接手这个仓库。先读 `docs/NEXT_AGENT_HANDOFF.md`，以冻结0.18为唯一设计权威，从第5节 P4-018-01 开始，核对并补齐剩余产品差异。已有完整战役候选包不代表最终验收完成。人物获取、养成、关系、剧情和玩法必须在正式存档中贯通。复用当前工程与资产，勿重做演示、改定稿或只靠测试宣布完成。先独立完成实现和本机验证，再按既定安排交Windows包给我测试。记录具体修改、证据、尚缺验收；不要重复索要Windows远程入口。
