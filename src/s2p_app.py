"""圖片簡報轉可編輯 PPT — 本機版（只在本機執行，不上傳任何檔案）。"""
print()
print("  圖片簡報轉可編輯PPT（本機版）")
print("  啟動中，約需 20 到 60 秒，完成後會自動開啟瀏覽器。")
print("  使用期間請勿關閉這個黑色視窗；用完直接關掉即可。")
print(flush=True)
import os
import shutil
import tempfile
import time

import gradio as gr
import pandas as pd

import slide2pptx as s2p

COLS = ["張", "編號", "文字（可修改）", "轉成文字"]

GUIDE = """
### 使用方式
1. **上傳圖片**：可一次選多張，依檔名排序成投影片順序。
2. 按 **「① 辨識文字」**，右邊會顯示每張圖的文字編號，下方表格列出辨識結果。
3. **在表格校對**：
   - 錯字直接點格子修改。
   - 不想改成文字方塊、要保留在圖上的，取消「轉成文字」打勾。
   - 想把文字從圖上整個拿掉，把文字格清空即可。
4. 按 **「② 產生 PPT」**，完成後點下方檔案下載，用 PowerPoint 開啟修改。
"""


def _sorted_paths(files):
    paths = [f if isinstance(f, str) else f.name for f in (files or [])]
    return sorted(paths, key=lambda p: os.path.basename(p))


def recognise(files, progress=gr.Progress()):
    paths = _sorted_paths(files)
    if not paths:
        raise gr.Error("請先上傳圖片。")
    work = tempfile.mkdtemp(prefix="s2p_")
    store, rows, previews = [], [], []
    for i, src in enumerate(paths, 1):
        progress((i - 1) / len(paths), desc=f"辨識第 {i}/{len(paths)} 張")
        # 複製成英數檔名，避免中文檔名在 Windows 讀取失敗；原圖不壓縮、不縮小
        path = os.path.join(work, f"slide_{i:03d}{os.path.splitext(src)[1].lower() or '.png'}")
        shutil.copyfile(src, path)
        items = s2p.detect_text(path)
        store.append({"image": path, "items": items})
        prev = s2p.draw_numbers(path, items, os.path.join(work, f"preview_{i:03d}.png"))
        previews.append((prev, f"第 {i} 張"))
        for j, it in enumerate(items, 1):
            rows.append([i, j, it["text"], True])
    df = pd.DataFrame(rows, columns=COLS)
    note = f"共 {len(paths)} 張、{len(rows)} 段文字。請校對表格後按「② 產生 PPT」。"
    return previews, df, store, note


def generate(store, table, fast, progress=gr.Progress()):
    if not store:
        raise gr.Error("請先按「① 辨識文字」。")
    df = table if isinstance(table, pd.DataFrame) else pd.DataFrame(table, columns=COLS)
    edits = {}
    for _, r in df.iterrows():
        try:
            key = (int(r[COLS[0]]), int(r[COLS[1]]))
        except (TypeError, ValueError):
            continue
        keep = r[COLS[3]]
        keep = keep if isinstance(keep, bool) else str(keep).lower() in ("true", "1", "✓")
        text = "" if pd.isna(r[COLS[2]]) else str(r[COLS[2]])
        edits[key] = (keep, text)

    slides = []
    for i, s in enumerate(store, 1):
        lines = []
        for j, it in enumerate(s["items"], 1):
            keep, text = edits.get((i, j), (True, it["text"]))
            if keep:
                lines.append({"box": it["box"], "text": text})
        slides.append({"image": s["image"], "lines": lines})

    work = tempfile.mkdtemp(prefix="s2p_out_")
    out = os.path.join(work, time.strftime("可編輯簡報_%Y%m%d_%H%M.pptx"))
    t0 = time.time()

    def tick(n, total):
        progress((n - 1) / total, desc=f"處理第 {n}/{total} 張")

    s2p.build_deck(slides, out, work, fast=fast, progress=tick)
    secs = time.time() - t0
    return out, f"完成：{len(slides)} 張，用時 {secs:.0f} 秒（平均每張 {secs / len(slides):.0f} 秒）。"


with gr.Blocks(title="圖片簡報轉可編輯 PPT") as demo:
    gr.Markdown("# 圖片簡報轉可編輯 PPT")
    gr.Markdown(GUIDE)
    store = gr.State([])
    with gr.Row():
        with gr.Column(scale=1):
            files = gr.File(label="上傳簡報圖片（PNG／JPG，可多張）",
                            file_count="multiple", file_types=["image"])
            btn_ocr = gr.Button("① 辨識文字", variant="primary")
        with gr.Column(scale=2):
            gallery = gr.Gallery(label="辨識結果（紅框數字＝表格編號）", columns=2, height=420)
    note = gr.Markdown()
    table = gr.Dataframe(headers=COLS, datatype=["number", "number", "str", "bool"],
                         interactive=True, static_columns=[0, 1], wrap=True,
                         label="辨識文字（可直接修改）", column_widths=["8%", "8%", "70%", "14%"])
    fast = gr.Checkbox(value=False, label="快速模式（每張約 1–3 秒；背景複雜處可能留下淡淡痕跡）")
    btn_ppt = gr.Button("② 產生 PPT", variant="primary")
    result = gr.File(label="下載 PPT")
    status = gr.Markdown()

    btn_ocr.click(recognise, inputs=files, outputs=[gallery, table, store, note])
    btn_ppt.click(generate, inputs=[store, table, fast], outputs=[result, status])

if __name__ == "__main__":
    print("  已啟動。若瀏覽器沒有自動開啟，請自行輸入 http://127.0.0.1:7860", flush=True)
    demo.queue(default_concurrency_limit=1).launch(
        theme=gr.themes.Soft(), server_name="127.0.0.1", inbrowser=True,
        ssr_mode=False, share=False)
