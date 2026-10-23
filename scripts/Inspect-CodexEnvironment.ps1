#Requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This script supports Windows only.' }

$roots = @(
    [Environment]::GetFolderPath('Desktop'),
    [Environment]::GetFolderPath('CommonDesktopDirectory'),
    [Environment]::GetFolderPath('StartMenu'),
    [Environment]::GetFolderPath('CommonStartMenu')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) } | Select-Object -Unique

$wsh = New-Object -ComObject WScript.Shell
$found = @()
foreach ($root in $roots) {
    Get-ChildItem -LiteralPath $root -Filter '*.lnk' -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '(?i)codex' } |
        ForEach-Object {
            try {
                $lnk = $wsh.CreateShortcut($_.FullName)
                $found += [pscustomobject]@{
                    Path = $_.FullName
                    TargetPath = $lnk.TargetPath
                    Arguments = $lnk.Arguments
                    IconLocation = $lnk.IconLocation
                }
            } catch { Write-Warning "Cannot inspect $($_.FullName): $($_.Exception.Message)" }
        }
}

$commands = [ordered]@{}
foreach ($name in @('mpv.exe', 'ffmpeg.exe', 'ffprobe.exe', 'codex.exe', 'codex')) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
    $commands[$name] = if ($cmd) { $cmd.Source } else { $null }
}

[pscustomobject]@{
    Timestamp = (Get-Date).ToString('o')
    OperatingSystem = [Environment]::OSVersion.VersionString
    WindowsPowerShell = $PSVersionTable.PSVersion.ToString()
    Commands = $commands
    CodexShortcuts = $found
    Note = 'Read-only inspection. Shortcuts not containing Codex in their filenames may not be listed.'
} | ConvertTo-Json -Depth 6
