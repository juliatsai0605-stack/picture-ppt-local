# Windows v6 教學影片交接及錄製限制（2026-11-04）

> 本文件依 Claude 於對話提供的交接報告整理，**不是 Claude 原始檔案逐字副本**。**更新（2026-11-04）：** 已在可啟動 v6 的 Windows 11 筆電錄製真實操作，公開約72秒[繁體中文字幕 MP4](media/windows-v6-real-tutorial.mp4)。早期版本所述「尚無 MP4」為當時狀態；後續已完成並發布。

## 目前狀態

- **v6 正式發布**：已完成。公開 Release：https://github.com/juliatsai0605-stack/picture-ppt-local/releases/tag/v6.0.0
- **公開展示網站**：https://juliatsai0605-stack.github.io/picture-ppt-local/
- **ZIP 大小**：369,330,309 位元組。
- **SHA-256**：`f3278622a93e70ccdd91479550cd29d2afa0a525689d0550cec92986770bc873`
- **教學影片**：已以 Windows 11 真實 v6 介面完成三張圖片 OCR（21 段文字）及 PPTX 轉換錄影，發布約72秒字幕版；未使用舊版 Linux 模擬錄影。
- **正式字幕及腳本**：`docs/VIDEO_SCRIPT.md`、`docs/VIDEO_SUBTITLES_v6.srt` 為待錄製素材，並非影片。

## Windows 執行限制

1. 可遠端連線的家中 Windows 11 桌機，啟動未簽章的 v6 EXE 時遭 Code Integrity 政策阻擋（先前於事件 3033／3077 確認）；Claude 交接指出 Smart App Control 強制執行，登錄值 `VerifiedAndReputablePolicyState=1`，後者為 Claude 回報、ChatGPT 尚未於本文件更新時獨立重查。
2. **不得關閉或繞過防護**，也不得將此環境的啟動失敗視為 v6 功能缺陷或測試通過。
3. 曾能執行 v6 的 Windows 筆電目前沒有連線，未獲遠端操作能力。
4. 本版為**免安裝可攜版**：ZIP 解壓縮後執行 `slide2pptx/圖片簡報轉PPT.exe`；**不建立自動桌面捷徑**。

## 建議錄影方式

使用曾成功執行 v6 的 Windows 筆電，或另一部在合法安全政策下可執行原始 v6 的 Windows 測試電腦。優先使用 Windows 內建螢幕錄影工具，若無法捕捉完整流程再選 OBS；先進行 10 秒測錄，確認可捕捉檔案總管、瀏覽器及 PowerPoint，再正式拍攝。**不要假設 Xbox Game Bar 一定能錄製檔案總管**。

請使用 3 張自行製作、無機敏資料的公開測試圖片。Claude 先前回報的測試圖片尚未取得；**另由 ChatGPT 新製作的 3 張原創公開測試圖已上傳**至 [docs/test-assets/](test-assets/)，並提供 [ZIP](test-assets/%E5%85%AC%E9%96%8B%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87_3%E5%BC%B5.zip)，兩者不是同一份。

### 鏡頭順序

1. 公開 v6 Release 下載 ZIP、解壓縮。
2. 直接執行 EXE，不展示不存在的安裝精靈或桌面捷徑。
3. 本機瀏覽器頁面一次匯入 3 張 PNG／JPG。
4. 實際按鈕執行文字辨識、必要校正、產生 PPTX。
5. 用 PowerPoint 開啟輸出檔並修改一段重建的文字。
6. 結尾展示公開網站與 GitHub Release；提醒背景圖表通常仍是圖片。

### 交付與檢核

- 優先保留**未剪輯的真實螢幕錄影**；1920×1080、30fps 為目標，螢幕尺寸不足時以原始解析度錄製，不要為追求規格犧牲畫面真實性。
- 最終影片：16:9、H.264 MP4，約 60–90 秒，繁體中文字幕。
- 錄影時隱藏通知、帳號、個資、機關內容；不得使用受保護資料。
- 交接記錄：Windows 版本、v6 ZIP 雜湊、錄影檔名／位置、各步驟實際耗時、遇到的錯誤、PPTX 編輯驗收結果。
- 取得原始 MP4 後，由 ChatGPT 對照真實畫面調整旁白與 SRT、剪輯並嵌入既有網站；未取得 MP4 前，網站播放器應保持「影片準備中」，不得宣稱已發布。

## 簽章評估

程式碼簽章應另行評估身分驗證、發行成本與 Windows 信任政策。**簽章不保證所有 Smart App Control 或企業安全政策均會允許執行**；不將簽章列為本次影片製作的必要前提。

## 新增錄影操作指引

請參閱 [V6_RECORDING_GUIDE.md](V6_RECORDING_GUIDE.md)，包含筆電安全前提、錄影軟體選擇、測試圖連結及原始素材交付規格。

## 發布完成與驗收紀錄

- 版本：Windows v6.0.0，ZIP SHA-256 與正式 Release 一致。
- 實機：Windows 11 筆電；三張原創公開測試 PNG；OCR 21 段；產生 3 張 PPTX 約 64 秒。
- 文字可編輯驗證：Microsoft PowerPoint 實際開啟，3 張各有 7 個可編輯文字方塊，共 21 個；已修改文字並另存驗證檔。
- 公開影片：[`docs/media/windows-v6-real-tutorial.mp4`](media/windows-v6-real-tutorial.mp4)，約 72 秒，H.264，繁體中文字幕。等待片段已加速；最後 PowerPoint 圖像是軟體實際輸出成果，不是 PowerPoint 視窗操作影片。
- 隱私審查：影片僅包含獨立瀏覽器開啟的本機 v6 測試介面、自製公開測試圖片、PowerPoint 輸出圖像及公開展示網站；抽樣影格確認未見私人桌面或通知。
- 聲音：公開影片暫無旁白；內建 Windows TTS 有聲草稿僅保留於筆電，因公開散布授權尚未確認而未上傳。
