# 接手入口：夜潮事务所 0.18

更新：2026-11-19（Asia/Singapore）。仓库：https://github.com/evening0twilight/gameNOT 。用户已授权直接提交/推送 main；不发布商店版本。先读本文件，再看本轮差异表和冻结设计。

## 当前进度（优先于下方历史记录）


本次为 `p4release-20261119`。发行判断为 **NO-GO**。请先看[逐项验收](p4-release-20261119/validation.md)、[本轮状态](p4-release-20261119/release-status.md)及[正式战役中的角色选择](p4-release-20261119/campaign.md)。第 5 节列出新的复现入口。冻结基线和存档版本仍为 0.18 与 8。

本机交付包为 `build/night-tide-0.18-p4release-20261119-windows.zip`，157843219 bytes，SHA256 `72a0c0e9457f43ce922e95d5df117c42de5914ed67096761372f4f6782f5dbf4`。[构建收据](p4release-20261119-build.json)对应48组统一检查与499个生产文件。[证据索引](p4-release-20261119/evidence-index.json)把最终截图、存档、验具、实包验证和 Mac 计时绑定到同一候选。20份旧通用输出已恢复原字节，新生成内容保存在独立前缀。Windows 与真人验收仍开放。

### 2026-11-17 营地返修（历史）

2026-11-17 最新营地引导返修见 `docs/p4-campguide-20261117/review.md`、`validation.md`。新周目第2晚故事、第3晚已有装备、第4晚配队；结束第4晚才保存基础教程完成，第5天起仍保留现场逐项教学。营地采购逐件、设施逐处，带教看真实资格，证据/公开/路线各自独立；限时支援与第23晚优先提示。旧档无camp_lessons时保留原入口，不强制重学。冻结设计、角色/资源/经验和runtime_revision=8未改。

本轮正式连续M01–M05，包括第三晚配撬棍、第四晚陈砚真实入队并轮换、第四晚完成节点、第五晚设施支援提示。隐藏GPU专项955项、44张图，简中/繁中/英文×16/20/24字号；修复英文大字号教学卡被旧营地说明挤出首屏的问题。后期带教/第23晚为明确隔离夹具，不是连续24日教学证据。另修复M05被队友挡路及剩余行动点不足时的空提示、嵌套窗口关闭引用失效。源码与图哈希见visual-review.json。全量检查/候选以 `p4campguide-20261117` 收据为准；没有Windows原生或真人品质通过声明，P4-018-01继续打开。


本轮39组统一全量检查与最终955项营地专项通过；44张隐藏GPU图对应相同源码。新候选 `build/night-tide-0.18-p4campguide-20261117-windows.zip`，155276528 bytes，SHA256 `f5a9d5522247c8732889b86ae24ae63d8cb2b1f080655cf54ac0b762d89a7f82`。实际导出PCK已验证三语目录和连续第5晚存档的第四晚完成标记，见packaged-checks.json。15个旧通用证据已恢复原字节。运行 `python3 tools/check_product018.py --full --jobs 3 --report-prefix p4campguide-20261117` 和 `python3 tools/build_windows_product018.py --candidate p4campguide-20261117 --review-dir docs/p4-campguide-20261117`。后续继续完整24日情境教学与玩法选择价值、剧情/母语自然度，不是只等用户验收。

### 前次三语与Qwen试作（历史）

2026-11-17 三语与Qwen试作：本轮见 `docs/p4-languages-20261117/review.md`、`validation.md`。用户确认简中/繁中/英文；启动页与设置提供语言入口，偏好独立于战役存档，运行不联网。两份译文覆盖3601条唯一源文案（含内部设计描述，非3601个页面）。修复动态说明、人物/目标/专长字段、剧情说话人、英文长按钮与720p三字号选项布局；冻结规则、角色获取和runtime_revision不变。母语逐句润色与整部游戏品质尚未验收。

