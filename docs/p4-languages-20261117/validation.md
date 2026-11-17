# p4languages-20261117 验证范围

本轮是三语接入与排版返修，不是正式发行验收。冻结baseline SHA256仍为 f5a51e5375e0f31ee85510b56bb728c1417ce46d5594a94bd907e1eddff92a9c；未修改设计视图、人物数值、获取顺序、奖励或 runtime_revision=8。

`multilanguage_review.gd` 为每种语言启动正式新周目，连续M01→第一晚→M02→林岚第一幕与private选择；切换真实语言按钮、重新读取偏好，比较全部内存状态与磁盘存档字节。包含标题、准备、战术、营地、人物、关系、装备、档案、帮助、登场和剧情。英文显示控件扫描不应残留中文（语言原生名称除外）。语言目录检查覆盖3601条当前唯一源文案，并检查非空值、英文中文残留、printf占位符及其顺序。

隐藏GPU使用锁定Godot、隐藏根窗口和1280×720 SubViewport；第一场与剧情选项覆盖16/20/24字号。故事选择区的几何检查仅在真实GPU模式执行：headless没有显示器，`popup_centered_clamped`只给580×400最小窗口，不能把这一尺寸当作720p视觉证据。最初未区分此行为的失败记录保留在initial-check-failure.log；没有用headless冒充GPU通过。

`language_lategame_review.gd`分别读取保留的day23/day24存档，检查结局、档案、八人培养/专长说明。全部54个演出故事开场采用隔离副本补seen记录后渲染，不写存档、不发奖励；这不证明这些故事在该周目已实际解锁，也不是三种语言的完整24日游玩。另42个社区/章节节点的译文进入目录，其所有适用分支没有逐页真人审读。

统一全量检查与本候选构建结果以outputs/p4languages-20261117-checks.json及docs/p4languages-20261117-build.json为准。重新运行检查会改写旧通用输出；归档时恢复上一轮原始证据，本轮独立前缀日志与新三语报告保留。规则完整周目仍以自动策略为主，不是新人盲玩或最佳策略证明。

复现：

```sh
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4languages-20261117
work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/multilanguage_review.gd
python3 tools/build_windows_product018.py --candidate p4languages-20261117 --review-dir docs/p4-languages-20261117
```

Windows原生键鼠/性能、8GB设备两小时内存、新人教程体验、整部剧本母语润色和人类审美验收仍缺证据。旧Windows“能玩但质量差”的反馈不因本轮通过检查而自动撤销。

最终隐藏GPU专项183项通过，69张截图与源文件哈希见visual-review.json；无英文中文残留。独立偏好与磁盘保存比较、剧情选择ID检查包含在该流程。无显示器专项129项、后期显示230项另记，不把headless最小窗口当作真实720p。原有三字号/三分辨率检查已扩展到简中、繁中、英文和伪本地化，共653项；伪本地化仅是压力测试，不是第四种玩家语言。历史校验12项通过。

最终38组统一全量检查通过，报告为outputs/p4languages-20261117-checks.json；检查开始与结束逐文件源码哈希相同，并与最后隐藏GPU快照一致。八条24日培养路线、四条基础完整战役与四种额外策略完成；三难度×两环境×36任务共216条有限路径通过。以上不等于穷举策略或真人体验。

新Windows候选：`build/night-tide-0.18-p4languages-20261117-windows.zip`，155971709 bytes，SHA256 `5cf293e9ecc7933f64dad09a9c0f558480efe3442dc67b74389357a3b9ff06cf`。x64 PE/ZIP、导出PCK本机启动与三语目录读取通过；目录哈希与检查源码一致，见packaged-languages.json。Windows原生测试与human_acceptance仍为false。15个被统一检查重写的旧通用证据已恢复原字节，见restored-prior-evidence.json。
