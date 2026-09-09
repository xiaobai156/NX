$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python -m PyInstaller --noconfirm --workpath ..\work\build-fixed --distpath dist BusinessOcrTrain_fixed.spec
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
$exe = Join-Path $PSScriptRoot 'dist\BusinessOcrTrain_0.1.3\BusinessOcrTrain_0.1.3.exe'
$report = Join-Path $PSScriptRoot 'verification'
$check = Start-Process -FilePath $exe -ArgumentList @('--self-check', ('"' + $report + '"')) -PassThru
if (-not $check.WaitForExit(30000)) { Stop-Process -Id $check.Id; throw 'UI check timed out' }
if ($check.ExitCode -ne 0) { throw 'UI check failed' }
Write-Host "EXE: $exe"
