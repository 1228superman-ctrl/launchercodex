---
name: codex-anime-launcher
description: "Create Codex anime-style startup videos with synchronized keyboard, scrolling and reveal music, and an optional reversible Windows shortcut. 为 Codex 制作可复用的动漫主题启动动画、聊天背景设计和自定义图标，按分镜生成视频并合成精准键盘/滚轮/点击音效及角色登场渐强配乐；可选安全接入 Windows Codex 启动快捷方式并验收回退。适用：Codex 五条悟启动动画、Codex 启动特效、Codex 主题美化、动漫视频配乐、修改桌面快捷方式图标。"
---

# Codex 动漫启动器 | Codex Anime Launcher · V2.0 Beta

## 启动原则

这是一个 **Skill（流程+模板+脚本）**，并非已经安装好的启动动画，也不自带第三方人物插画、视频、音乐、程序或播放器。不会自动突破当前机器 Codex 原生主题能力。核心目标：把用户提供或合法生成的素材制作成「真实操作 → 图标转场 → 动漫角色显现 → Codex 界面」视频，按已验证的 V13 分段逻辑进行配音效，可选通过独立 Windows 快捷方式在播放后启动真正的 Codex。

1. **每次先分析需求 → 展示计划、将修改的路径与风险 → 等用户明确同意 → 才调用写入/安装/改图工具。** 制作视频和改 Codex 系统入口是两个独立的授权阶段；不得以同意做视频推定同意修改软件入口。
2. 优先检查现有环境、现成 GitHub/官方解决方案与工具版本，能复用不重装；先验证安全、兼容性、成本。只读检测可先做；明确不做系统级静默安装。
3. **图像生成与编辑必须使用图像生成工具**，不可用 Python 代画、Pillow/OpenCV 改人物造型。FFmpeg/Python 在本 Skill 里只负责视频归一化、拼接、声音合成、时轴与验收。
4. 屏幕录制不得泄露私人聊天、客户资料、账号或 API Key；先裁剪/重录安全演示场景。避免用粗糙马赛克补救展开的历史侧栏。可用无敏感内容的演示素材代替。
5. 不修改 Codex 核心程序、安装文件、ASAR、WindowsApps、注册表或安全设置；默认只新建外部快捷方式。不能保证原生支持图片聊天壁纸；需实机核查。见 [背景边界](references/background.md)。
6. 真实 Codex 界面和视频里后期合成的 Codex UI 要明确区分；禁止拿后期合成演示冒充当前客户端已经生效。
7. 不分发未经授权的动漫插图、电影剪辑、商业音乐。用户可提供自有或有权使用的音频；不能把上传过的《SPECIALZ》直接放进公开 Skill。

## 识别用户想要的产物

分别确认：A 展示用横/竖版 MP4；B 日常简短启动片；C 聊天区域真实自定义主题；D 快捷方式/图标/任务栏入口。**不要把 A 的成功声称为 B/C/D 均已完成。** 用户只想要视频时，不做任何 Windows 改动。

## 流程（先方案，确认后分阶段执行）

### 1. 检测（只读）

- Windows 环境：`scripts/Inspect-CodexEnvironment.ps1` 检查 Codex 快捷方式、ffmpeg、mpv（无需管理员权限）。其他操作系统改用对应方案，不执行 Windows 脚本。
- 通用媒体：`python scripts/check_environment.py --video INPUT.mp4 --music YOUR_MUSIC.mp3`。
- 与用户核实角色、是否露脸、横竖屏、展示或实际启动、音乐来源与使用范围、素材源、配色/设备限制。整理**变更清单**，确认后再制作。

### 2. 分镜与画面来源

- 填写 [分镜模板](templates/storyboard_template.md) 及 [主题配置](templates/theme_config.json)，记录镜头事件实际时间（不是按固定时长比例猜测）。
- 首帧、壁纸、图标插画走图像生成工具；动画片段走用户实际可用的视频模型、剪辑或安全录屏。需要稳定的图标位置、没有完整隐私对话、无意外侧栏弹出和突兀马赛克。
- 已有完整片段可执行 `python scripts/build_animation.py --clips clip1.mp4 clip2.mp4 --output render/video_silent.mp4 --portrait-output render/video_vertical_silent.mp4`。脚本仅拼接传入的视频，**不会自动生成镜头、视频素材或图片**；最终播放时长必须实测。

### 3. 配乐流程（V13 经迭代后的默认结构）

