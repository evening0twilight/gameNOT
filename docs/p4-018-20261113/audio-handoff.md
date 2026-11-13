# 0.18 音频接力 · 2026-11-13

状态：音频资源、控制器和专属工具已稳定；隔离副本已验证完整共享接点。主对话已合入两处共享修改，负责最终统一检查和 Windows 导出。新曲和短音仍待用户听感确认，未关闭 P4。

## 共享文件接入（主对话处理）

- `story_screen.gd` 已有 daily/grave 路由；逐页或速览会先创建新窗口、随后旧窗口退出，旧窗口的回调会把新窗口的音乐覆盖为营地曲。将现有两行替换为 `ui.sound.scene_music(dialog.window, "grave" if view.tone=="grave" or view.delivery.mode=="letter" else "daily")`，并在上页、下页、速览/全文按钮的处理内加 `ui.sound.play("ui_page")`。同一音乐上下文换页应保持播放位置。建议通用按钮辅助支持可选 cue 参数，避免同一次翻页还叠加 ui_focus。
- `main.gd` 的冲突窗口将原来的 `sound.ambience("grave")` 和退出回调替换为 `sound.scene_music(dialog.window, "grave")`。在 `campaign_screens.gd` 的人物初见窗口同样绑定 daily；最终结局的底层音乐仍由 `music_context()` 决定。
- `main.gd` 的 `commit_pending()`：`sound.schedule(sound.contextual_events(feedback_plan, previous_state, session.state), visual_started, feedback_seconds, func(): return paused)`；在 `_process` 自然到期时用 `finish_feedback(true)`；将 `finish_feedback(completed: bool=false)` 中原 `sound.cancel_timeline()` 替换为 `sound.finish_timeline() if completed else sound.cancel_timeline()`（GDScript 用常规 if/else）。自然结尾允许已到点的提示响完，Space/取消/返回标题仍传默认 false 并停止在播的战术音。请保留背景音乐与菜单音在暂停菜单可播放。
- `campaign_screens.gd` 的 `write_manual`：只在手动保存成功后用 `ui.sound.play("ui_save")`，不响自动存档。
- 初审纠正：daily 有真实剧情入口，缺口是窗口切换后被覆盖，而不是资源从未接入。24个正式短音中 ui_page/ui_save 无入口；旧文件夹还有若干同名替代和未接入的历史素材，不能把文件总数作正式音效数。

## API 小样

