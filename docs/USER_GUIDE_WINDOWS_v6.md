# Windows v6 完整使用教學｜零付費、免安裝可攜版

> 適用版本：`v6.0.0`。本文件為可直接閱讀／錄製旁白的操作說明。Windows 執行畫面尚未取得，故非實測影片。首次使用請在允許執行此程式的個人電腦操作；不要要求 AI Agent 關閉系統安全防護。

## 第一步｜下載正式 ZIP

1. 開啟 [Windows v6 官方發布頁](https://github.com/juliatsai0605-stack/picture-ppt-local/releases/tag/v6.0.0)。
2. 在 **Assets** 區下載 `picture-to-editable-ppt_Windows_v6.zip`，約 352 MiB。
3. **不要選 GitHub 自動產生的 `Source code (zip)`**，它是程式原始碼，不是已封裝的 Windows 應用程式。
4. 如希望核對檔案完整性，可在 Windows PowerShell 執行：
   ```powershell
   Get-FileHash -LiteralPath "C:\\實際下載資料夾\\picture-to-editable-ppt_Windows_v6.zip" -Algorithm SHA256
   ```
   預期值：`f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873`。**檔名、檔案大小、雜湊值相符不等於保證無惡意程式**，仍須核對來源、授權及終端安全規範。

## 第二步｜解壓縮與啟動

1. 在 Windows 檔案總管找到 ZIP，選 **「解壓縮全部」**，將整個資料夾放在自己有讀寫權限的位置（例如「文件」中的專用資料夾）。
2. 開啟解壓縮後的 `slide2pptx` 資料夾。
3. 執行 **「圖片簡報轉PPT.exe」**。此為**免安裝可攜版**，不需要另裝 Python，**不會自動建立桌面捷徑**。
4. 程式正常啟動時，會在瀏覽器開啟本機操作介面（例如 `http://127.0.0.1:7860`）。`127.0.0.1` 是你自己電腦，不是提供他人從網路連入的公開網站。

### 遇到 Windows 安全警告怎麼辦？

**先確認自己下載的檔案確實來自上述 GitHub Release**，並經核對檔案完整性。

- **Microsoft Defender SmartScreen 的「Windows 已保護您的電腦」提醒**：在個人電腦上，先核對來源、雜湊與風險，再遵循系統顯示的選項及自身安全政策決定是否執行；不能因為「免費工具」就無條件略過警告。
- **Smart App Control（智慧應用程式控制）顯示封鎖**：這是另一種執行控制。Microsoft 說明**無法針對單一應用程式設定例外**。不要為了本工具停用 Smart App Control；改用允許執行的設備，或請發行者評估適當簽章。
- **Code Integrity／WDAC／公司、機關管理政策封鎖**：停止執行，請設備管理者依規範評估；**不得更改登錄、關閉政策、停用防毒或藉由 Agent 繞過**。

簽章憑證可能涉及費用，但**EXE 打包本身不必購買憑證**。簽章也不是保證所有電腦都一定放行。

官方說明：[Smart App Control FAQ](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions)、[Smart App Control 概述](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/overview)。

## 第三步｜圖片轉 PPT

1. 準備 1 張或多張 PNG/JPG；可先下載專案內的 [3 張公開測試圖片](test-assets/%E5%85%AC%E9%96%8B%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87_3%E5%BC%B5.zip)。
2. 透過本機網頁的圖片匯入區加入圖片。
3. 依畫面選擇 **「① 辨識文字」**（按鈕名稱以 v6 真正介面為準）。
4. 檢視 OCR 文字結果，必要時校正中文錯字與數字。
5. 按 **「② 產生 PPT」**，取得 PowerPoint 檔案。
6. 在 PowerPoint 開啟，點選並修改重建後的文字方塊；逐頁核對順序、字型、文字位置、版面和背景圖片。

**可編輯的是重建後的文字；底圖、插畫、線條與圖表不保證都轉成 PowerPoint 原生物件。** OCR 和影像修補可能產生誤差，不能省略人工驗收。

## 第四步｜直接交給 AI Agent 協助（可選）

如果你使用已取得你授權、能操作本機檔案／終端機的 Claude Code、Codex 等 Agent，可將下列文字連同專案網址直接交給它：

> 請協助部署 GitHub 專案 https://github.com/juliatsai0605-stack/picture-ppt-local 的 Windows v6 正式版。先閱讀 README、LICENSE、NOTICE 及 docs/USER_GUIDE_WINDOWS_v6.md；從 v6.0.0 Release 下載 `picture-to-editable-ppt_Windows_v6.zip`，不要下載 Source code ZIP。核對 SHA-256 `f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873`，確認設備安全政策允許後，完整解壓縮並執行 `slide2pptx/圖片簡報轉PPT.exe`。使用公開測試圖驗證匯入、辨識、校正、產生 PPTX 與 PowerPoint 文字編輯。若遇 SmartScreen、Smart App Control 或組織管理政策封鎖，請辨別原因並回報；**不得停用、繞過或修改安全防護以強制執行**。不要上傳使用者圖片、個人資料或機關資訊。

Agent **不是只貼連結就能取得電腦操作權限**；沒有可用本機執行環境時，它只能提供操作步驟。

## 教學影片文字版（可直接當旁白）

「這是一套免費的 Windows 本機圖片轉 PowerPoint 工具。從 GitHub 正式發布頁下載 Windows v6 ZIP，記得選發行附件，不是原始碼 ZIP。下載後完整解壓縮，再進入資料夾執行圖片簡報轉 PPT。這是可攜版，不用另裝 Python，也不會自動建立桌面捷徑。啟動後在本機網頁加入一張或多張圖片，按下文字辨識，檢查並修正需要校對的內容。接著產生 PPTX，在 PowerPoint 中就能修改重建的文字方塊。圖片中的圖表與其他視覺元素通常仍是底圖，請記得逐頁核對成果。如果 Windows 安全機制封鎖程式，請先確認來源及設備安全規範；Smart App Control 或企業政策封鎖時，不要強制繞過。也可以把 GitHub 專案網址交給已獲授權的 AI Agent 協助操作。」

## 發布與測試現況

- **已完成**：v6.0.0 公開 GitHub Release、Windows ZIP、展示網站下載連結、本篇文字教學與測試圖片。
- **尚未完成**：Windows v6 在可執行設備上的完整功能實測及真實操作錄影 MP4；網站影片區仍是「準備中」。
- **已知限制**：先前家中 Windows 桌機因 Code Integrity／Smart App Control 阻擋未簽署 EXE，未為了測試停用安全防護。
