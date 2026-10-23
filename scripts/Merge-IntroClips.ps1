#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string[]]$Clips,
    [Parameter(Mandatory = $true)][string]$OutputFile,
    [ValidateRange(640,3840)][int]$Width = 1920,
    [ValidateRange(480,2160)][int]$Height = 1080,
    [ValidateRange(15,60)][int]$FPS = 30,
    [string]$AudioFile
)

$ErrorActionPreference = 'Stop'
if ($Clips.Count -lt 2) { throw 'Provide at least 2 clips in timeline order.' }
$ffmpeg = Get-Command 'ffmpeg.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $ffmpeg) { throw 'ffmpeg.exe not found in PATH. Install it from a trusted source first.' }
foreach ($clip in $Clips) {
    if (-not (Test-Path -LiteralPath $clip -PathType Leaf)) { throw "Missing input clip: $clip" }
}
if ($AudioFile -and -not (Test-Path -LiteralPath $AudioFile -PathType Leaf)) { throw "Missing audio file: $AudioFile" }

$output = [IO.Path]::GetFullPath($OutputFile)
if (Test-Path -LiteralPath $output) { throw "Output already exists, will not overwrite: $output" }
if ((@($Clips | ForEach-Object { [IO.Path]::GetFullPath($_) }) -contains $output)) { throw 'Output must not overwrite an input clip.' }
$parent = [IO.Path]::GetDirectoryName($output)
if (-not (Test-Path -LiteralPath $parent -PathType Container)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }

$temp = Join-Path ([IO.Path]::GetTempPath()) ('codex-intro-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    $videoPaths = @()
    for ($i = 0; $i -lt $Clips.Count; $i++) {
        $target = Join-Path $temp ('seg-{0:D3}.mp4' -f $i)
        $vf = 'scale={0}:{1}:force_original_aspect_ratio=decrease,pad={0}:{1}:(ow-iw)/2:(oh-ih)/2:color=black,fps={2},format=yuv420p' -f $Width,$Height,$FPS
        & $ffmpeg.Source -nostdin -hide_banner -loglevel error -y -i $Clips[$i] -vf $vf -an -c:v libx264 -preset medium -crf 19 -r $FPS -movflags +faststart $target
        if ($LASTEXITCODE -ne 0) { throw "FFmpeg failed to normalize: $($Clips[$i])" }
        $videoPaths += $target
    }

    $list = Join-Path $temp 'concat.txt'
    # Escape single quotes for FFmpeg concat demuxer. Forward slashes avoid Win32 backslash escapes.
    $rows = $videoPaths | ForEach-Object { "file '" + ($_.Replace('\', '/').Replace("'", "'\''")) + "'" }
    [IO.File]::WriteAllLines($list, [string[]]$rows, [Text.UTF8Encoding]::new($false))

    if ($AudioFile) {
        & $ffmpeg.Source -nostdin -hide_banner -loglevel error -y -f concat -safe 0 -i $list -i $AudioFile -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -af apad -shortest -movflags +faststart $output
    } else {
        & $ffmpeg.Source -nostdin -hide_banner -loglevel error -y -f concat -safe 0 -i $list -map 0:v:0 -c:v copy -an -movflags +faststart $output
    }
    if ($LASTEXITCODE -ne 0) { throw 'FFmpeg concat failed.' }
    Write-Output "Video created: $output"
} finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
