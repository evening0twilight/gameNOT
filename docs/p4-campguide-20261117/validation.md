# p4campguide-20261117 验证范围

本轮新增campguide_review.gd，使用正式命令从新周目连续M01走到M05结算营地。包含第二晚通过真实夜间总结按钮补读、第三晚给苏棠配已有撬棍、第四晚真实陈砚入队后保存林岚/苏棠/陈砚阵容、第5场完成和后续营地单项提示；保存读取与教程完成时点、阅读不改资源/人物/关系、旧存档兼容、损坏元数据拒绝均单独检查。

晚期检查采用隔离副本，分别验证支援期限的优先级、带教实际资格查询、单处设施页面与第23晚路线页面。师生资格夹具调整了经验与共同经历，只证明展示条件，不冒充真实后期培养。全部截图以campguide前缀保存。

隐藏GPU使用根窗口隐藏、1280×720 SubViewport及RenderingServer.force_draw，检查简中/繁中/英文×16/20/24字号×第2/3/4/5晚。首轮等待frame_post_draw在隐藏窗口处停止，改为主动离屏绘制后重新完成全流程；没有显示主窗口，也不把headless当作视觉证据。英文24字号首屏教学卡下沉问题复看后修正，检查新增教学按钮首屏位置约束。

统一检查新增本专项，保留全部已有规则、历史、三语与完整周目回归。源码冻结后运行全量检查，再导出同一哈希的Windows候选。最终数量、源码/图片哈希及构建结果以visual-review.json、outputs/p4campguide-20261117-checks.json与docs/p4campguide-20261117-build.json为准。

复现：

```sh
work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/campguide_review.gd -- --isolated-ui-review
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4campguide-20261117
python3 tools/build_windows_product018.py --candidate p4campguide-20261117 --review-dir docs/p4-campguide-20261117
```

冻结baseline SHA256仍为f5a51e5375e0f31ee85510b56bb728c1417ce46d5594a94bd907e1eddff92a9c；runtime_revision仍为8。没有Windows原生键鼠、8GB设备两小时性能或真人新手体验通过声明。三语目录覆盖检查不等于母语逐句审读。全量检查覆盖的自动策略不等于所有玩家策略。

最终隐藏GPU专项955项通过，202条正式UI行动记录，44张截图。图与源码哈希见visual-review.json；字段中隔离带教和终夜画面明确区别于连续新周目。

无显示器营地专项同样955项通过，原首班119项与后续战术140项通过；三语专项129项、后期显示230项、字号尺寸653项通过。最终语言目录覆盖3680条唯一源文案，新增教学不依赖运行时API。

导出后额外使用tools/verify_pack_campguide.gd，从实际PCK读取本轮连续第5晚存档、检查第4晚完成标记与新周目初始化，并在内存中读取一个后续说明，确认不改资源/人物/日期。另使用verify_pack_languages.gd核对导出三语目录。结果随packaged-checks.json保存；这些仍是Mac加载导出包，不是Windows原生运行。

最终39组统一全量检查通过，八条24日培养路线无失败、八名角色的第二专长均有实际使用记录；三难度×两环境×36任务共216条有限路径、四条完整战役、四种额外策略通过。该断言证明脚本执行路径与保存兼容，不证明最优策略、所有教学时机或真人平衡。检查源码哈希与最终GPU截图对应源码一致。最终字号专项使用设置实际提供的16/20/24，另存camp-fonts-final.log复核。

新Windows候选：`build/night-tide-0.18-p4campguide-20261117-windows.zip`，155276528 bytes，SHA256 `f5a9d5522247c8732889b86ae24ae63d8cb2b1f080655cf54ac0b762d89a7f82`。x64 PE/ZIP、导出PCK本机启动，以及实际包内三语哈希和连续第5晚教学存档读取均通过，见packaged-checks.json。Windows原生与human_acceptance仍为false。15个被检查重写的历史通用输出已恢复原字节；本轮campguide专属存档、截图和独立前缀日志保留。
