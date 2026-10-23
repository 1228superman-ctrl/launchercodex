[English README](README.md)

# Codex 动漫启动器 | Codex Anime Launcher V2.0 Beta

**把任意用户选定的动漫／原创主题制作成 Codex 启动动画，并可选安全接入 Windows 启动快捷方式。**

此包是 ChatGPT / Codex 等 Agent 可调用的 **Agent Skill**；提供 `SKILL.md`、可运行视频与音频处理脚本、主题配置、Windows 快捷方式脚本及 Gojo V13 实际剪辑案例。没有授权的音乐、动漫原画、旧 Codex 录屏或商业软件不会打包进来。

## 快速使用

1. 将 ZIP 解压后的整个 `codex-anime-launcher` 目录放在个人 `~/.agents/skills/` 或项目 `.agents/skills/` 下（需实际运行端支持 Agent Skills）。目录下应直接存在 `SKILL.md`。
2. 对 AI 助手说：**“使用 codex-anime-launcher Skill，帮我制作一套某某主题的 Codex 启动动画，包括图标、背景和 V13 风格的渐强配乐；先检查环境、展示方案，等我确认后再执行。”**
3. 若只要视频，完成分镜 → 提供或生成合法素材 → 制作无声画面 → 配乐 → 验收即可。**不必改本机 Codex。**
4. 如需真正点击快捷方式就播放动画，需要额外按 `docs/windows-setup.md` 接入外部启动器，检查现有 Codex 安装与播放器 `mpv`。

## 自带工具

- `scripts/check_environment.py`：只读 FFmpeg/音视频检查。
- `scripts/build_animation.py`：把用户已有的视频片段标准化拼接，导出横/竖版无声画面。
- `scripts/generate_sound_effects.py`：按分镜时刻生成打字、鼠标滚轮、图标点击轻音效。
- `scripts/sync_music.py`：**旧音轨完全丢弃**；角色出现后音乐随动画渐强，末尾淡出。
- `scripts/verify_output.py`：全片解码、时间、音量、视频流一致性报告。
- `scripts/Inspect-CodexEnvironment.ps1`：Windows 只读 Codex 环境检查。
- `scripts/New-CodexAnimationShortcut.ps1`、`Start-CodexWithAnimation.ps1`、`Restore-CodexShortcut.ps1`：Windows 外部入口与恢复。

## 从 V13 示例开始

V13 完整长度为 22.208 秒。`examples/gojo_v13_audio_timeline.json` 记录：2.39 秒打字结束、滚动段无背景音乐、7.625–10.625 秒图标转场无音乐、10.625 秒开始歌曲渐强、19.375 秒开始淡出。样例中歌曲设为用户自行提供的曲目第 55 秒，不随 ZIP 分发。

```bash
python scripts/generate_sound_effects.py --timeline examples/gojo_v13_audio_timeline.json --output work/v13_foley.wav
python scripts/sync_music.py --video work/v13_silent.mp4 --foley work/v13_foley.wav --music assets/YOUR_LICENSED_MUSIC.mp3 --timeline examples/gojo_v13_audio_timeline.json --output exports/v13_music.mp4
python scripts/verify_output.py --video exports/v13_music.mp4 --compare-video-to work/v13_silent.mp4 --timeline examples/gojo_v13_audio_timeline.json
```

执行前替换路径并确保无声视频真实时长与 JSON 一致；其他长度必须重新标注时间点。脚本不生成图片、角色、原作录音，不扫描或修改个人数据。

## 界限与风险

- 图片背景不一定是 Codex 原生功能；不得把后期合成镜头说成真实软件美化成功。
- 仅创建/替换 `.lnk` 快捷方式，不修改应用包；任务栏原图标不一定自动切换。
- `mpv`、FFmpeg 和生成素材由用户自行提供合法来源并检查。
- 商业动画人物与音乐用于发布可能需要授权，不能因为是 Skill 示例就认为可以商用。
- 当前已对 Python 媒体流程执行离线功能测试；Windows 快捷方式脚本需在目标机器上按说明实际测试。

文档标准参考：[OpenAI Skills 官方说明](https://developers.openai.com/api/docs/guides/tools-skills)。

## 开源版补充说明

- 这是**可复用的 Skill 和剪辑工具**，不会从文字自动生成动漫原画或视频；先提供合法素材。
- 原生 Codex 图片聊天背景及 Windows 快捷方式在其他机器上的兼容性尚未全量验证。
- 运行 `python -m unittest discover -s tests -v` 可进行无需个人视频素材的技术自检。
- 商业音乐和动漫角色版权不包含在 MIT 许可内；本项目为非官方社区项目，不代表 OpenAI。