用户本轮重新授权使用 `.env` 的 `aliyun-apikey` 尝试配乐，并已提供业务空间；不要再重复索要。Fun-Music实际返回AccessDenied。Qwen Audio成功生成44.96秒营地候选，HTTP下载超时后同一结果经HTTPS恢复；原WAV及淡出试听保留在 `outputs/aliyun-audio-20261117/`。这只是试作，不是已重制全套配乐；游戏正式音源未替换。自动听辨与人类听感分开记录，见 `audio-handoff.md`。凭据和签名URL只留在忽略目录，绝不进入Git或游戏。

本轮38组统一全量检查、183项隐藏GPU三语专项、230项后期显示、653项字号/尺寸及12项历史校验通过；69张截图与源码哈希一致。三语无显示器专项129项，剧情窗口几何仅采用GPU证据。当前检查/构建前缀改为 `p4languages-20261117`，上一候选记录保留在下方。此候选无Windows原生或真人品质通过声明，P4-018-01继续打开。后续继续实际培养/战术选择价值、营地学习节奏、完整剧情与翻译自然度审查，不能写成只等验收。


新Windows候选：`build/night-tide-0.18-p4languages-20261117-windows.zip`，155971709 bytes，SHA256 `5cf293e9ecc7933f64dad09a9c0f558480efe3442dc67b74389357a3b9ff06cf`。x64 PE/ZIP、导出PCK本机启动与三语目录读取通过；目录哈希与检查源码一致，见packaged-languages.json。Windows原生测试与human_acceptance仍为false。15个被统一检查重写的旧通用证据已恢复原字节，见restored-prior-evidence.json。

命令：`python3 tools/check_product018.py --full --jobs 3 --report-prefix p4languages-20261117`；`python3 tools/build_windows_product018.py --candidate p4languages-20261117 --review-dir docs/p4-languages-20261117`。本轮已直接从导出PCK核对三语目录与标题，仍不代表Windows原生验收。

### 前次后续引导返修（fieldguide，历史）

2026-11-17 后续引导返修：用户继续要求第二场之后逐项教学、人物与目标更清楚。当前修改见 `docs/p4-fieldguide-20261117/review.md`，验证见同目录 `validation.md`。M02开始保留已学操作，一次介绍一个有场景用途的新功能；准备页默认简明，主动展开不关闭教学；必做目标固定并可定位，地图人物姓名、机器名称、目标编号/类型、同格目标分行、危险斜纹已接入。可选教学记忆随正式存档保存，撤销不忘记已读说明，老档无标志时不强制教学。本轮未改任何冻结设计文件，也没有改变角色数值或获取顺序。配乐继续暂停。

本轮专项140项通过，正式新周目连续M01至M04，第4晚陈砚按原规则入队，掩护作业和撬棍真实执行。25张保留的隐藏GPU图包含720p三字号/1080p、M08/M12和借调人员隔离画面；后者及3项关系保障检查不得冒称真实后期成长。记录使用fieldguide/p4fieldguide-20261117独立前缀。完整回归及Windows候选仍以对应checks/build收据为准；没有Windows原生或真人品质通过声明。

本轮35组统一全量检查、140项后续教学专项、原首班119项GPU回归和12项历史检查通过。新包 `build/night-tide-0.18-p4fieldguide-20261117-windows.zip`，157397772 bytes，SHA256 `041a091017ff1abda3412593653c819a3887fe9878678fca81dcfb540280ec31`。Windows x64导出、PE/ZIP和Mac加载导出PCK启动通过；本候选未做Windows原生测试，human_acceptance=false。源码/检查/构建逐文件哈希一致。命令：`python3 tools/check_product018.py --full --jobs 3 --report-prefix p4fieldguide-20261117`；`python3 tools/build_windows_product018.py --candidate p4fieldguide-20261117 --review-dir docs/p4-fieldguide-20261117`。历史通用输出已恢复原字节，本轮新日志与存档使用独立前缀。

后续优先继续审查营地后续系统学习、后期专长的实际选择价值和连续剧情节奏；不要把本轮有限路径验证变成只等用户验收。P4-018-01仍打开。

