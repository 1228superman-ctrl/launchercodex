# Windows 安装与 Codex 快捷方式配置（分阶段授权）

**确认已获用户允许修改指定快捷方式后再执行写操作。** 只想导出视频，不需要做这一步。参考 `references/background.md` 区分真实软件主题和视频里的视觉素材。

## 前提

- Windows 10/11、PowerShell 5.1、真实可用的 Codex 安装及原始 `.lnk`；通过 `scripts/Inspect-CodexEnvironment.ps1` 检查，不猜路径。
- 用户提供制作好的 `intro.mp4`、可选 `icon.ico`，以及从可信渠道安装的 `mpv` 播放器（可留空，缺失时跳过动画）。
- 独立文件夹存放视频和工程（例如 `D:\MyAnimeCodex\`），不要把素材放到桌面；桌面只适合快捷方式。

## 只读检查

```powershell
powershell.exe -NoProfile -File '.\scripts\Inspect-CodexEnvironment.ps1'
```

## 默认：新建独立快捷方式

按实际电脑**改写全部示例路径**：

```powershell
powershell.exe -NoProfile -File '.\scripts\New-CodexAnimationShortcut.ps1' `
  -CodexShortcut 'C:\Users\YOU\Desktop\Codex.lnk' `
  -VideoFile 'D:\MyAnimeCodex\exports\intro.mp4' `
  -ProjectRoot 'D:\MyAnimeCodex' `
  -IconPath 'D:\MyAnimeCodex\assets\icon.ico'
```

- `ProjectRoot\backup\`：原始快捷方式备份。
- `ProjectRoot\launcher\`：启动器脚本副本。
- `ProjectRoot\shortcuts\Codex-Anime-Launcher.lnk`：**新增的入口**。
- 第一次双击新快捷方式实测：完整播放视频后进入**真实 Codex**；缺少 mpv 时会尝试直接启动 Codex。图标/动画快捷方式是外部包装，不是修改 Codex 程序。

**仅在新入口验证通过并得到另一次明确同意后** 才可加 `-ReplaceOriginal` 替换选中的原始 `.lnk`，绝不自动修改任务栏所有图标；任务栏可能需要重新固定，仍需人工点一次验证。

## 图标来源与修改

先用图像生成工具制作独立方形图标，并用安全工具导出合法 `.ico`；本 Skill 的 Python 不修改图片。 `-IconPath` 仅影响这个 Windows 快捷方式（不是打开后的程序内置图标）。

## Codex 背景

先使用当前版本设置菜单中存在的原生颜色、主题等功能。若没有官方导入图片背景的选项，不要通过此 Skill 强制修改安装资源。用户若要求壁纸，只交付视频/壁纸设计，或在另一个独立授权步骤评估社区方案与风险。主题恢复应从真实设置中操作。

## 跳过、失败与恢复

启动器设计为播放器缺失/视频缺失时，尽可能直接打开备份的原始 Codex 快捷方式。异常时先看 `mpv` 播放能力与备份文件。恢复脚本见 `docs/restore.md`。
