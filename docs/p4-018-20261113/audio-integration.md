# 主对话共享入口接入记录

2026-11-13：已按 audio-handoff.md 接入 main.gd 的 scene_music、schedule 暂停回调、finish_feedback(completed)；增加 button 的可选 cue 参数以避免翻页叠加 ui_focus。story_screen 的页码/速览按钮用 ui_page，窗口用 scene_music。campaign_screens 首次接触绑定 daily，手动保存成功才播放 ui_save。等待音频对话的新接口稳定后共同检查。主对话继续美术，未开始全量检查/构建。

已补齐 contextual_events（失败不响成功音、中继增援提示）与剧情翻页先 hide 后释放，主工作区80项音频检查通过，见 outputs/p4art-audio.log。