### 前次第一场返修记录（firstshift，历史）

2026-11-17 用户要求继续打磨第一场救援、第一晚、关键剧情，明确要求 PvZ 式逐步教学，并核对初始角色和后期角色获取顺序。当前返修见 `docs/p4-firstshift-20261117/review.md`，验证见同目录 `validation.md`。新局 M01 只先显示移动，真实行动逐步展开稳定/拾起/交付/离场；第一晚压缩成状态→按需安排→结束夜晚；关键剧情使用场景/人物/对白和同屏选择。初始三人保留，后续 M04/07/10/13/16 入队，章节经验底线为 Lv1/2/3，没有新人直接获得 Lv5。配乐仍暂停，不改变平台。

本次用户指令明确修订了体验政策的三项教学字段，`release_baseline.json` 仍为唯一权威，生成视图同步；没有更改数值、关卡、人物顺序、剧本对白或选择。`tutorial-amendment.json` 保留具体授权及前后指纹，before-* 保留旧原字节。历史校验现在是243个原路径+1个旧baseline档案、43个已退休路径；不把旧档案算作原路径未变。只允许精确旧内容指纹读取，旧档不重播教学、不重新发奖励。

新证据前缀为 `p4firstshift-20261117`。`firstshift_review.gd` 用正式命令连续走新局M01→第一晚→M02→林岚第一幕；GPU截图另记 `outputs/firstshift-review-gpu.json`，headless另记 `outputs/firstshift-review.json`。原 Windows“能玩但质量差”仍未被撤销，P4-018-01保持打开。下一步继续针对后续系统学习、地图小尺寸辨识与连续剧情质量，不得写成仅等待用户验收。

本轮34组统一检查、119项连续流程/界面专项与12项历史校验通过；24张隐藏GPU图和两份真实连续存档的哈希见 visual-review.json。当前本机包 `build/night-tide-0.18-p4firstshift-20261117-windows.zip`，159266180 bytes，SHA256 `0535f165935aa52cf4ac021f295137f736602e12b998b2ee173ef808447edc51`。Windows x64导出、PE/ZIP及Mac加载导出PCK启动通过；本候选未做Windows原生测试，human_acceptance=false。源码/检查/构建逐文件哈希一致。命令：`python3 tools/check_product018.py --full --jobs 3 --report-prefix p4firstshift-20261117`；`python3 tools/build_windows_product018.py --candidate p4firstshift-20261117 --review-dir docs/p4-firstshift-20261117`。默认jobs=1仍执行完全相同检查，jobs仅并行互不读写对方输出的完整周目。

### 2026-11-13 候选（历史）

2026-11-13 最新用户反馈明确否定当前产品质量：简陋、上手不清且繁琐、剧情偏弱、音乐勉强可用。**P4-018-01 已重新打开，不再把下一步写成只等用户验收。** 本次正式工程返修及剩余差异见 `docs/p4-quality-20261113/review.md`，验证见同目录 `validation.md`。已调整战斗/营地/标题/剧情界面、行动预览、30场景演出、地点地面材质与混音。用户已明确“OpenAI没有能生成的模型就先算了”，配乐重制暂停，继续现有音源；不得再次索要其他服务或把它列为等待用户答复。平台尚未决定改变，冻结0.18保持不变。旧p4art结果仅作历史，后续包用p4quality-20261113。


本轮33组完整检查与14张隐藏GPU界面复核已通过，详见 `outputs/p4quality-20261113-checks.json`。新候选及导出证据以 `docs/p4quality-20261113-build.json` 为准；不能用其替代Windows原生或品质通过。后续优先从本轮review.md的“仍未关闭”继续，旧表不是当前完成结论。

当前本机包：`build/night-tide-0.18-p4quality-20261113-windows.zip`，156706323 bytes，SHA256 `9cb312f1bb357eaff3b80b8977319f9aa05966811f8157a71da5f5853568b343`。Windows x64导出、PE/ZIP及Mac加载导出PCK启动通过；本候选未做Windows原生测试。

