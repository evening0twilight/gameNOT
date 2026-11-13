# p4quality-20261113 验证记录

这是产品质量返修候选，不是最终发行。用户报告画面简陋、上手繁琐、剧情偏弱及音乐勉强可用，本轮未将这些意见改写为“只待填表”。完整差异见源码review.md（包内PRODUCT-REVIEW.md）。配乐重制按用户指示暂停。

## 源码及本机检查

- 实现保存点：73df7d0；最终游戏源码与outputs/p4quality-20261113-checks.json逐文件SHA256一致，构建脚本再次强制比对。
- 统一全量检查：33组通过，共约1221秒；本轮各检查日志无ERROR或WARNING。冻结manifest全部生成视图与唯一baseline一致，规则数据、奖励、阈值、runtime_revision=8不改。
- 新增p4quality_tests：835项通过。包括实际M01出发→预览/取消→撤退→营地，嵌套弹窗不改变预算；剧情选项后接续回应；30演出场景的当面/休养/来信与回看语义（明确隔离夹具）；标题三字号与两分辨率；混音切换功率、压低恢复和共享限幅。
- 原UI本地化布局检查507项通过，覆盖720p/1080p/1440p、三字号与伪本地化；原音频80项回归通过。
- 36地图×2环境×3难度共216条有限脚本路径通过；四类24日周目、关联培养关系周目、八条24日重点培养路线通过。它们是正式规则指令与真实成本/保存读取，仍不是人类玩法或平衡验收。
- 受保护历史244/287路径哈希核验；43路径已按显式清理清单退休，missing为空，complete=false。不声称已检查不存在的历史文件。

## 图形复核

使用隐藏原生根窗口与实际GPU SubViewport，1280×720输出14张图；不占主显示器，不是概念图或Windows截图。新局/实际M01出发及移动、正式day06/day18/day24保留周目作为来源。棋盘边长474像素；p4quality-visual-review.json failures为空。复看了标题、战斗、营地、准备和剧情截图。音频停止后留出混音器释放时间，最终隐藏渲染日志无错误或警告。

## 构建与证据边界

命令：

```sh
python3 tools/check_product018.py --full --report-prefix p4quality-20261113
python3 tools/build_windows_product018.py --candidate p4quality-20261113 --review-dir docs/p4-quality-20261113
```

导出结果以docs/p4quality-20261113-build.json为准；包内build-receipt.json包含EXE/PCK和源码哈希。构建检查包括Windows x64 PE、ZIP完整性、Mac加载导出PCK启动；这些均不能代替Windows原生测试。

windows_native_tested=false，human_acceptance=false。未取得本候选Windows键鼠、8GB参考机/2小时内存、5人新人/整局、审美或听感通过证据。实际未关闭的质量项见PRODUCT-REVIEW.md。平台未迁移，没有运行时模型/API依赖。
