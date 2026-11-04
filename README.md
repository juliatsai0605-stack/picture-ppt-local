# 圖片簡報轉可編輯 PPT（Windows 本機版）

> **產品展示網站（已公開）**：https://juliatsai0605-stack.github.io/picture-ppt-local/  
> **完整操作教學**：網站內「使用教學」；[影片錄製腳本](docs/VIDEO_SCRIPT.md)（真實操作影片尚待錄製）  
> **未來專案發布範本**：[GitHub 展示網站與影片發布流程](docs/PROJECT_LAUNCH_TEMPLATE.md)  


把 AI 產生的簡報圖片（PNG／JPG）轉成可以修改文字的 PowerPoint。
**設計上採本機處理**，介面預設於 `127.0.0.1` 運作；尚未完成 Windows 發行版的網路封包驗證，因此暫不保證絕無對外連線。請勿在完成資安驗證前處理機敏圖片。

## 下載

**Windows v6.0.0 已正式發布：** [下載 Windows v6 ZIP（約 352 MiB）](https://github.com/juliatsai0605-stack/picture-ppt-local/releases/download/v6.0.0/picture-to-editable-ppt_Windows_v6.zip)。另可查看 [GitHub Release 發布說明](https://github.com/juliatsai0605-stack/picture-ppt-local/releases/tag/v6.0.0)。請勿將 GitHub 自動產生的 Source code ZIP 誤當成 Windows 執行版本。

## 使用方式（Windows 發行版）

1. 在壓縮檔上按右鍵 →「解壓縮全部」（請勿在壓縮檔內直接執行）。
2. 進入 `slide2pptx` 資料夾，點兩下「圖片簡報轉PPT.exe」。
3. 此版為免安裝可攜版，**不會自動建立桌面捷徑**。Windows 若顯示安全警告，請先核對來源並遵循電腦的資訊安全政策；企業簽章政策可能阻止未簽署程式執行。
4. 瀏覽器會自動開啟操作畫面（網址 `http://127.0.0.1:7860`，僅本機可連）。
5. 上傳圖片 →「① 辨識文字」→ 在表格校對錯字 →「② 產生 PPT」→ 下載。

## 功能

- 辨識圖上文字（中文、英文、數字），可在表格逐段修改。
- 以修補模型擦除原文字，原圖作為最底層圖片，文字改為可編輯文字方塊（微軟正黑體）。
- 底圖為投影片內的圖片物件，複製到其他簡報時背景可一併帶走。
- 支援中文檔名；輸出圖片維持原解析度。可一次處理多張，依檔名排序。

## 系統需求

Windows 10／11 64 位元；建議記憶體 8 GB 以上；無須另行安裝 Python。v6 為免安裝可攜版，並不自動建立桌面捷徑。

## 常見問題

- **Windows 擋下執行檔？** 發行版如未具有效程式碼簽章，可能觸發 SmartScreen。請先確認來源、ZIP 的 SHA-256 及安全掃描結果；若仍有警告，依個人電腦或所屬單位資訊安全政策處理，不應逕行略過防護或以移動檔案方式規避防毒偵測。
- **圖示緊貼文字被一起擦掉？** 在表格取消該列「轉成文字」的打勾，或到 PowerPoint 補回。
- **辨識有錯字？** 以表格校對為準，OCR 無法保證完全正確。
- **會連網嗎？** 程式設計使用 `127.0.0.1` 提供本機介面，並設定關閉模型下載與使用統計；但尚未以 Windows 網路封包監看確認所有執行路徑，故不能把「未對外傳輸」視為已實測的安全保證。

## 運作原理

文字辨識：RapidOCR（ONNX Runtime，PP-OCR 偵測／分類模型、PP-OCRv5 辨識模型）。
擦字：LaMa 影像修補模型（ONNX 版）。介面：Gradio。輸出：python-pptx。

## 原始碼與自行打包

`src/` 為應用程式原始碼，`launcher/` 為 Windows 啟動器（C 語言）。發行版將程式編譯後與
Python 3.11 embeddable、Windows 版套件及模型一併封裝；模型檔不在本倉庫內，來源見 `NOTICE.md`。

## 授權與致謝

本倉庫自行撰寫之程式以 MIT 授權（見 `LICENSE`）。發行版內含第三方元件與模型，各依其授權，
詳見 `NOTICE.md`。

## 免責聲明

本工具僅供轉換簡報圖片之輔助，輸出內容請自行逐頁核對。處理機敏資料時，請遵守所屬單位之資訊安全及保密規定。