### 上一候选记录（p4art，历史）

2026-11-13 原 P3 聊天在候选包完成、最终暂存后连接失败，已由接手聊天恢复提交交付。接手复核见 `docs/p4-018-20261113/recovery.md`：源码/检查/包收据一致，仍待本轮 Windows 与真人验收。下方第5节的早期缺口描述须结合本轮差异表和当前进度读取，不能把已经完成的新素材重新列为未制作。

用户已恢复官方 API 额度并要求继续。此前暂停/额度不足状态已结束；已完成全部八人新立绘、每人两套完整人体服装与八表情复用、三视设定参考、与服装一致的六帧棋子、四类居民/两类借调和十二地点地标。用户批准的是 `p4close-corrected-art-v3.png` 的方向；不等于全套美术或整款游戏最终验收。

当前仍在 P4 产品对齐与验收阶段。初始三人出发位置选择、实际培养/带教预览、16专长解释、剧情事实与全文速览修正已保留；真实八条24日培养路线与三条同AP收益分支记录见本轮差异表。冻结设计、收益、阈值及保存 runtime_revision=8 未改。

本轮人物材质是完整人体底图加同位脸部替换，保留原颈肩；128种实际GPU组合检查和96px集合图已复看。行走重复同腿的图已返修为交替脚，动作、命中和搬运沿用正式指令反馈。图像来源/全部提示/最终文件哈希见 `docs/p4-018-20261113/image-prompts.json`。初版莫遥身份、错误步态与残留背景均记录为返工，不列作验收素材。

用户另开声音对话 `01a1d35e-924f-7a91-8c60-98fa85045576`，音频负责人已完成制作并停止写入。官方 gpt-audio-1.5 请求成功，但非语音音效小样返回口头说明，没有作为游戏资源。正式声音采用可复现原创合成，6首循环/24短音；新增4首循环与12短音，窗口音乐所有权、翻页/保存、暂停/跳过、失败结算和中继增援提示已接回主工程。看 `docs/p4-018-20261113/audio-handoff.md` 与 `audio-integration.md`；没有运行时API依赖。

本轮31组统一检查与独立80项音频检查通过。Windows x64导出、PE/包哈希检查和Mac加载导出PCK启动通过，详细结果以 `docs/p4-018-20261113/validation.md`、`outputs/p4art-20261113-checks.json`、`docs/p4art-20261113-build.json` 为准；不存在的收据不能称通过。命令：

```sh
python3 tools/check_product018.py --full --report-prefix p4art-20261113
python3 tools/build_windows_product018.py --candidate p4art-20261113 --review-dir docs/p4-018-20261113
```

接下来按 `docs/p4-018-remaining.md`：P4-018-01核对具体差异与证据边界；P4-018-02本轮包交用户Windows测试；P4-018-03目标8GB硬件、新人/完整周目、美术与听感验收。不能用本机检查或生成数量替代真人/Windows证据。2026-11-12的 p4close 包只有代码修正，且更早Windows包已由用户验证并授权删除；均不能代表本轮包已验收。

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

同一 Godot 工程 `game/`，GDScript、Compatibility，锁定 Godot `4.7.2.stable.official.ed1daf0bf`。Windows 11 x64、键鼠；本轮新增简体中文、繁体中文、英文，macOS为开发环境。

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
| 三语展示/翻译资源 | `presentation/localization.gd`、`data/localization/{zh_CN,zh_TW,en}.json`；离线目录检查 `tools/check_localization.py` |
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

## 5. 下一步从这里继续：核对 P4-018-01 与 P4-018-02/03 验收

按 [11 月 19 日验收表](p4-release-20261119/validation.md) 核对 R01–R08/H01–H04。遇到缺陷要保留当天存档、输入步骤与本包 SHA256，修复对应入口后再交付新包。

