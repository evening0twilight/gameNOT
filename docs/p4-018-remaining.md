# P4-018 本轮差异闭环（2026-11-13）

最新：用户已否定画面、上手/繁琐程度、剧情与音乐品质，不能继续将表中“真人待验”理解为实现已达到产品目标。P4-018-01重新打开。本轮实际返修与尚未解决内容见 [质量复核](p4-quality-20261113/review.md)，候选验证见 [本轮记录](p4-quality-20261113/validation.md)。配乐重制已按用户指示暂停；平台未改变。本轮33组统一检查通过，Windows导出记录使用docs/p4quality-20261113-build.json，截图使用outputs/p4quality-*.png。下表保留上一候选的证据，不代表本轮品质通过。

唯一权威为冻结0.18；当前仍是 P4-018-01，未通过最终验收。用户已验证旧Windows包，新包须另记实测。本轮八人素材与声音已整合，候选包仍需独立验收。

| 项目 | 定稿依据 | 当前实现/证据 | 未满足部分与关闭条件 | 状态 |
| --- | --- | --- | --- | --- |
| R01 首次接触 | experience.visual_policy.first_contact | `campaign_screens.introduction`：初始3人可调整真实出发位置；后加入5人可换入草案；保留原安排/地图/档案入口。`p4close_tests`核对初始3人×3位置实际部署；`p4close-first-contact.png`为720p实际界面 | 新人能理解选择作用仍需观察，不把已读介绍当玩法选择 | 实现已修，体验待验 |
| R04 人物美术 | release_scope.assets / experience.visual_policy.consistency | 用户认可完整人体底图+同位脸部方向后，八人两服装/八表情正式接入，8份三视参考与8组六帧棋子；修正莫遥身份、重复同腿和透明背景。`p4art-character-review.json`128种实际组合、`p4art-ensemble.png`96px与同服装辨识复看 | 方向批准不等于8人最终审美；需用户逐人辨识和正式场景确认；不把像素不变等同审美通过 | 制作/正式接入完成，人类美术验收待定 |
| A 全部养成用途 | progression_relationship.levels、abilities、acceptance.H02 | 正式人物页显示Lv2/3/4/5/6跨级收益、实际训练/休息/治疗/不培养与符合条件带教预览，16专长附普通替代及代价。`p4close-before-mentor.json`是正式连续周目带教前状态；8条各24日重点培养路线，逐日真实保存读取，8人第二专长都有正式使用记录 | 发动/取得不等于战术价值已验收；五级全部差异的场景和机会成本仍逐项确认，江朔三格交接和叶禾三格绝缘已补入独立连续路线（`p4close-growth-campaign-jiang/ye.json`）；已新增陈砚合法分支对照：M08装置两轮后3HP对0HP、M24档案2HP对0HP；贺鸣M22交接装置6HP对3HP、莫遥M15贺鸣10HP对8HP也已补入合法分支对照；5名玩家决策解释尚无 | 实现与连续证据扩充，收益验收未关 |
| B/R05 剧情变体 | scripts.fact_selection、acceptance.R05 | `story_facts.gd`统一结算、社区、章节、回看、结局事实。修复C14失败否定已带回药品、M17隔离结语、固定责怪他人的违约台词。替换多处制作备注式文本。速览读实际呈现页，不用可能含编辑备注的节点opening。`p4close-editorial.json`包含654条分支呈现记录/4001检查 | 已实际审读54节点休养开场及42社区/章节成功与条件文本，完成针对性修正；2026-11-13代理完成398条去重场景台词及108条社区/章节结语审读，修复L06离队来信的练舞时态；全部适用状态组合与真人连续逐页体验仍未验收 | 已修明确矛盾，逐页验收未关 |
| C 素材用途 | release_scope.assets、acceptance.R08 | 8人新棋子与立绘服装一致；4类居民按目标文本映射、2类借调外形，12地标在地点卡和棋盘边缘显示；6机器/48图标保留，实际GPU集合图`p4art-assets-*`。6曲/24短音接入，新增4曲/12短音，主工作区音频80项检查通过 | 小尺寸阅读、地点识别与听感仍需真人；图标带文字辅助，不声称全部无需标签识别。图像为官方API生成；新增声音为原创合成，未冒称gpt-audio生成 | 已修已知素材差异，真人待验 |
| D 引导/负担 | acceptance.R06、H01–H03 | 720p首次接触、培养、剧情速览、地图、动作实际GPU复看；沿用三字号与多分辨率检查；增加按包记录的实测单/空白观察表 | 尚无5人新人试玩/完整周目观察；档案内容较长，需实测导航/阅读负担 | 本机复看完成，真人待验 |
| P4-018-02 | acceptance.R01–R06 | 本轮命令`check_product018.py --full --report-prefix p4art-20261113`与`build_windows_product018.py --candidate p4art-20261113 --review-dir docs/p4-018-20261113`，源码、检查、包哈希一一对应 | 全量检查/导出收据以本日validation为准；本机导出PCK启动不能代替Windows；用户按本包实测 | 31组统一检查与Windows导出/本机PCK启动通过；Windows原生与人类验收待定 |
| P4-018-03 | acceptance.R07/R08/H01–H04 | 新增隐藏1080p GPU稳定棋盘/后期存档预览计时工具；11月12日本机95分位17.341ms、首次预览187.543ms；11月13日分别15.227ms和16.277ms，旧尖峰未复现但原因未确定，未宣称Windows性能通过；Windows实测单和新人观察表已准备 | 目标Windows 8GB机器、冷启动、真实输入延迟、2小时进程内存、5人体验及本轮美术/听感仍无验收证据。Mac结果单列，不替代 | 待实测与人类确认 |

本轮未改变冻结规则、奖励、成长阈值或存档版本。没有运行时生成式AI。密钥只从本机.env读入子进程环境，不写报告、Git或游戏包。

## 本轮可复现命令

```sh
python3 tools/check_product018.py --full --report-prefix p4art-20261113
python3 tools/build_windows_product018.py --candidate p4art-20261113 --review-dir docs/p4-018-20261113
work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/p4close_offscreen_review.gd -- --isolated-ui-review
work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/p4close_asset_review.gd -- --isolated-ui-review
work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/p4close_performance.gd -- --isolated-ui-review
```

性能命令应在其他Godot检查结束后单独运行；同时运行的检查会争抢CPU，不能拿受争用的帧率结果判定产品性能。隐藏GPU路径不占用户主屏，仍不是Windows键鼠/显示端验收。
