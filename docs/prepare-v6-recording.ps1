#requires -version 5.1
<#
Windows v6 真實操作錄影準備工具（不繞過任何安全防護）
1. 從原專案 Release 下載 ZIP，驗證 SHA-256
2. 準備三張公開測試圖、工作及錄影資料夾
3. 提示使用者開啟 Windows 錄影工具及真實的 v6 EXE
用途：使用先前已能合法啟動 v6 的個人 Windows 電腦；不在未經授權的公司／機關電腦執行。
#>
param(
    [switch]$SkipDownload,
    [switch]$OpenRecorder
)
$ErrorActionPreference='Stop'
$repo='https://github.com/juliatsai0605-stack/picture-ppt-local'
$zipUrl='https://github.com/juliatsai0605-stack/picture-ppt-local/releases/download/v6.0.0/picture-to-editable-ppt_Windows_v6.zip'
$sampleUrl='https://raw.githubusercontent.com/juliatsai0605-stack/picture-ppt-local/main/docs/test-assets/%E5%85%AC%E9%96%8B%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87_3%E5%BC%B5.zip'
$expected='f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873'
$base=Join-Path $env:USERPROFILE 'Videos\PPT_v6_教學錄影'
$setup=Join-Path $base 'v6_正式版'
$samples=Join-Path $base '公開測試圖片'
$zip=Join-Path $base 'picture-to-editable-ppt_Windows_v6.zip'
$sampleZip=Join-Path $base '公開測試圖片_3張.zip'
foreach($dir in @($base,$setup,$samples)){New-Item -ItemType Directory -Force -Path $dir | Out-Null}
Write-Host 'Windows v6 操作錄影準備' -ForegroundColor Cyan
Write-Host "錄影目錄：$base"
if(!(Test-Path $zip)){
    if($SkipDownload){throw "找不到 ZIP，且已指定 SkipDownload：$zip"}
    Write-Host '正在下載公開 v6.0.0 Release ZIP（約 352 MiB）...'
    Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing
}
$actual=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if($actual -ne $expected){
    throw "ZIP SHA-256 不符，已停止；請檢查來源與檔案：$actual"
}
Write-Host 'v6 ZIP SHA-256 相符。' -ForegroundColor Green
if(!(Test-Path (Join-Path $setup 'slide2pptx'))){
    Write-Host '解壓縮 v6 ...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zip,$setup)
}
if(!(Test-Path $sampleZip)){
    Invoke-WebRequest -Uri $sampleUrl -OutFile $sampleZip -UseBasicParsing
}
if(!(Get-ChildItem -LiteralPath $samples -Filter '*.png' -File -ErrorAction SilentlyContinue)){
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($sampleZip,$samples)
}
$exe=Get-ChildItem (Join-Path $setup 'slide2pptx') -Filter '*.exe' -File|Select-Object -First 1
if(!$exe){throw '解壓縮後找不到 Windows v6 啟動 EXE，請停止並核對。'}
$instructions=@'
真實操作錄影：
1. 開啟剪取工具，進入錄影功能（Windows+Shift+R 通常可直接啟動錄影）。
2. 先測錄 10 秒，確認有錄到檔案總管／本機瀏覽器／PowerPoint。
3. 在符合設備安全政策的電腦，執行 v6 EXE，匯入三張「公開測試圖片」，辨識文字、校正、匯出 PPTX。
4. 真正用 PowerPoint 開啟並修改文字，完成後停止錄影，將原始影片存入本資料夾。
5. 正式發布前檢查每一段：私人帳號、通知、路徑、文件內容；優先裁掉或用完全不透明遮罩覆蓋。
若 Windows Smart App Control 或 Code Integrity 封鎖 EXE，請停止並記錄；不要停用或繞過安全防護。
本工具不會自動錄製螢幕、不會修改安全設定，也不會上傳錄影。
'@
$guide=Join-Path $base '錄影步驟及安全提醒.txt'
[System.IO.File]::WriteAllText($guide,$instructions,[System.Text.Encoding]::UTF8)
Start-Process explorer.exe -ArgumentList ('"'+$samples+'"')
Start-Process explorer.exe -ArgumentList ('"'+$exe.DirectoryName+'"')
if($OpenRecorder){
    try{Start-Process 'ms-screenclip:'}catch{Write-Host '請手動開啟 Windows 剪取工具錄影功能。'}
}
Write-Host "已準備好：$exe" -ForegroundColor Green
Write-Host "錄影指引：$guide"
Write-Host '請先確認此電腦的安全政策允許執行；遇到封鎖不可繞過。'
$answer=Read-Host '是否現在嘗試執行已核對的 v6 EXE？（輸入 YES 才執行）'
if($answer -ceq 'YES'){
    try{Start-Process -FilePath $exe.FullName -WorkingDirectory $exe.DirectoryName -ErrorAction Stop}
    catch{Write-Warning ("Windows 已拒絕啟動程式，請保留安全政策並停止測試：" + $_.Exception.Message)}
} else {Write-Host '已略過 EXE 啟動，可先測錄公開畫面。'}
