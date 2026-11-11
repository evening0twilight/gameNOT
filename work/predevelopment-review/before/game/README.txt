夜潮事务所 — 正式产品工程准备版
设计版本：0.15（当前继续设计，暂不进入正式开发），2026-11-03
引擎：Godot 4.7.2 标准版，GDScript，Compatibility 渲染。

当前工程不是完整游戏。入口只加载人物与关系数据，用于确认正式工程可以启动。
完整设计：../outputs/full-game-design.html
真实实现状态：docs/development.json
本轮检查结果：docs/engine-checks.json、docs/design-checks.json

本工作区下载的引擎位置：
../work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot

在工作区根目录运行：
  work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --editor --path game
  work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot --headless --path game --script tests/run_tests.gd
  python3 game/tools/validate_design.py
  python3 game/tools/build_product_document.py

主要结构：
  data/                 正式产品的数据基线、内容提纲、规则与状态契约
  scripts/domain/       无 UI 的规则与存档基础模块
  scripts/app/          启动入口；尚无完整战役界面
  scenes/               Godot 场景
  tests/                在真实 Godot 引擎中执行的检查
  tools/                内容登记与结构检查工具
  docs/                 实施状态与生成的检查记录

数据编辑注意：
  data/final_design/ 是当前关卡、人物分支、战斗、装备与跨系统衔接的权威规范。
  0.4基础作者源在 ../work/final-design/build_*.py；整局、系统和战术修订依次在 ../work/campaign-review/、../work/system-audit/、../work/tactical-review/，由同一流程按序应用。
  当前完整设计与推演的重建命令（工作区根目录）：
    python3 work/final-design/rebuild.py
  重建顺序包含内容生成、地图/状态检查、人物承诺、36关逐动作与组合检查、实际战斗接整局、兼容数据同步与HTML文档。
  game/tools/build_product_document.py 仅重新生成当前HTML，不会退回旧设计。
  旧0.2/0.3生成器已经禁止直接运行；历史HTML保留。
  外层人物背景、初始关系与需求表继续维护，sync_legacy同步任务、规则和装备的当前引用。
  检查脚本是正式产品的设计工具，不是另一套待发布游戏。
  静态路径排程不等于全战斗；0.7另有36关逐动作参考推演，范围见战术报告；Godot完整战役仍未实施。

执行约束：
  最新指示：暂不进入正式开发；当前只完善设计与校验。
  后续进入开发时沿用同一个最终项目，不另做丢弃式网页版本。
  不在本对话处理发行、提交费用、商店或对外发布。
  新战斗系统不能沿用旧 Python 探针的结果声称已经平衡。
  纯规则测试通过不等于真人体验、全部剧情、完整时长或 Windows 兼容性通过。
  用户已确认：失败仍到结局；常规难度仅重伤，最高难度可永久离队且需披露；冲突不剥夺基础行动控制。
  具体采用最高难度超出明示救援期限后永久医疗离队的设计；不是随机死亡。

0.6系统性逻辑审查：../outputs/systematic-logic-audit.html；规范 data/final_design/system_audit_contract.json；验证 work/system-audit/verify.py（工作区根目录）。仍仅设计，未改正式运行代码。

0.7 战术审查：../outputs/tactical-playability-review.html。36关逐动作参考推演、组合检查与整局账本，不是正式游戏实现或真人游玩结论。

0.8 引导、人物视觉与情境评价：../outputs/player-experience-design.html；规范 data/final_design/player_experience_contract.json。保留0.7战斗与0.6记忆存储，新增评价入口只做离线设计推演，未实现正式教程或情绪系统。

0.9 全局整合复审：../outputs/integrated-design-review.html；规范 data/final_design/integrated_review_contract.json。具名阵容、实际战斗整局、单一关系结算、贡献防刷和提示调度；新增检查在 ../work/integrated-review/，重建流程已接入。仍不是正式游戏功能实现。

历史0.10 阵容解法与高级合作：../outputs/approach-design-review.html；规范 data/final_design/approach_review_contract.json。12关增加可选现场服务、合作的精确用法及设备维修的项目成本；原主目标保留。当前仍仅设计与离线推演，未改正式运行代码。

历史0.11玩家选择审查：../outputs/player-choice-review.html
玩家选择规则：data/final_design/player_choice_contract.json
0.11：4处不同现场操作，取消8处重复值守；两座限期后勤设施；掩护无需训练；接力与定向牵引随合格的普通双人训练学会。仍为设计阶段。

当前0.12高级合作价值与制作范围：../outputs/cooperation-value-review.html
正式范围：data/final_design/production_scope.json；16项专长、7种装备。取消独立合作培养分支，保留四项有具体关系条件的现场协作。5级强化第一专长次数。仅设计与离线推演，不是完整产品实现。

0.13审查：../outputs/growth-identity-review.html
战斗形式：俯视2D、8×8网格、三人全队回合；非卡牌/3D阵列战斗。
当前养成与关系契约：data/final_design/growth_identity_contract.json。
离线设计模型与检查：../work/growth-identity-review/；未改正式运行时代码。

0.14全域审查：../outputs/full-audit-review.html
当前规则权威入口：data/final_design/design_manifest.json。
审查修订源与当前全量检查：../work/full-audit/。0.13报告保留为历史，不能覆盖0.14医疗、工坊、改约与归责规则。

0.15当前修订：../outputs/player-ready-review.html
人物完整剧本：../outputs/character-script-final.html
当前设计复核：python3 work/player-ready-review/rebuild.py（在工作区根目录；只处理设计与离线模型）
0.14及更早报告属于历史；当前经济、角色修订与人物全文以0.15为准。
