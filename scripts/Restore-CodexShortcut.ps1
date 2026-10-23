#Requires -Version 5.1
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
param(
  [Parameter(Mandatory=$true)][string]$OriginalShortcutBackup,
  [Parameter(Mandatory=$true)][string]$DestinationShortcut
)
$ErrorActionPreference = 'Stop'
$backup = [IO.Path]::GetFullPath($OriginalShortcutBackup)
$destination = [IO.Path]::GetFullPath($DestinationShortcut)
if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { throw "Missing backup: $backup" }
if ([IO.Path]::GetExtension($backup) -ne '.lnk' -or [IO.Path]::GetExtension($destination) -ne '.lnk') {
    throw 'Both paths must be .lnk shortcuts.'
}
if ($backup -eq $destination) { throw 'Backup and destination must be different.' }
$wsh = New-Object -ComObject WScript.Shell
$lnk = $wsh.CreateShortcut($backup)
if ($lnk.Arguments -match 'Start-CodexWithAnimation\.ps1') {
    throw 'Selected backup itself points to the animation wrapper. Choose the real original backup.'
}
if (-not (Test-Path -LiteralPath (Split-Path -Parent $destination))) {
    throw 'Destination parent folder does not exist.'
}
if ($PSCmdlet.ShouldProcess($destination,'Restore original Codex shortcut')) {
    Copy-Item -LiteralPath $backup -Destination $destination -Force
    Write-Output "Restored shortcut only: $destination"
}
