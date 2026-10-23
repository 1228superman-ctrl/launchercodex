#Requires -Version 5.1
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory = $true)][string]$CodexShortcut,
    [Parameter(Mandatory = $true)][string]$VideoFile,
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [string]$IconPath,
    [string]$PlayerPath = 'mpv.exe',
    [switch]$ReplaceOriginal
)

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This script supports Windows only.' }

function Quote-PSArgument([string]$s) {
    if ($s.Contains('"')) { throw 'Double quotes in a path or player name are not supported.' }
    return '"' + $s + '"'
}

$original = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($CodexShortcut))
$project = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($ProjectRoot))
$video = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($VideoFile))

if (-not (Test-Path -LiteralPath $original -PathType Leaf)) { throw "Codex shortcut does not exist: $original" }
if ([IO.Path]::GetExtension($original).ToLowerInvariant() -ne '.lnk') { throw 'CodexShortcut must refer to a .lnk file.' }
if (-not (Test-Path -LiteralPath $video -PathType Leaf)) { throw "Video does not exist: $video" }
if ($IconPath) {
    $IconPath = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($IconPath))
    if (-not (Test-Path -LiteralPath $IconPath -PathType Leaf)) { throw "Icon file does not exist: $IconPath" }
    if ([IO.Path]::GetExtension($IconPath).ToLowerInvariant() -ne '.ico') { throw 'IconPath must be an .ico file.' }
}

$sourceLauncher = Join-Path $PSScriptRoot 'Start-CodexWithAnimation.ps1'
if (-not (Test-Path -LiteralPath $sourceLauncher -PathType Leaf)) { throw 'Launcher helper is missing from the skill package.' }

# Avoid using the original shortcut from inside the same project folder as the target shortcut.
$backupFolder = Join-Path $project 'backup'
$launcherFolder = Join-Path $project 'launcher'
$shortcutFolder = Join-Path $project 'shortcuts'
$destination = if ($ReplaceOriginal) { $original } else { Join-Path $shortcutFolder 'Codex-Anime-Launcher.lnk' }
if (-not $ReplaceOriginal -and [string]::Equals($original, $destination, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Original and output shortcut paths must not be equal.'
}
if (-not $ReplaceOriginal -and (Test-Path -LiteralPath $destination)) {
    throw "Output shortcut already exists: $destination"
}

# Never allow callers to accidentally use an already-installed launcher as the source.
$wsh = New-Object -ComObject WScript.Shell
$existing = $wsh.CreateShortcut($original)
if ($existing.Arguments -match 'Start-CodexWithAnimation\.ps1') {
    throw 'The selected shortcut already points to an anime launcher. Choose the original Codex shortcut instead.'
}

if (-not $PSCmdlet.ShouldProcess($destination, 'Create a recoverable Codex animation shortcut')) { return }
New-Item -ItemType Directory -Force -Path $backupFolder, $launcherFolder, $shortcutFolder | Out-Null

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$backupShortcut = Join-Path $backupFolder ("Codex.original.$stamp.lnk")
Copy-Item -LiteralPath $original -Destination $backupShortcut -ErrorAction Stop
$launcherCopy = Join-Path $launcherFolder 'Start-CodexWithAnimation.ps1'
Copy-Item -LiteralPath $sourceLauncher -Destination $launcherCopy -Force

$psExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $psExe -PathType Leaf)) { throw "Windows PowerShell not found: $psExe" }

$args = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ' + (Quote-PSArgument $launcherCopy) +
    ' -OriginalShortcut ' + (Quote-PSArgument $backupShortcut) +
    ' -VideoFile ' + (Quote-PSArgument $video) +
    ' -PlayerPath ' + (Quote-PSArgument $PlayerPath)

# To avoid losing the original before creating the new link, write to a staging path first.
$stagingShortcut = Join-Path $shortcutFolder ("Codex-staging-$stamp.lnk")
try {
    $link = $wsh.CreateShortcut($stagingShortcut)
    $link.TargetPath = $psExe
    $link.Arguments = $args
    $link.WorkingDirectory = $project
    $link.Description = 'Play custom intro, then open the original Codex desktop app'
    if ($IconPath) { $link.IconLocation = $IconPath }
    elseif ($existing.IconLocation) { $link.IconLocation = $existing.IconLocation }
    $link.Save()

    # With -ReplaceOriginal, stage the new link then replace only the specified source .lnk.
    if ($ReplaceOriginal) {
        Copy-Item -LiteralPath $stagingShortcut -Destination $original -Force -ErrorAction Stop
        Remove-Item -LiteralPath $stagingShortcut -Force
    } else {
        if (Test-Path -LiteralPath $destination) { throw "Output shortcut already exists: $destination" }
        Move-Item -LiteralPath $stagingShortcut -Destination $destination -ErrorAction Stop
    }
} catch {
    if (Test-Path -LiteralPath $stagingShortcut) { Remove-Item -LiteralPath $stagingShortcut -Force }
    throw
}

Write-Output ([pscustomobject]@{
    OutputShortcut = $destination
    OriginalBackup = $backupShortcut
    LauncherScript = $launcherCopy
    VideoFile = $video
    IconFile = if ($IconPath) { $IconPath } else { '(original shortcut icon)' }
    ReplacedOriginal = [bool]$ReplaceOriginal
    Note = 'Only a shortcut was created/replaced. Codex files were not modified; playback needs mpv.'
} | Format-List | Out-String)
