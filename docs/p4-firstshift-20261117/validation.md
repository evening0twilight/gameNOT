# p4firstshift-20261117 验证记录

当前为返修候选，不是正式发行或品质通过。具体体验变化见 review.md。

本轮采用正式 Session/Rules 从新周目连续执行 M01、第一晚、M02、林岚第一幕，没有注入角色经验、任务完成或剧情解锁。第一场两名居民实际交付，第一晚实际训练和保存读取。未知内容指纹、错误校验和、损坏教学状态仍被拒绝；保留旧存档读取不强制教学。角色入队/高级能力限制另以明确隔离回归检查验证。

最终专项119项检查通过，包含92个记录的连续实际操作、真实移动按钮/地图点击与剧情选择按钮、预览取消、读档、教学跳过/撤销、旧指纹兼容和未来角色不可提前培养/出战。该路径救回M01两名居民；第一晚真实训练后延续M02，再打开林岚人物节点并选择保留私人边界。原剧情质量回归916项和UI本地化507项也在本轮执行。

隐藏 GPU 图形记录为 outputs/firstshift-review-gpu.json 与 firstshift-*.png；常规无图形记录为 outputs/firstshift-review.json。输出24张实际截图，包括720p下16/20/24字号的移动与营地布局；图片与两份真实GPU周目存档哈希记录在 visual-review.json。均不是 Windows 原生或真人学习表现。

本轮34组统一全量检查通过，日志无错误或警告；36地图×2环境×3难度的216条有限脚本路径、四类24日周目、联动周目、八条重点培养路线均执行完成。独立历史校验12项通过。全量检查及导出结果以 outputs/p4firstshift-20261117-checks.json、docs/p4firstshift-20261117-build.json 为准。源代码在检查开始时锁定 SHA256，导出前再次核对；不能用上一候选记录代替。

命令：

```sh
python3 tools/test_history_validation.py
python3 tools/check_product018.py --full --jobs 3 --report-prefix p4firstshift-20261117
python3 tools/build_windows_product018.py --candidate p4firstshift-20261117 --review-dir docs/p4-firstshift-20261117
```

runtime_revision=8；唯一获准的内容指纹迁移是本次三个教学政策字段修订的精确前驱版本。规则、获取顺序、经验、数值和剧情选择不改；原 baseline 原字节另存，历史受保护哈希不重写。旧第6/18日存档也保存在同目录 before-save-day06/18.json，兼容检查直接读取这些旧字节，避免全量周目输出更新后变成新档测试。

未取得本候选 Windows 原生性能/键鼠、8GB参考机两小时内存、新人盲玩、完整周目或人类审美通过证据。配乐重制暂停。
