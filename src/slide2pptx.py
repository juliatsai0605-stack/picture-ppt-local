"""Turn slide images into an editable PowerPoint deck.

Pipeline
  1. detect_text()   OCR every text line (PP-OCRv5 reads Traditional Chinese).
  2. erase_text()    remove the chosen lines from the image. Flat or gradient
                     backgrounds are filled by interpolation (instant); busy
                     backgrounds use the LaMa inpainting model (slower).
                     Pixels outside the text areas are never changed.
  3. build_deck()    one slide per image: the clean image as the slide
                     background, one editable text box per line, matched in
                     position, size, colour and weight.
"""
from __future__ import annotations

import glob
import os
import re

import cv2
import numpy as np
from lxml import etree
from PIL import ImageFont
from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu

FONT_EA = "微軟正黑體"
FONT_LATIN = "Arial"
SLIDE_W, SLIDE_H = Emu(12192000), Emu(6858000)  # 16:9, 13.333 x 7.5 in
WIN = 512                                          # LaMa input size

_ocr = None
_lama = None
_font_path, _font_index = None, 0
MODEL_DIR = os.environ.get("S2P_MODEL_DIR", "")


def _model(local_name, repo, filename):
    """Use the bundled model file when present (offline), else download it."""
    if MODEL_DIR and os.path.exists(os.path.join(MODEL_DIR, local_name)):
        return os.path.join(MODEL_DIR, local_name)
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo, filename)


def imread(path):
    """Read an image from any path, including non-ASCII (Chinese) Windows paths."""
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"無法讀取圖片：{os.path.basename(path)}")
    return img


def imwrite(path, img):
    ok, buf = cv2.imencode(os.path.splitext(path)[1] or ".png", img)
    if not ok:
        raise ValueError(f"無法寫入圖片：{os.path.basename(path)}")
    buf.tofile(path)
    return path


# ----------------------------------------------------------------- OCR ---

def _get_ocr():
    """RapidOCR detector + PP-OCRv5 mobile recogniser (reads Traditional Chinese natively)."""
    global _ocr
    if _ocr is None:
        import yaml
        from rapidocr_onnxruntime import RapidOCR
        from rapidocr_onnxruntime.ch_ppocr_v3_rec.text_recognize import TextRecognizer
        repo = "PaddlePaddle/PP-OCRv5_mobile_rec_onnx"
        model = _model("ppocrv5_rec.onnx", repo, "inference.onnx")
        chars = yaml.safe_load(open(_model("ppocrv5_rec.yml", repo, "inference.yml"), encoding="utf-8"))
        chars = list(chars["PostProcess"]["character_dict"])
        _ocr = RapidOCR()
        _ocr.text_recognizer = TextRecognizer({
            "model_path": model, "keys_path": chars, "use_cuda": False,
            "rec_img_shape": [3, 48, 320], "rec_batch_num": 6})
    return _ocr


def _tidy(text: str) -> str:
    # OCR often reads the ideographic comma and full-width colon as look-alikes
    if re.search(r"[\u4e00-\u9fff]", text):
        text = text.replace("丶", "、").replace(":", "：")
    return text


