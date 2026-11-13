# 2026-11-13 产品质量返修

用户反馈：画面简陋、不知道怎么玩且繁琐、剧情偏弱、音乐勉强可用。这是质量未达标反馈，不是仅缺验收表。P4-018-01 重新打开。平台尚未改变，继续冻结0.18的同一 Godot 工程。

权威：`game/data/final_design/design_manifest.json` 指向的 `release_baseline.json`。本轮不更改规则、原对白、选择、奖励、阈值或存档版本。

| 依据 / 问题 | 正式工程返修 | 证据与余项 |
| --- | --- | --- |
| release_scope.platform.ui / battle；棋盘被大面积装饰和按钮挤小 | 三栏任务/棋盘/行动，720p棋盘边长约350→474；目标坐标、行列号、救/运/工与危险图例；专长优先，回合操作固定在底部 | 隐藏GPU实渲染 p4quality-battle.png；不是Windows输入或美术验收 |
| experience.tutorial_policy.information；预览只有AP与内部坐标 | 显示实际规则预览中的生命、AP、稳定、交付、施工进度和目标位置；取消无状态变化 | p4quality_tests 实际M01出发/预览/取消；仍需新人理解目标与替代方案的实际证据 |
| release_scope.screens.camp / H03；营地堆积大量按钮 | 先显示夜间预算/自然休息/明日入口，再人物卡；短谈选择对象，更多安排集中收纳；培养比较、装备、关系、认责和倾向仍有正式入口 | 实际M01撤退→营地；真实day06存档GPU复看。新布局不代表完整周目的管理负担已达标 |
| release_scope.screens.story / scripts；选完又从开头看，画面缺少情境 | 选择后直接到对应回应；背景和人物融入阅读区域；18生活+12双人场景补具体动作与停顿，放在原页内不增加翻页 | 30场景×当面/休养/来信隔离检查，记录回看不因后来康复改变；动作只用于记录为在场的版本。未重写冻结剧情，不宣称故事吸引力已达标 |
| release_scope.assets.location_kits；多数地点都使用甲板底材 | 新增钢板/瓷砖/水泥/木板/浅水/深水/墙/碎石8材质，12地点映射4基础材质；复用原地图与地标 | image-prompts.json，正式场景GPU复看；完整地点空间美术与人物融合仍需继续打磨，8材质不等于12地点完成审美验收 |
| release_scope.screens.title；入口像后台表单 | 使用事务所背景、救援主题短文、清晰的新周目/继续入口 | p4quality-title.png；720p/1080p三字号检查 |
| release_scope.assets.music；6曲存在但听感弱 | 保留现有音源，等功率切换、脚步轻微音高变化、关键提示暂压伴奏、主输出限幅 | 80项原音频回归+新增交叉切换/压低恢复检查。不是新配乐或听感合格证明 |
| H04；新导航发生独占弹窗冲突 | 新弹窗隐藏父窗，关闭后延迟恢复仍有效父窗 | 专项真实UI回归；不重复扣预算 |

## 声音复核结论与用户决定

已读取声音制作聊天 `01a1d35e-924f-7a91-8c60-98fa85045576`。6循环/24短音来自可复现原创合成；以前 gpt-audio-1.5 尝试得到口头说明，没有生成正式器乐。现有camp/ending约24秒单声道，另4循环约18–33秒；这只说明资源结构，不能证明音乐质量。

`audio-model-review.json` 是 gpt-audio-1.5 对72秒音乐串听样例的辅助分析：指出音色偏薄、循环感和场景区分不足。它不是人耳验收，不覆盖全部音轨，也不将模型评价当客观评分。官方音频模型文档定位为语音，当前可用接口实测不能直接交付本项目器乐。2026-11-13用户明确回复“没有的话就先算了”，因此暂停配乐重制，不再等待其他服务或密钥；音源继续使用，品质缺口保留记录。

## 仍未关闭

- 美术统一性、复杂关卡的目标/角色/机器小尺寸辨识，不能仅用放大棋盘和新纹理关闭；代表画面方向仍未获得本轮认可。
- 剧情连续体验和人物吸引力仍不足；本次只修演出、节奏和明确重复阅读问题，未擅改冻结主线/对白/选择。
- 5人新人、5份完整周目与目标Windows 8GB机器性能证据仍缺；没有把脚本周目当真人，不把此前Windows“能玩”记录升级为品质通过。
- 本轮不是平台迁移。换平台尚未决策，也不会自动解决画面、引导和剧情问题。

原 p4art 包与其报告保留历史。当前检查与包使用独立前缀 p4quality-20261113。所有本机图形检查使用隐藏根窗口的GPU SubViewport，不占主屏。

## 冻结16类界面的入口核对

这是生产代码入口核查，不等于16页全部通过人类体验验收。本轮主要调整title/battle/camp/story；其余复用原正式入口。

| 定稿界面 | 生产入口 | 此轮确认范围 |
| --- | --- | --- |
| title | campaign_screens.title / main.can_variant_b | 新周目、继续、存档选择、帮助、音量、退出及天气B解锁状态 |
| slots | campaign_screens.manual_slots / main.recover / campaign_picker | 十个手动位置、覆盖确认、备份恢复和周目选择保留 |
| new_game | main.new_campaign / difficulty_controls | 原三难度披露、严峻确认、天气B解锁条件保留 |
| briefing | campaign_screens.briefing / city | 必须目标前置；环境、城市事实、支线期限读取正式数据 |
| deployment | campaign_screens.briefing / planning_board | 3人/后勤、装备、L2倾向、药剂和接应草案仍可操作 |
| battle | tactical_workspace.render / main.propose | 新布局；所有预览仍来自Session同一规则入口 |
| settlement | main.render_camp / appraisal_log | 目标事实、资源和XP、社区发布选择、关系事件原因保留 |
| side_offer | main.prepare_mission / show_journal | 接受、稍后、已尝试与过期信息入口保留 |
| camp | camp_workspace.show / main.show_night_review | 2项目2短谈、疲劳预览、自然睡眠及D23警告可达 |
| growth | campaign_screens.profile / main.group_project | 个人课程/合法带教的实际成本与收益比较保留 |
| supply | main.show_workshop | 购买、撤销、制作、库存和设施入口未删除 |
| relations | campaign_screens.relationships / camp_workspace.administration | 方向关系、认责、证据补救、约定/授权入口保留 |
| story | story_screen.show / journey_presentation.scene | 新回应接续；现场/休养/来信与摘要语义保留 |
| journal | main.show_journal / render_campaign_options | 已知事实、可用但未读故事占位、核查与发布入口保留 |
| ending | main.render_ending | 世界、地区、人物选择/履约、关系收束及另开存档保留 |
| settings_help | main.settings_action / show_help / pause_menu | 三字号、声音、速度、动效、键位与保存返回保留 |

## 本轮实渲染画面

全部来自1280×720隐藏GPU SubViewport；不是概念图或Windows截图。

- [标题与周目入口](../../outputs/p4quality-title.png)
- [正式M01战斗与目标坐标](../../outputs/p4quality-battle.png)
- [真实day06存档营地](../../outputs/p4quality-camp.png)
- [真实day06回看P_lin_1的对话区域](../../outputs/p4quality-dialogue.png)
- [实际已提交移动中的画面](../../outputs/p4quality-walking.png)

对话截图用于检查布局；30段新补演出由专项测试检查适用状态，不将此P_lin_1截图说成L/R演出全量展示。
