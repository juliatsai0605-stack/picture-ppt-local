# v6 驗證狀態與發布檢核（2026-11-04）

> 本文件為依現有交接紀錄整理的**驗收狀態表**，不是原始 `V6_VIDEO_HANDOFF.md`，也不是 Windows 實機驗收報告。

## 已完成及證據範圍

- Linux 環境使用與 v6 相同的程式、模型及套件，完成三張自行製作之測試圖匯入、OCR、產生 PPTX、下載；紀錄顯示共辨識 15 段文字。
- 產生之 PPTX 經程式讀取，計 3 頁，每頁包含一個名為「底圖」的圖片物件與 5 個可編輯文字方塊。**尚未用 Windows PowerPoint 實際開啟編輯。**
- Linux 辨識約 4–13 秒；產出 PPT 約 1–2 秒。**不得視為 Windows 效能數據。**
- OCR 已知異常：標題被分割為兩個文字方塊、`PowerPoint` 誤辨為 `PoWerPoint`、`PPT 並下載` 中空格消失；教學必須實際展示校對程序。
- 已在連線 Windows 桌機找到預定發行壓縮檔：`圖片簡報轉PPT_本機版_Windows_v6.zip`；檔案大小 **369,330,309 位元組**；2026-11-04 重新計算 SHA-256：
  `f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873`
- 發行版為可攜式設計；既有程式碼未提供桌面捷徑建立功能。**不要宣稱有安裝精靈或桌面捷徑。**

## 尚未驗證／發布

- [x] Windows 桌機成功解壓縮 ZIP；EXE 未具數位簽章，Microsoft Defender 即時防護啟用，已完成資料夾自訂掃描。
- [ ] **啟動阻擋待排除**：2026-11-04 使用 Windows PowerShell 啟動 EXE 時，Windows 回報檔案含病毒或潛在不需要的軟體，程式未啟動；同時段 Defender 事件中未查得與此檔案對應的新威脅偵測。進一步於 `Microsoft-Windows-CodeIntegrity/Operational` 查得事件 **3077、3033**，指出 EXE **未達 Enterprise signing level／違反 Code Integrity policy**（Policy ID：`{0283ac0f-fff1-49ae-ada1-8a933130cad6}`），故現階段較明確的阻擋原因為簽章／程式碼完整性政策。不得據此認定 EXE 為惡意程式，也不可停用防護或加入排除清單。應由負責的系統／資安管理者確認適用簽章及發行政策。
- [ ] 安全阻擋原因釐清後，再於 Windows 10/11 實際啟動 EXE，記錄等待時間、黑色視窗及 SmartScreen 提示（如有）。
- [ ] 在 Windows 介面的辨識校對表格中修改錯字，確認修改有保存並進入輸出結果。
- [ ] 使用 Microsoft PowerPoint 開啟 PPTX，確認文字實際可選取、可修改、底圖仍在。
- [ ] 網路封包監看：核對執行時有無對外連線，尚不能宣稱已實測「圖片絕不上傳」。
- [ ] 核對第三方套件與模型授權、壓縮檔掃描、ZIP 內容與預定 tag 對應性。
- [ ] 建立 GitHub Release（`v6.0.0`）並將此 SHA-256 對應 ZIP 上傳為附件；檢查公開下載可用。
- [ ] 取得原始 `V6_VIDEO_HANDOFF.md` 並原檔加入 `docs/`；目前交接文字僅見對話摘要，未取得原檔。
- [ ] 在 Windows 實機錄製教學 MP4，經內容及隱私檢查後以 Release 附件提供；網站再加入可播放的影片連結。
- [ ] 重新驗證網站下載按鈕、手機版介面、說明文字與正式 Release 一致。

## 發布管制

發布前，勿將 Linux 測試表述為 Windows EXE 實測；不得以 Linux 截圖當作 Windows 教學；不應宣稱 OCR 零錯誤、所有圖形皆可編輯、絕無網路傳輸或已完成 Windows 安全驗證。任何 SmartScreen 警示均應先檢查來源、雜湊及安全政策，不引導直接關閉防護。

影片及 ZIP 建議存於 GitHub Release 資產，避免將大型二進位檔加入 Git 歷史。
