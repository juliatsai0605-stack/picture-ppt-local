#requires -version 5.1
# Prepare verified v6 video recording on an authorized Windows PC.
# This script does NOT disable, bypass or alter security controls.
param([switch]$SkipDownload,[switch]$OpenRecorder)
$ErrorActionPreference = 'Stop'
$zipUrl = 'https://github.com/juliatsai0605-stack/picture-ppt-local/releases/download/v6.0.0/picture-to-editable-ppt_Windows_v6.zip'
$sampleUrl = 'https://raw.githubusercontent.com/juliatsai0605-stack/picture-ppt-local/main/docs/test-assets/%E5%85%AC%E9%96%8B%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87_3%E5%BC%B5.zip'
$expectedHash = 'f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873'
$base = Join-Path $env:USERPROFILE 'Videos\PPT_v6_Recordings'
$appDir = Join-Path $base 'v6_portable'
$sampleDir = Join-Path $base 'public_test_images'
$zip = Join-Path $base 'picture-to-editable-ppt_Windows_v6.zip'
$sampleZip = Join-Path $base 'public_test_images.zip'
foreach ($dir in @($base,$appDir,$sampleDir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
Write-Host "Recording folder: $base" -ForegroundColor Cyan
if (!(Test-Path -LiteralPath $zip)) {
    if ($SkipDownload) { throw "Missing local ZIP: $zip" }
    Write-Host 'Downloading official v6 ZIP (~352 MiB)...'
    Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing
}
$actualHash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) { throw "SHA-256 mismatch: $actualHash" }
Write-Host 'ZIP SHA-256 verified.' -ForegroundColor Green
$appExeDir = Join-Path $appDir 'slide2pptx'
if (!(Test-Path -LiteralPath $appExeDir)) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zip,$appDir)
}
if (!(Test-Path -LiteralPath $sampleZip)) {
    Invoke-WebRequest -Uri $sampleUrl -OutFile $sampleZip -UseBasicParsing
}
if (@(Get-ChildItem -LiteralPath $sampleDir -Filter '*.png' -File -ErrorAction SilentlyContinue).Count -eq 0) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($sampleZip,$sampleDir)
}
$exe = Get-ChildItem -LiteralPath $appExeDir -Filter '*.exe' -File | Select-Object -First 1
if (!$exe) { throw 'No Windows EXE found in v6 package.' }
$notes = @'
Record only on a Windows PC where the existing security policy permits the app.
1. Use Windows Snipping Tool record mode (Win+Shift+R, if available).
2. Record a 10-second test and confirm Explorer, browser and PowerPoint are captured.
3. Start v6 EXE (portable app; no installer and no automatic desktop shortcut).
4. Import the 3 public PNG samples, OCR, correct, export PPTX, edit text in PowerPoint.
5. Save original recording in the same Videos/PPT_v6_Recordings folder.
6. Before publishing, remove private scenes or cover them with fully opaque masks.
Do NOT disable or bypass Smart App Control, Code Integrity or other security controls.
This helper does not record the screen, alter security policy or upload files.
'@
$notesPath = Join-Path $base 'RECORDING_README.txt'
[System.IO.File]::WriteAllText($notesPath,$notes,[System.Text.Encoding]::UTF8)
Start-Process explorer.exe -ArgumentList ('"'+$sampleDir+'"')
Start-Process explorer.exe -ArgumentList ('"'+$appExeDir+'"')
Write-Host "Verified EXE: $($exe.FullName)"
Write-Host "Instructions: $notesPath"
if ($OpenRecorder) {
    Write-Host 'Open Snipping Tool recording with Win+Shift+R; do not record private windows.'
}
$answer = Read-Host 'Launch verified v6 EXE now? Type YES to proceed'
if ($answer -ceq 'YES') {
    try {
        Start-Process -FilePath $exe.FullName -WorkingDirectory $exe.DirectoryName -ErrorAction Stop
    } catch {
        Write-Warning ('Windows denied EXE launch. Stop and keep security settings intact: ' + $_.Exception.Message)
    }
} else {
    Write-Host 'Launch skipped; folders and samples are ready.'
}
