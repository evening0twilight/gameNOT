# Windows PowerShell 5.1, UTF-8 ASCII subset. Keep beside the exported game.
param([switch]$Automated)
$ErrorActionPreference = 'Stop'
$game = Join-Path $PSScriptRoot 'night-tide.exe'
$pack = Join-Path $PSScriptRoot 'night-tide.pck'
$receiptFile = Join-Path $PSScriptRoot 'build-receipt.json'
foreach ($path in @($game, $pack, $receiptFile)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Extract the full ZIP before starting. Missing: $path" }
}
$receipt = Get-Content -LiteralPath $receiptFile -Raw -Encoding UTF8 | ConvertFrom-Json
$sessionId = (Get-Date -Format yyyyMMdd-HHmmss) + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$folder = Join-Path ([Environment]::GetFolderPath('MyDocuments')) ('NightTide-Review-' + $sessionId)
$null = New-Item -Path $folder -ItemType Directory
$deviceFile = Join-Path $folder 'device.json'
$memoryFile = Join-Path $folder 'process-memory.csv'
$marker = Join-Path $folder 'title-presented.txt'
$record = [ordered]@{
    session_id = $sessionId
    candidate = $receipt.candidate
    mode = if ($Automated) { 'isolated_automatic_checks' } else { 'normal_reference_play' }
    started_utc = [DateTime]::UtcNow.ToString('o')
    completed = $false
    launch_to_title_signal_upper_ms = $null
    launch_poll_interval_ms = 25
    first_launch_since_reboot = 'observer must confirm'
    two_hour_private_memory_trend = 'review raw samples with gameplay notes'
}
$record | ConvertTo-Json | Set-Content -LiteralPath $deviceFile -Encoding UTF8
Write-Host "Recording this game session in $folder"
if ($Automated) {
    $env:NIGHT_TIDE_NATIVE_DIR = $folder
    $gameArgs = @('--log-file', ('"{0}"' -f (Join-Path $folder 'engine.log')), '--', '--acceptance-test')
} else {
    $env:NIGHT_TIDE_REVIEW_DIR = $folder
    $gameArgs = @('--fullscreen', '--', '--reference-session')
}
$watch = [Diagnostics.Stopwatch]::StartNew()
$process = Start-Process -FilePath $game -WorkingDirectory $PSScriptRoot -ArgumentList $gameArgs -PassThru
$null = $process.Handle
$processStart = $process.StartTime
while (-not $Automated -and -not $process.HasExited -and $watch.Elapsed.TotalSeconds -lt 60) {
    if (Test-Path -LiteralPath $marker) {
        $record.launch_to_title_signal_upper_ms = [math]::Round($watch.Elapsed.TotalMilliseconds, 2)
        break
    }
    Start-Sleep -Milliseconds 25
}
$samples = 0
$firstSample = $null
$lastSample = $null
$largestGap = 0
while (-not $process.HasExited) {
    try {
        $process.Refresh()
        $privateBytes = $process.PrivateMemorySize64
        $workingBytes = $process.WorkingSet64
    } catch {
        if ($process.HasExited) { break }
        throw
    }
    $seconds = [math]::Round($watch.Elapsed.TotalSeconds, 3)
    if ($null -eq $firstSample) { $firstSample = $seconds }
    if ($null -ne $lastSample) { $largestGap = [math]::Max($largestGap, $seconds - $lastSample) }
    $lastSample = $seconds
    $samples++
    [pscustomobject]@{seconds=$seconds; private_bytes=$privateBytes; working_set_bytes=$workingBytes} |
        Export-Csv -LiteralPath $memoryFile -Append -NoTypeInformation
    $null = $process.WaitForExit(60000)
}
$process.WaitForExit()
$watch.Stop()
# Hash AFTER exit. The recorder must not warm the EXE/PCK before timing startup.
$record.exe_sha256 = (Get-FileHash -LiteralPath $game -Algorithm SHA256).Hash.ToLowerInvariant()
$record.pck_sha256 = (Get-FileHash -LiteralPath $pack -Algorithm SHA256).Hash.ToLowerInvariant()
$record.matches_build_receipt = ($record.exe_sha256 -eq $receipt.sha256.'night-tide.exe' -and
                                $record.pck_sha256 -eq $receipt.sha256.'night-tide.pck')
$record.process_seconds = [math]::Round(($process.ExitTime - $processStart).TotalSeconds, 2)
$record.exit_code = $process.ExitCode
$record.memory_samples = $samples
$record.first_sample_seconds = $firstSample
$record.last_sample_seconds = $lastSample
$record.memory_sample_span_seconds = if ($samples -gt 1) { [math]::Round($lastSample - $firstSample, 2) } else { 0 }
$record.longest_memory_sample_gap_seconds = [math]::Round($largestGap, 2)
$record.game_metrics_present = Test-Path -LiteralPath (Join-Path $folder 'game-metrics.json') -PathType Leaf
try {
    $os = Get-CimInstance Win32_OperatingSystem
    $system = Get-CimInstance Win32_ComputerSystem
    $record.windows = $os.Caption
    $record.build = $os.BuildNumber
    $record.os_architecture = $os.OSArchitecture
    $record.last_boot_utc = $os.LastBootUpTime.ToUniversalTime().ToString('o')
    $record.cpu = @(Get-CimInstance Win32_Processor | Select-Object Name,Architecture)
    $record.gpu = @(Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,CurrentHorizontalResolution,CurrentVerticalResolution)
    $record.ram_bytes = $system.TotalPhysicalMemory
    $record.hardware_recorded = $true
} catch {
    $record.hardware_recorded = $false
    Write-Warning "Device inventory unavailable. Record CPU, GPU, Windows version and installed RAM manually."
}
if ($Automated) {
    $reportPath = Join-Path $folder 'report.json'
    $record.native_automatic_checks_passed = $false
    if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
        $native = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $record.native_automatic_checks_passed = ($native.passed -eq $true -and $native.native_windows -eq $true)
    }
    $record.run_output_present = $record.native_automatic_checks_passed
} else {
    $record.run_output_present = ($record.game_metrics_present -and $null -ne $record.launch_to_title_signal_upper_ms)
}
$record.completed = $true
$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $deviceFile -Encoding UTF8
Write-Host "Finished. Results in $folder"
if (-not $record.matches_build_receipt -or -not $record.run_output_present -or $record.exit_code -ne 0) {
    throw "Recording incomplete. Check device.json, exit code, title signal, EXE/PCK hashes and game metrics."
}
