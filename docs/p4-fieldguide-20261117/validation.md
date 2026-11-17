# p4fieldguide-20261117 验证记录

本轮是继续返修，品质与最终发行未通过验收。

专项脚本fieldguide_review.gd从正式新周目开始，经M01、第一晚、M02、M03、M04到第4晚，使用生产Session/Rules和正式装备草案。包含真实的掩护作业与撬棍执行、预览取消、读档、教学记忆、目标定位、旧档、撤销、跳过以及非法教学数据拒绝。140项检查、158条记录命令通过；M04招募陈砚仍按正式进度触发。另有3项独立关系保障检查。独立M08/M12及临时支援员场景只检查后期机制说明与布局，不伪装为实际成长路线。

隐藏GPU使用锁定Godot、隐藏原生根窗口及实际SubViewport。25张保留截图和第4晚连续存档的SHA256见visual-review.json；记录为outputs/fieldguide-review-gpu.json，无图形执行另存fieldguide-review.json。复核720p的16/20/24字号和1080p；大字号说明允许滚动，不能把自动几何检查称为新人盲玩通过。

35组统一全量检查通过，检查期间游戏源码哈希保持一致；结果见outputs/p4fieldguide-20261117-checks.json。涵盖36地图×2环境×3难度的216条有限脚本路径、24日战役及多种玩法路线、八条完整培养路线。历史验证另见outputs/fieldguide-history-check.log，12项通过。Windows构建另以docs/p4fieldguide-20261117-build.json为准。

```sh
python3 tools/test_history_validation.py
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4fieldguide-20261117
python3 tools/build_windows_product018.py --candidate p4fieldguide-20261117 --review-dir docs/p4-fieldguide-20261117
```

本轮没有修改冻结baseline或生成设计视图。runtime_revision仍为8，field_lessons是可选教学记忆；既有精确旧指纹兼容规则未扩大。游戏数值、获取和培养门槛不改。上一候选的GPU截图、连续存档和视觉哈希收据保留，不用本轮重跑覆盖它们。统一检查仍会临时重写旧通用输出；最终归档时恢复其原字节，本轮回归以独立前缀日志为准，新连续存档独立使用fieldguide名称。

仍缺本候选Windows原生键鼠/性能、8GB设备两小时内存、新人学习节奏、完整战役真人体验与人类审美验收。源代码、自动检查、隐藏GPU、导出包与真人证据分别记录。

隐藏图形复现：`work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --path game --minimized --resolution 1x1 --script tests/fieldguide_review.gd`；借调人员与M05同格设施的独立复核使用同参数运行`tests/fieldguide_support_review.gd`。

地图通用渲染也影响第一场，因此另运行原firstshift_review.gd的隐藏GPU回归：119项通过。新画面保留4张（移动三字号与拾起），使用fieldguide-firstshift前缀；原先的firstshift系列证据已恢复原字节。

导出完成：`build/night-tide-0.18-p4fieldguide-20261117-windows.zip`，157397772 bytes，SHA256 `041a091017ff1abda3412593653c819a3887fe9878678fca81dcfb540280ec31`。Windows x64 PE与ZIP完整性检查通过，导出PCK在本机macOS加载启动通过；不构成Windows原生测试。源码与统一检查、构建收据逐文件SHA256一致。
