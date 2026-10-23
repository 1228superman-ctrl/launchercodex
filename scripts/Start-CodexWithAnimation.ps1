#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OriginalShortcut,
    [Parameter(Mandatory = $true)][string]$VideoFile,
    [string]$PlayerPath = 'mpv.exe'
)

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This script supports Windows only.' }

$shortcut = [Environment]::ExpandEnvironmentVariables($OriginalShortcut)
$video = [Environment]::ExpandEnvironmentVariables($VideoFile)
$player = $null

if (-not (Test-Path -LiteralPath $shortcut -PathType Leaf)) {
    throw "Original Codex shortcut backup is missing: $shortcut. No program was launched."
}
if ([IO.Path]::GetExtension($shortcut).ToLowerInvariant() -ne '.lnk') {
    throw 'OriginalShortcut must be a backed-up .lnk file.'
}

# Playback is optional. Missing mpv or missing video never blocks a normal Codex launch.
if (Test-Path -LiteralPath $video -PathType Leaf) {
    if (Test-Path -LiteralPath $PlayerPath -PathType Leaf) {
        $player = (Resolve-Path -LiteralPath $PlayerPath).Path
    } else {
        $playerCommand = Get-Command $PlayerPath -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($playerCommand) { $player = $playerCommand.Source }
    }
} else {
    Write-Warning "Animation video not found; launching Codex normally: $video"
}

if ($player) {
    try {
        # mpv exits when the video completes; press q to skip playback.
        $playerArgs = @('--no-config', '--fullscreen', '--no-border', '--ontop', '--keep-open=no', '--no-osc', '--really-quiet', ('"' + $video + '"'))
        $process = Start-Process -FilePath $player -ArgumentList $playerArgs -Wait -PassThru -ErrorAction Stop
        if ($process.ExitCode -ne 0) { Write-Warning "mpv exited with code $($process.ExitCode)." }
    } catch {
        Write-Warning "Animation player failed: $($_.Exception.Message); launching Codex normally."
    }
} else {
    Write-Warning 'mpv is not available (or video is missing); launching Codex normally.'
}

# The backed-up shortcut retains any Store/MSIX AppUserModelID or original arguments.
Start-Process -FilePath $shortcut -ErrorAction Stop
