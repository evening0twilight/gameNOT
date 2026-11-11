夜潮事务所 — 0.18 开发前设计基线（2026-11-04）

本轮仍未进入正式开发。当前Godot工程只有基础准备模块，不是完整可玩游戏。
当前手册：../outputs/full-game-design.html
本轮审查：../outputs/predevelopment-review.html
唯一规则入口：data/final_design/design_manifest.json
唯一规则内容：data/final_design/release_baseline.json
领域JSON是生成投影，不可独立改成另一份规则。旧报告仅保留历史证据。
后续维护：修改release_baseline.json → python3 work/predevelopment-review/export_views.py → 必要回归 → build_report.py → verify.py。
consolidate.py和finish_design.py是本轮一次性的历史迁移记录，不是后续重新套补丁的维护入口。

当前范围：俯视2D 8×8、3人2AP、8角色、24主线+12支线、16能力、7装备、4情境协作。
本地引擎：../work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot
Godot 4.7.2 standard / GDScript / Compatibility；首发Windows 11 x64键鼠简体中文。

设计回归：python3 work/predevelopment-review/regression.py （在工作区根目录）
整局回归：python3 work/ordinary-player-review/campaigns.py --output predevelopment-campaigns.json
本轮检查：python3 work/predevelopment-review/verify.py
当前阅读页生成：python3 work/predevelopment-review/build_report.py
旧work/*/apply_design.py、sync.py、rebuild.py均是旧版重建工具，不用于当前版本；运行会被投影/指纹检查发现。
正式程序与真人验收标准见data/final_design/acceptance.json，不用离线通过替代实机证据。
