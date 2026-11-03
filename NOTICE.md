# 第三方元件聲明

發行版壓縮檔內含下列元件，各依其原授權使用。授權種類為依各專案公開資訊所載，未逐一查核版本差異，使用或再散布前請自行確認。

| 元件 | 用途 | 授權（依專案公告） | 來源 |
|---|---|---|---|
| LaMa（ONNX 版 lama_fp32.onnx） | 影像修補擦字 | Apache-2.0 | https://github.com/advimman/lama ；https://huggingface.co/Carve/LaMa-ONNX |
| RapidOCR（rapidocr_onnxruntime） | 文字辨識 | Apache-2.0 | https://github.com/RapidAI/RapidOCR |
| PaddleOCR PP-OCR 模型（偵測、分類、PP-OCRv5 辨識） | 文字辨識模型 | Apache-2.0 | https://github.com/PaddlePaddle/PaddleOCR |
| ONNX Runtime | 模型推論 | MIT | https://github.com/microsoft/onnxruntime |
| Gradio | 操作介面 | Apache-2.0 | https://github.com/gradio-app/gradio |
| python-pptx | 產生 PPT | MIT | https://github.com/scanny/python-pptx |
| OpenCV、NumPy、Pillow、lxml 等 | 影像與資料處理 | 各自授權 | 見各套件 `dist-info` |
| Python 3.11 embeddable | 執行環境 | PSF License | https://www.python.org |
| Microsoft Visual C++ 執行階段 DLL | 執行環境 | Microsoft 授權 | 隨發行版附帶 |

各套件完整授權文字見發行版內 `_internal/runtime/Lib/site-packages/*.dist-info`。
