# 恢复 Windows 原始 Codex 启动入口

前提：事先由 `New-CodexAnimationShortcut.ps1` 自动留有 `.lnk` 备份。**先查看路径并征求恢复许可。**

## 未替换旧入口的情况

若只是创建了 `shortcuts/Codex - 动画启动.lnk`，用户可以删除该新快捷方式继续用原 Codex；备份建议保留到测试正常结束。不需要更改应用文件。

## 曾替换原始快捷方式的情况

1. 查找 `ProjectRoot/backup/Codex.original.YYYYMMDD...lnk`。
2. 打开该 `.lnk` 属性确认仍指向原生 Codex，而不是动画启动器。
3. 在确认覆盖的目标 `.lnk` 路径无误后执行（示例路径需改）：

```powershell
powershell.exe -NoProfile -File '.\scripts\Restore-CodexShortcut.ps1' `
  -OriginalShortcutBackup 'D:\MyAnimeCodex\backup\Codex.original.20261023.lnk' `
  -DestinationShortcut 'C:\Users\YOU\Desktop\Codex.lnk' `
  -WhatIf
```

确认预演正确后移除 `-WhatIf` 执行。脚本使用 ShouldProcess，默认有覆盖前确认。恢复只复制 `.lnk`，不写注册表，不碰 Codex 账号数据。

任务栏若先前固定的是新快捷方式，需自行重固定原始 Codex。背景若使用过 Codex 原生设置，则在真实设置里改回，不要删除用户数据目录。
