param(
    [string]$AutoHotkey = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
)
$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'benchmark-switching.ahk'
$report = Join-Path ([IO.Path]::GetTempPath()) ("dofusahk-switching-{0}.csv" -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
if (-not (Test-Path -LiteralPath $AutoHotkey -PathType Leaf)) {
    throw "AutoHotkey v2 interpreter not found: $AutoHotkey"
}
$arguments = @('/ErrorStdOut', ('"{0}"' -f $script), ('"{0}"' -f $report))
Write-Host 'Testing focus on four temporary windows. No mouse clicks will be sent.'
$process = Start-Process -FilePath $AutoHotkey -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait
if ($process.ExitCode -ne 0) {
    if (Test-Path -LiteralPath $report) { Get-Content -LiteralPath $report | Select-Object -Last 3 | Write-Host }
    throw "Focus benchmark failed (exit $($process.ExitCode)). Report: $report"
}
$culture = [Globalization.CultureInfo]::InvariantCulture
Import-Csv -LiteralPath $report | Group-Object Mode | ForEach-Object {
    $requests = @($_.Group | ForEach-Object { [double]::Parse($_.RequestMs, $culture) })
    $focus = @($_.Group | ForEach-Object { [double]::Parse($_.FocusMs, $culture) })
    [pscustomobject]@{
        Mode = $_.Name
        Switches = $_.Count
        AverageRequestMs = [math]::Round(($requests | Measure-Object -Average).Average, 3)
        AverageFocusMs = [math]::Round(($focus | Measure-Object -Average).Average, 3)
        MaxFocusMs = [math]::Round(($focus | Measure-Object -Maximum).Maximum, 3)
    }
} | Format-Table -AutoSize
Write-Host "PASS: focus, disabled switching, missing/closed windows and restore. Report: $report"
Write-Host 'This tests synthetic windows; repeat the fast F1-click-F2-click sequence in game separately.'
