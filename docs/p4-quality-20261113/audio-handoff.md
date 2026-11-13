# 本候选声音范围

本轮保留p4art-20261113的全部音源；随附audio-generated.json/audio-inventory.json是声音制作聊天的原始资源清单副本，哈希对应同一文件，未改为模型生成素材。

运行混音新增：等功率交叉切换；关键伤势/目标提示短时压低伴奏后恢复；常用界面/机器音量平衡；脚步确定性轻微音高变化；共享主输出-1dB限幅。独立音量、静音、暂停/跳过的原机制保留。统一检查中的80项音频回归与p4quality专项检查对应当前控制器。

现有音乐的音色、循环长度及情境差异问题仍未解决。OpenAI语音接口没有交付本项目所需器乐；用户已明确没有适用接口就先算了，因此暂停配乐重制。模型对72秒串听样本的辅助分析见audio-model-review.json（非人耳验收）。没有运行时API或密钥依赖。

官方接口定位参考：[gpt-audio-1.5](https://developers.openai.com/api/docs/models/gpt-audio-1.5)、[音频输入/输出指南](https://developers.openai.com/api/docs/guides/audio-chat-completions)。停止重制的依据是本次可用接口与实际尝试结果，不是对未来模型的判断。