官方 [模型页](https://developers.openai.com/api/docs/models/gpt-audio-1.5) / [Chat Completions 音频指南](https://developers.openai.com/api/docs/guides/audio-chat-completions)。授权额度的 `GET /v1/models/gpt-audio-1.5` 与 `POST /v1/chat/completions` 均 HTTP 200；返回模型 `gpt-audio-1.5`。请求 `store=false`，text+audio，alloy/WAV，最多 220 输出 token。提示：“Output only an isolated, non-vocal game sound effect: one dull metal relay click, then one short electrical hum tail. The whole sound should last under one second. No speech, explanation, imitation by mouth, music, or other background.” 返回 8.4 秒口头说明，自述无法直接生成音效；输出达到上限。测试 WAV 的 SHA256 为 `7f6a1af9f77a7ecfe183cddd04e0a911bd2f661cdcd841abb24a57d807469a2e`，只保存在本机系统临时目录。此探测验证了账号和音频能力，未得到可用非语音素材，未批量调用或导入语音。正式制作走工程内原创合成，保留历史来源和资产。

**补充共享接点：** `sound.schedule` 的第一个参数请使用 `sound.contextual_events(feedback_plan, previous_state, session.state)`（其余参数保持）。这一步过滤“进结算一律播放成功音”，按真实完成目标/成功/结局选择提示；也依据中继器造成的增援预告或登场状态补上 `machine_relay`。沿用战术界面已有的对象进度、结算结果和增援标记。

窗口补充：`story_screen.gd` 翻页/速览目前先 `queue_free()` 再创建 exclusive modal；验证时捕捉到同一父窗口还有旧 exclusive child 的 Godot 报错。建议翻页/速览的回调先 `dialog.window.hide()`、再 `queue_free()` 并创建新页，保持旧 owner 到树退出时才释放音乐；测试可用 L01 的“全文速览与选择”（L01 只有一页）。

候选包：`docs/product018-audio.json` 是旧版记录。请主对话在本次包中另附本目录的 `audio-generated.json`、`audio-inventory.json`、`audio-handoff.md`，并把新的资产路径/来源合入共用资产表。不要用旧三曲记录代表新版清单。

## 已稳定的音频工作

- 新制四首立体声循环：普通任务（82 BPM）、紧迫任务（106 BPM）、人物日常（78 BPM）、沉重事件（58 BPM）。保留原营地/标题与结局两首。新曲用八小节和弦、独立声部、跨边界的包络和延迟尾巴；无运行时动态作曲。六首之间线性振幅交叉淡化 1.2 秒，快速切回可恢复仍在淡出的曲目位置。四首新曲与 12 个短音源码 WAV 共约 9.3 MB，历史目录未删除。
- 正式 24 短音分组 6 界面、8 动作、6 机器、4 目标/伤势。保留六个界面、移步/作业/稳定/撤离以及回合/终局；替换打击、推、拾取、放下、伤势、目标完成及六种机器音。动作音保留与路径/命中时点同步，动效暂停只冻结现场声和待播序列，跳过取消待播及现场尾音；菜单和音乐仍可听。动效关闭时仍有对应即时短音，不代替文字/画面。
- 新 WAV 与 Godot 导入参数：`game/assets/product018/audio/nov13/`。制作脚本 `tools/generate_audio_nov13.py`；[原创合成配方和哈希](audio-generated.json)、[30个运行素材路径、哈希和测量](audio-inventory.json)。源文件声峰值、均方电平和循环边界均已核验；六曲边界附近 0.2 秒均有信号，邻点波形斜率残差 0–2 PCM16 单位。该测量来自源 PCM；Godot 导入后实际播放器另验证了普通任务曲跨边界。
- 音频负责人写入范围已稳定：上述 WAV 和 .import、`audio_controller.gd`、音频专用生成/核对脚本及 `game/tests/p4_audio_nov13.gd`。共享文件仍由主对话整合；截至本次隔离检查，主工作区已接上初见、剧情窗口所有权、界面提示和暂停/自然结束。增援/结算过滤调用及独占窗口关闭顺序已由主对话合入；从主工作区复制当前源码和素材到新隔离副本复跑，80 项音频和 89 项动作检查通过。高频切歌测试曾在 headless 退出时报告 WAV 播放引用清理警告；给 dummy mixer 留出启动和清理时间后，同一源码副本连续三轮通过且无该警告。目标机持续运行内存须另测。

## 隔离复核

锁定 Godot 4.7.2，macOS headless dummy audio。新建独立工程副本和独立存档，无外放或占用屏幕；测试源文件自身运行时不需要 FFmpeg 或 API。隔离副本已纳入上面的两处共享接入修改，非 Windows 导出包。

- `P4_AUDIO_NOV13: checks=80 failures=0`；`P4_FEEDBACK_RESULTS: checks=89 failures=0`。新测试实际启动 Godot 播放器并跨过普通任务曲边界，验证过渡、快速返回、音量/静音存取、正式 UI 提交 M01 移动和结束回合、暂停时播放位置/队列不走、继续、跳过与自动结束、L01 速览切换和手动保存。紧迫阈值及冲突窗口使用隔离场景；M03/M05/M06/M10/M11 使用定稿地图和真实回合 reducer（直达地图，无连续周目宣称）。M11 真实增援预告和生成各出一次音，失败结算不响成功音。结局读回已有连续第 24 日存档（SHA256 `fb9b361cf4faff1fed21654c9340230d0820657b416522e7b956ded18fee1433`）。
- 复现（主对话合入共享接点、导入素材后）：`"$GODOT" --headless --path game --script res://tests/p4_audio_nov13.gd -- "$PWD/outputs/baseline018-linked-day24.json"`。单独复查素材/导出样例：`python3 tools/review_audio_nov13.py --previews outputs`。未跑全量入口、未导出或测试新的 Windows 产物、未提交推送。

## 试听索引

- `outputs/p4-audio-nov13-music.mp3`（72 秒）：00:00 营地、00:12 普通任务、00:24 紧迫任务、00:36 日常、00:48 沉重事件、01:00 结局。每段约第 5 秒越过源循环边界。SHA256 `f07acb55d55d3dab11a369e5c0e2a5c0cfa6f39202bf5e58284eaf089ea3b0ef`。
- `outputs/p4-audio-nov13-sfx.mp3`（24 秒）：逐秒按 [清单顺序](audio-inventory.json)；0–5 界面、6–13 动作、14–19 机器、20–23 回合/伤势/目标/结局。SHA256 `3e7e57755aa243374e438a619c2843d649b11b861d02cecbd91061caf6c86919`。
- `outputs/p4-audio-nov13-field-mix.mp3`（19 秒）：示意混音，9 秒开始切到紧迫曲，15 秒后撤离/完成。采用默认滑块比例并整体放大约 6 dB 供试听；不是运行时录音。SHA256 `19fc6d5e40ddba01c894635ea8520a0d5de98201ad09da8d8ba5be7bb09beddc`。

听感由用户在耳机/目标 Windows 扬声器分别确认；重点听紧迫度差异、连续脚步/机械不盖关键信息、长时间循环是否疲劳、交叉淡化和 UI 音大小。新资产未获听感批准，P4-018-02/03 仍待主对话出包及用户验收。