def detect_text(image_path: str, min_height: int = 12, min_score: float = 0.5):
    """Return [{'box': [x0, y0, x1, y1], 'text': str, 'score': float}], top to bottom."""
    result, _ = _get_ocr()(imread(image_path))
    items = []
    for pts, text, score in result or []:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
        if y1 - y0 < min_height or float(score) < min_score or not text.strip():
            continue
        items.append({"box": [x0, y0, x1, y1], "text": _tidy(text.strip()),
                      "score": round(float(score), 2)})
    items.sort(key=lambda it: (it["box"][1] // 10, it["box"][0]))
    return items


def draw_numbers(image_path: str, items, out_path: str):
    """Preview: the image with each detected line boxed and numbered."""
    img = imread(image_path)
    for i, it in enumerate(items, 1):
        x0, y0, x1, y1 = it["box"]
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 2)
        label = str(i)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x0, y0 - th - 6), (x0 + tw + 6, y0), (0, 0, 255), -1)
        cv2.putText(img, label, (x0 + 3, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2, cv2.LINE_AA)
    imwrite(out_path, img)
    return out_path


# ------------------------------------------------------------- erasing ---

def _get_lama():
    global _lama
    if _lama is None:
        import onnxruntime as ort
        path = _model("lama_fp32.onnx", "Carve/LaMa-ONNX", "lama_fp32.onnx")
        _lama = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    return _lama


def _window(c0, c1, total):
    s = int((c0 + c1) / 2 - WIN / 2)
    return max(0, min(s, total - WIN))


def _lama_fill(img, mask):
    """Inpaint each masked region from a native-resolution window centred on it."""
    sess = _get_lama()
    h, w = mask.shape
    ph, pw = max(0, WIN - h), max(0, WIN - w)
    if ph or pw:
        img = cv2.copyMakeBorder(img, 0, ph, 0, pw, cv2.BORDER_REFLECT)
        mask = cv2.copyMakeBorder(mask, 0, ph, 0, pw, cv2.BORDER_CONSTANT, value=0)
    H, W = mask.shape
    out = img.copy()
    remaining = mask > 0
    n, labels, stats, _ = cv2.connectedComponentsWithStats(remaining.astype(np.uint8), 8)
    strip = WIN * 3 // 4
    for i in sorted(range(1, n), key=lambda k: -stats[k, cv2.CC_STAT_AREA]):
        x, y, cw, ch = stats[i, :4]
        comp = labels == i
        for sx in range(x, x + cw, strip):
            ex = min(x + cw, sx + strip)
            for sy in range(y, y + ch, strip):
                ey = min(y + ch, sy + strip)
                wx, wy = _window(sx, ex, W), _window(sy, ey, H)
                part = np.zeros_like(comp)
                part[sy:ey, sx:ex] = comp[sy:ey, sx:ex]
                take = part[wy:wy + WIN, wx:wx + WIN]
                if not take.any():
                    continue
                hole = remaining[wy:wy + WIN, wx:wx + WIN]
                rgb = cv2.cvtColor(out[wy:wy + WIN, wx:wx + WIN], cv2.COLOR_BGR2RGB)
                im = (rgb.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
                mk = hole.astype(np.float32)[None, None]
                res = sess.run(None, {"image": im, "mask": mk})[0][0].transpose(1, 2, 0)
                if res.max() <= 1.5:
                    res = res * 255.0
                res = cv2.cvtColor(np.clip(res, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
                region = out[wy:wy + WIN, wx:wx + WIN]
                region[take] = res[take]
                remaining[wy:wy + WIN, wx:wx + WIN][take] = False
    return out[:h, :w]


def _smooth(v, k):
    k = max(3, min(k, (len(v) // 2) * 2 - 1)) | 1
    return cv2.GaussianBlur(v[:, None, :], (1, k), 0)[:, 0, :] if len(v) >= 3 else v


def _flat_fill(img, y0, y1, x0, x1):
    """Interpolate a rectangle from the pixels just outside it (no texture copied)."""
    H, W = img.shape[:2]
    src = img.astype(np.float32)
    h, w = y1 - y0, x1 - x0
    top = src[max(0, y0 - 3):max(1, y0 - 1), x0:x1].mean(0) if y0 >= 2 else None
    bot = src[min(H - 1, y1 + 1):min(H, y1 + 3), x0:x1].mean(0) if y1 + 2 <= H else None
    top = bot if top is None else top
    bot = top if bot is None else bot
    top, bot = _smooth(top, 15), _smooth(bot, 15)
    v = ((np.arange(h) + 0.5) / h)[:, None, None]
    patch = (1 - v) * top[None] + v * bot[None]
    if w < 1.5 * h:  # compact hole: blend in left and right edges too
        lft = src[y0:y1, max(0, x0 - 3):max(1, x0 - 1)].mean(1) if x0 >= 2 else None
        rgt = src[y0:y1, min(W - 1, x1 + 1):min(W, x1 + 3)].mean(1) if x1 + 2 <= W else None
        lft = rgt if lft is None else lft
        rgt = lft if rgt is None else rgt
        lft, rgt = _smooth(lft, 7), _smooth(rgt, 7)
        u = ((np.arange(w) + 0.5) / w)[None, :, None]
        horiz = (1 - u) * lft[:, None] + u * rgt[:, None]
        corners = ((1 - u) * (1 - v) * (top[0] + lft[0]) / 2 + u * (1 - v) * (top[-1] + rgt[0]) / 2
                   + (1 - u) * v * (bot[0] + lft[-1]) / 2 + u * v * (bot[-1] + rgt[-1]) / 2)
        patch = patch + horiz - corners
    img[y0:y1, x0:x1] = np.clip(patch, 0, 255).astype(np.uint8)


def _is_flat(img, X0, Y0, X1, Y1, ring=6):
    H, W = img.shape[:2]
    a0, b0, a1, b1 = max(0, X0 - ring), max(0, Y0 - ring), min(W, X1 + ring), min(H, Y1 + ring)
    gray = cv2.cvtColor(img[b0:b1, a0:a1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    mag = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))
    band = np.ones(mag.shape, bool)
    band[Y0 - b0:Y1 - b0, X0 - a0:X1 - a0] = False
    return (mag[band] > 60).mean() < 0.12


def _merge_rects(rects):
    """Union rectangles that overlap, so neighbouring lines are erased together."""
    rects = [list(r) for r in rects]
    merged = True
    while merged:
        merged = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    rects[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    rects.pop(j)
                    merged = True
                    break
            if merged:
                break
    return rects


def erase_text(image_path: str, boxes, fast: bool = False, pad: int = 5, grow: int = 2):
    """Return the image (BGR array) with every box erased.

    fast=True never runs the AI model: every box is interpolated, which is
    instant but can leave a soft patch on busy backgrounds.
    """
    img = imread(image_path)
    h, w = img.shape[:2]
    padded = [[max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]
              for x0, y0, x1, y1 in boxes]
    lama_mask = np.zeros((h, w), np.uint8)
    for X0, Y0, X1, Y1 in _merge_rects(padded):
        if fast or _is_flat(img, X0, Y0, X1, Y1):
            _flat_fill(img, max(0, Y0 - grow), min(h, Y1 + grow), max(0, X0 - grow), min(w, X1 + grow))
        else:
            lama_mask[Y0:Y1, X0:X1] = 255
    if lama_mask.any():
        img = _lama_fill(img, lama_mask)
    return img


# -------------------------------------------------------------- layout ---

def _measure_font():
    global _font_path, _font_index
    if _font_path is None:
        win = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        cands = [os.path.join(win, f) for f in ("msjhbd.ttc", "msjh.ttc") if os.path.exists(os.path.join(win, f))] or \
            sorted(glob.glob("/usr/share/fonts/**/NotoSansCJK-Bold.ttc", recursive=True)) or \
            sorted(glob.glob("/usr/share/fonts/**/*CJK*.tt[cf]", recursive=True))
        _font_path = cands[0] if cands else ""
        for i in range(10):
            try:
                name = ImageFont.truetype(_font_path, 20, index=i).getname()[0]
                if "TC" in name or "JhengHei" in name:
                    _font_index = i
                    break
            except Exception:
                break
    return _font_path, _font_index


def text_width(text: str, px: float) -> float:
    path, idx = _measure_font()
    if not path:  # rough fallback: CJK 1 em, others 0.55 em
        return sum(px if ord(c) > 0x2E80 else px * 0.55 for c in text)
    return ImageFont.truetype(path, max(1, int(px)), index=idx).getlength(text)


def _split_runs(text: str):
    """'布建：網路…' -> ['布建：', '網路…'] so label and value can differ in weight."""
    m = re.match(r"^(.{1,6}?[：:])(.+)$", text)
    return [m.group(1), m.group(2)] if m else [text]


def _colour_runs(orig, clean, box, text):
    """Split text into runs of the same colour by sampling each character cell."""
    x0, y0, x1, y1 = box
    bw = x1 - x0
    widths = [text_width(c, 100) for c in text]
    total = sum(widths) or 1
    cols, cx = [], float(x0)
    for wd in widths:
        span = bw * wd / total
        a, b = int(cx), max(int(cx + span), int(cx) + 2)
        cols.append(_colour(orig, clean, (a, y0, min(b, x1), y1)) if a < x1 else (255, 255, 255))
        cx += span
    runs = []  # [text, [colours]]
    for ch, col in zip(text, cols):
        if runs and (ch in "、，。・·：:（）() " or
                     np.linalg.norm(_lab(col) - _lab(np.median(runs[-1][1], axis=0).astype(int))) < 28):
            runs[-1][0] += ch
            runs[-1][1].append(col)
        else:
            runs.append([ch, [col]])
    # absorb one-character runs (usually punctuation or a sampling blip) into a neighbour
    i = 0
    while len(runs) > 1 and i < len(runs):
        if len(runs[i][0]) == 1:
            j = i - 1 if i > 0 else i + 1
            if j < i:
                runs[j][0] += runs[i][0]
            else:
                runs[j][0] = runs[i][0] + runs[j][0]
            runs[j][1] += runs[i][1]
            runs.pop(i)
            i = 0
        else:
            i += 1
    return [(t, tuple(int(v) for v in np.median(c, axis=0))) for t, c in runs]


def _ink(orig, clean, box):
    x0, y0, x1, y1 = box
    a = orig[y0:y1, x0:x1].astype(np.float32)
    b = clean[y0:y1, x0:x1].astype(np.float32)
    return a, np.linalg.norm(a - b, axis=2)


def _colour(orig, clean, box):
    """Colour of the strongest ink in box (pixels that changed most when erased)."""
    a, d = _ink(orig, clean, box)
    if d.size == 0 or d.max() < 10:
        return (255, 255, 255)
    px = a.reshape(-1, 3)[d.reshape(-1) >= 0.6 * d.max()]
    b, g, r = np.median(px, axis=0)
    return int(r), int(g), int(b)


def _lab(rgb):
    px = np.uint8([[list(rgb[::-1])]])
    return cv2.cvtColor(px, cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)


def _is_bold(orig, clean, box):
    _, d = _ink(orig, clean, box)
    if d.size == 0 or d.max() < 10:
        return False
    return (box[3] - box[1]) >= 30 and (d > 0.5 * d.max()).mean() > 0.30


def _set_background(slide, image_path):
    part, rid = slide.part.get_or_add_image_part(image_path)
    csld = slide._element.find(qn("p:cSld"))
    bg = etree.Element(qn("p:bg"))
    csld.insert(0, bg)
    bgpr = etree.SubElement(bg, qn("p:bgPr"))
    fill = etree.SubElement(bgpr, qn("a:blipFill"), dpi="0", rotWithShape="1")
    etree.SubElement(fill, qn("a:blip"), {qn("r:embed"): rid})
    etree.SubElement(fill, qn("a:srcRect"))
    etree.SubElement(etree.SubElement(fill, qn("a:stretch")), qn("a:fillRect"))
    etree.SubElement(bgpr, qn("a:effectLst"))


def _style_run(run, size_pt, rgb, bold, spacing_pt, shadow):
    rpr = run._r.get_or_add_rPr()
    for k, v in (("lang", "zh-TW"), ("altLang", "en-US"),
                 ("sz", str(max(100, int(round(size_pt * 100))))), ("b", "1" if bold else "0")):
        rpr.set(k, v)
    if spacing_pt:
        rpr.set("spc", str(int(round(spacing_pt * 100))))
    for child in list(rpr):
        rpr.remove(child)
    fill = etree.SubElement(rpr, qn("a:solidFill"))
    etree.SubElement(fill, qn("a:srgbClr"), val="%02X%02X%02X" % rgb)
    if shadow:
        eff = etree.SubElement(rpr, qn("a:effectLst"))
        sh = etree.SubElement(eff, qn("a:outerShdw"), blurRad="38100", dist="22860",
                              dir="2700000", algn="tl", rotWithShape="0")
        c = etree.SubElement(sh, qn("a:srgbClr"), val="000000")
        etree.SubElement(c, qn("a:alpha"), val="55000")
    etree.SubElement(rpr, qn("a:latin"), typeface=FONT_LATIN)
    etree.SubElement(rpr, qn("a:ea"), typeface=FONT_EA)


def _add_textbox(slide, orig, clean, box, text, sx, sy):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    runs = _split_runs(text)
    size_h = bh * 0.92
    size_w = bw / max(1e-6, text_width(text, 100) / 100)
    spacing_px = 0.0
    if size_w > size_h * 1.45 and len(text) > 2:      # visibly letter-spaced line
        size_px = size_h
        spacing_px = max(0.0, (bw - text_width(text, size_px)) / (len(text) - 1))
    else:
        size_px = min(size_w, size_h * 1.1)
    size_pt = size_px * sy / 12700
    spacing_pt = spacing_px * sy / 12700

    label = runs[0] if len(runs) > 1 else None
    styles = []
    pos = 0
    for r_text, rgb in _colour_runs(orig, clean, box, text):
        if label is not None:
            # keep the label (before the colon) bold and the rest regular
            cut = len(label) - pos
            if 0 < cut < len(r_text):
                styles.append((r_text[:cut], rgb, True))
                styles.append((r_text[cut:], rgb, False))
            else:
                styles.append((r_text, rgb, pos < len(label)))
        else:
            styles.append((r_text, rgb, None))
        pos += len(r_text)
    whole_bold = _is_bold(orig, clean, box)
    styles = [(t, c, whole_bold if b is None else b) for t, c, b in styles]
    shadow = size_px >= 36

    extra = max(bw * 0.15, 20)
    height = bh * 1.6
    tb = slide.shapes.add_textbox(Emu(int(x0 * sx)), Emu(int(((y0 + y1) / 2 - height / 2) * sy)),
                                  Emu(int((bw + extra) * sx)), Emu(int(height * sy)))
    tb.name = "文字 " + text[:12]
    tf = tb.text_frame
    tf.word_wrap = False
    tf.auto_size = None
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    for r_text, rgb, bold in styles:
        r = p.add_run()
        r.text = r_text
        _style_run(r, size_pt, rgb, bold, spacing_pt, shadow)


def build_deck(slides, out_path: str, workdir: str, fast: bool = False, progress=None):
    """slides: [{'image': path, 'lines': [{'box': [...], 'text': str}]}, ...]

    A line with empty text is erased from the picture without a text box.
    """
    prs = Presentation()
    first = imread(slides[0]["image"])
    fh, fw = first.shape[:2]
    prs.slide_width = SLIDE_W                      # 13.333 in wide, height follows the image
    prs.slide_height = Emu(int(SLIDE_W * fh / fw))
    blank = prs.slide_layouts[6]
    for n, s in enumerate(slides, 1):
        if progress:
            progress(n, len(slides))
        orig = imread(s["image"])
        h, w = orig.shape[:2]
        clean = erase_text(s["image"], [ln["box"] for ln in s["lines"]], fast=fast)
        clean_path = os.path.join(workdir, f"clean_{n:03d}.png")
        imwrite(clean_path, clean)
        slide = prs.slides.add_slide(blank)
        # 底圖做成置底的圖片物件（不用投影片背景），複製貼到其他簡報時才不會遺失
        pic = slide.shapes.add_picture(clean_path, 0, 0, prs.slide_width, prs.slide_height)
        pic.name = "底圖"
        sx, sy = prs.slide_width / w, prs.slide_height / h
        for ln in s["lines"]:
            if ln["text"].strip():
                _add_textbox(slide, orig, clean, ln["box"], ln["text"].strip(), sx, sy)
    prs.save(out_path)
    return out_path