1. P4-018-01 已有新周目 24 天可见控件走查、三条逐晚读盘路线、八人同时点对照、96 节点三语审读、12 地点棋盘和六首运行时配乐。完整人工节奏、96px 辨认、台词自然度和听感仍待实测。详见同目录 campaign.md、story-review.md、audio-handoff.md。
2. P4-018-02 使用下列命令重建并独立核对 ZIP 内的 PCK。使用默认历史检查，保留旧证据原字节。正式安装包不进 Git。
3. P4-018-03 继续按本候选的[实测单](p4-release-20261119/windows-review.md)、[采样说明](p4-release-20261119/reference-session.md)和验收表获取 Windows 11 x64 8GB 的实际采样、5 人首战与一章记录、5 份完整周目观察。旧包实测不能移作本包证据。发现阻断缺陷即继续返修。

```sh
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4release-20261119
python3 tools/build_windows_product018.py --candidate p4release-20261119 --review-dir docs/p4-release-20261119
python3 tools/verify_release_pack.py --candidate p4release-20261119 --review-dir docs/p4-release-20261119
```

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
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4release-20261119
python3 tools/build_windows_product018.py --candidate p4release-20261119 --review-dir docs/p4-release-20261119
```

Windows PowerShell（Python已安装）：

```powershell
python tools/bootstrap.py windows
python tools/bootstrap.py templates
$env:GODOT = (Resolve-Path 'work/toolchain/windows/Godot_v4.7.2-stable_win64.exe').Path
python tools/check_product018.py --full --jobs 3 --report-prefix p4release-20261119
python tools/build_windows_product018.py --candidate p4release-20261119 --review-dir docs/p4-release-20261119
```

原 macOS 工作机：`/Users/a1-6/projects/person/gameNOT`；默认引擎为 `work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot`，已安装的 Windows 导出模板仍可离线使用。新 Mac 需自行准备锁定版本并使用 `GODOT` 指向可执行文件；bootstrap 当前没有 macOS 引擎下载目标。

默认检查应报告 244/287 份受保护历史内容已核验（243个原路径，加1份旧baseline档案；另核验本次获准教学修订的当前文件）、43 个已按清理清单移除，`history.missing=[]`、`history.complete=false`。其中 36 张重复截图有受保护的同字节原图，原图缺失或损坏会报错；恢复旧路径时也必须通过原 SHA256。兼容参数 `--allow-missing-history` 仅可容许未记入清单且被 Git 排除的旧 ZIP/AVI 缺失；当前新克隆不需要它。

当前入口是 `check_product018.py` / `build_windows_product018.py`。旧 `check.py`、`build_windows.py`、baseline018、p4-tuning入口只对应历史阶段。CI已换到当前入口，仅PR和手动触发；**本次直接推main不自动运行CI，不能声称远程CI通过**。

全量检查会重写当前输出日志/周目记录；重建会覆盖当前product018包和收据。修改前保存必要旧证据，不覆盖冻结保护文件；新一轮产品验收应使用独立报告名。Godot源码变动后，构建要求与全量检查的源文件哈希一致。

图形检查：原工作机不要占用用户主显示器，曾指定的外屏目前不可假定存在。可用 `game/tests/product018_offscreen_review.gd`（隐藏根窗口的GPU截图）或先确认可用外屏；headless通过不等于视觉验收。无GPU环境只跑规则，把视觉验证明确留待有图形环境完成。

## 7. 可以直接交给下一位代理的指令

> 请接手这个仓库。先读 `docs/NEXT_AGENT_HANDOFF.md`，以冻结0.18为唯一设计权威，从第5节 P4-018-01 开始，核对并补齐剩余产品差异。已有完整战役候选包不代表最终验收完成。人物获取、养成、关系、剧情和玩法必须在正式存档中贯通。复用当前工程与资产，勿重做演示、改定稿或只靠测试宣布完成。先独立完成实现和本机验证，再按既定安排交Windows包给我测试。记录具体修改、证据、尚缺验收；不要重复索要Windows远程入口。