读 [音频制作说明](docs/audio-design.md) 与 [V13 实例](examples/gojo_v13_workflow.md)。核心是让音效跟画面发生的动作绑定：

| 画面阶段 | 默认音轨 |
|---|---|
| 键盘输入 | 有节奏的敲击声，不加背景音乐 |
| 聊天记录向下滚 | **只有滚轮声**，随实际滚动出现，不加背景音乐 |
| Codex 图标出现及点击转场 | **无背景音乐**，仅轻微图标和点击音效 |
| 角色开始显现 | 有权使用的歌曲从指定时间点切入，音量由小增大 |
| 角色显现完整 | 音乐达到设计峰值，但要留足响度余量 |
| 最终 Codex 界面 | 音乐随视觉收尾淡出 |

修改 [audio_timeline.json](templates/audio_timeline.json) 的真实时间节点和音效事件，然后生成并混音：

```bash
python scripts/generate_sound_effects.py --timeline templates/audio_timeline.json --output work/foley.wav
python scripts/sync_music.py --video work/video_silent.mp4 --foley work/foley.wav --music assets/YOUR_LICENSED_MUSIC.mp3 --timeline templates/audio_timeline.json --output exports/intro_with_audio.mp4
python scripts/verify_output.py --video exports/intro_with_audio.mp4 --compare-video-to work/video_silent.mp4 --timeline templates/audio_timeline.json --report exports/qa.json
```

`sync_music.py` **明确丢弃输入视频的旧音轨**，仅使用新生成的打字/滚轮/图标音效和用户提供的音乐，防止前半段有旧背景音乐残留。它支持歌曲截取起点、音乐基底音量、渐强时长及结尾淡出。音乐一开始必须**发生在 `reveal_start`**，并非 `icon_start`。若用户只要音效、不加歌曲，可省略 `--music`，得到全段仅操作音效的版本。生成输出绝不覆盖原文件。

### 4. 视觉主题和系统接入（另行征求确认）

- 优先使用 Codex 当前版本真实存在的设置项；可用原生背景配色 != 支持导入任意动漫图片。必要时注明只能制作视频演示。参考 [背景限制](references/background.md)。
- 只在 Windows 用户同意并检查原始 `.lnk` 后，使用 `scripts/New-CodexAnimationShortcut.ps1` 创建独立动画入口；默认**不替换**原始快捷方式。播放器建议 `mpv`，不随包分发、不自动下载。
- 先测试独立快捷方式；仅当用户明确要求替换常用桌面 `.lnk` 才使用 `-ReplaceOriginal` 并备份。改的是快捷方式 `IconLocation`，**不是 Codex 的官方应用程序图标**；任务栏是否转向新入口须手动验证。
- 具体步骤见 [Windows 安装](docs/windows-setup.md) 和 [恢复](docs/restore.md)。

### 5. 验收与交付

- 视频：音画时间轴、首尾、画面比例、编码、文件完整解码，横/竖版抽帧人工检查，人物与镜头不穿帮、无异常黑屏、无隐私。
- 声音：滚动段确实没有歌曲；图标转场确实没有歌曲；滚轮/点击不过强；角色显现音乐逐渐增强、进入主题界面逐渐淡出，避免削波。脚本报告响度仅作辅助，**必须实际观看试听**。
- 系统：双击新入口播放动画并启动真实 Codex；关闭或跳过动画仍可正常打开；登录/工作区未受影响；快捷方式备份可恢复。尚未 Windows 实机测试时不要声称已验证。
- 交付日志明确列出哪些是**真实已实现**、哪些只是演示镜头、哪些缺少素材/授权、哪些需要用户下一步确认；每次修改新建 V2/V3 文件，不覆盖已验收的版本。

## 辅助文件索引

- `README.md`：给最终使用者的最短教程。
- `examples/gojo_v13_workflow.md` / `examples/gojo_v13_audio_timeline.json`：我们最终认可的 22.208 秒音乐时间轴及返工经验（**只有配置，不含音乐和视频**）。
- `docs/audio-design.md`：细化音效事件、FFmpeg 混音逻辑、调参诊断。
- `docs/windows-setup.md` / `docs/restore.md` / `docs/verification.md`：安装、恢复、验收。
- `references/storyboard.md` / `references/background.md`：视觉创作与官方界面能力边界。
- `scripts/*.py`：跨平台（Python 3.10+，FFmpeg 必需）媒体拼接、音效、音乐同步、验证。
- `scripts/*.ps1`：Windows 快捷方式启动器、环境检查和恢复（仅授权后运行修改性脚本）。
