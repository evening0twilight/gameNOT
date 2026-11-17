# Qwen 营地音频试作

用户本轮重新授权尝试阿里云模型，并提供了业务空间。只使用本机 .env 中 aliyun-apikey，不保存或展示密钥；响应的临时签名下载 URL 仅在被 Git 排除的 work 目录。游戏没有接入模型服务。

Fun-Music 请求返回 HTTP 403 / AccessDenied。Qwen Audio 第一次响应连接中断；第二次成功生成44.96秒WAV，HTTP下载超时后从同一生成结果用HTTPS恢复，没有再次生成。完整提示、实际返回的usage、文件哈希、失败尝试和测量见 audio-model-review.json。不能从第一次断连推断是否计费，也不报告无法核实的总费用。

原文件为48kHz、双声道、16-bit PCM。平均-16.2dBFS，峰值0dBFS，有33个满幅样本；降低试听音量不能修复已经发生的削波。Qwen Omni独立自动听辨认为无说话/歌声、以钢琴和弦乐为主、抒情柔和稍伤感，且结尾突然截断。该结果是模型辅助描述，不是人类听感验收。

camp-audition-fade.mp3 为试听版本：降3dB，并将最后1.96秒淡出。原WAV未覆盖。试听文件不能声称无缝循环、完整混音或正式配乐完成；本轮没有替换 production 音轨。若继续制作正式营地曲，需处理循环接缝、峰值与响度、长时间重复耐听度，再与对白/操作提示共同混音。

文档来源：[音频生成接口](https://help.aliyun.com/en/model-studio/audio-generation-api)、[Fun-Music](https://help.aliyun.com/zh/model-studio/fun-music/)、[Omni 音频理解](https://help.aliyun.com/en/model-studio/qwen-omni)。实际账号可用性以本次请求收据为准。

原WAV与试听MP3保留在仓库outputs/aliyun-audio-20261117，并单独交付试听；它们不在Windows游戏包内，包中的正式音乐未更换。随包说明中的文件哈希指向这些外部试作证据，不表示已接入PCK。
