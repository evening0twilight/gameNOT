# 0.18 本机清理记录 · 2026-11-11

用户报告 Windows 包已经验证过，并授权删除本机安装包。未收到实测端的包哈希、逐项结果或性能数据。原 [0.18 构建收据](product018-build.json) 原样保留，记录的是 2026-11-07 的构建与 macOS 导出检查；其中 `windows_native_tested=false` 是当时构建端的状态。此次清理未关闭 P4 最终验收。

| 删除项 | 本机清理量 |
| --- | ---: |
| `build/` 内 7 份 Windows ZIP 及对应解包导出目录（P2、P3、P4、P4 feedback、P4 tuning、baseline018、product018） | 1,658,724 KiB |
| 两段旧原始 AVI 和 60 张 0.18 逐帧 PNG；保留对应 MP4 和渲染记录 | 223,704 KiB |
| Godot 全平台模板下载压缩包；保留本机锁定引擎与已安装的 Windows x64 模板 | 1,251,320 KiB |
| 34 份已在 `archives/evidence/` 逐字节归档的历史证据解包副本 | 348,260 KiB |
| 项目内 Godot/Python/Finder 缓存、旧引擎检查输出和历史预览浏览器会话 | 79,040 KiB |
| 35 张 P3 和 36 张 P4 feedback 历史回放截图的同字节副本 | 50,936 KiB |
| 合计（删除前按路径计的磁盘占用） | 3,611,984 KiB（约 3.44 GiB） |

七份 ZIP 删除前均核对过原收据的大小和 SHA256。原 `build/night-tide-0.18-windows.zip` 为 114470678 字节，SHA256 `b88172277556b058b07b67fd39174521cfd16d567d65bbfc5bdd009c24a65a11`。安装包不在 Git；以后按[交接文档](NEXT_AGENT_HANDOFF.md#6-新账号新克隆如何启动)重新导出。下载压缩包已与工具链锁定哈希比对，已安装的两个 Windows 模板及版本文件也与压缩包内原件一致。

游戏源码、运行素材、冻结设计、存档、构建收据、全部历史回放 JSON、独有截图和包含独有文件的本机阶段快照均保留。历史截图的保留路径见 [移除清单](product018-history-retirements.json)；原始路径仍可从清理前提交 `c7de36a` 取回。压缩归档原件可用 `python3 tools/evidence.py` 恢复，清理前已校验每份归档及其解包副本。

清理前 287 个受保护路径逐一匹配原哈希。清理后默认检查核验现存的 244 个路径，将 5 份旧 ZIP、2 段 AVI 和 36 张重复截图单独记为 `history.retired`，`history.missing=[]`，`history.complete=false`。这些重复截图的保留副本仍在原哈希清单内；其缺失、损坏或恢复了内容不符的旧文件，都会使当前检查失败。旧报告和原保护哈希清单不回填清理后的状态。

在临时目录验证了无历史本地文件的仓库快照：9 个历史完整性单元测试和 `check_product018.py --full` 的 29 组检查通过；`build_windows_product018.py` 导出通过，检查了 PE x64、macOS 上独立启动资源包以及 ZIP 和内部文件的完整性。临时 ZIP 为 114470984 字节，SHA256 `4ebc8e805732f9a6e7a5ccd722aea48d76cccd1ef7200ab3ddefcfa77ada6d50`，验证后随临时目录删除。此次导出没有在 Windows 上运行，没有覆盖仓库的原构建收据和原检查日志。
