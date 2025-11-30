# -*- coding: utf-8 -*-
"""
Bilgisayarla Görü Ödevi (Soru 1–5) — input/ klasöründen okur, ZIP yok, Pillow 10+ uyumlu
- S1: Orijinal + (Parlaklık, Kontrast, Negatif, Eşik) — yan yana
- S2: Gri histogram (MANUEL) + mean/std/entropy/min/max (konsol + CSV)
- S3: Orijinal, Kontrast Germe ve ikisinin histogramları — 2x2 kolaj
- S4: Orijinal & Hist. Eşitleme yan yana + altlarına histogramlar — 2x2 kolaj
- S5: Gamma {0.5,1.0,1.5,2.0,2.5} — yan yana + kısa açıklama .txt
"""
import os, csv, math
from typing import List, Tuple, Dict
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

# ---------------- Ayarlar ----------------
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
IMG_DIR   = os.path.join(BASE_DIR, "input")            # <-- GÖRSELLER BURADAN ALINIR
OUT_DIR   = os.path.join(BASE_DIR, "deliverable_final_out")
MAX_SIDE  = None   # Örn. hız için 1400 yapabilirsiniz; None = dokunma
ALLOWED_EXTS = {".tif",".tiff",".jpg",".jpeg",".png",".bmp",".webp"}

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# --------------- Metin yardımcıları ---------------
TR_MAP = str.maketrans({"ı":"i","İ":"I","ş":"s","Ş":"S","ğ":"g","Ğ":"G","ö":"o","Ö":"O","ç":"c","Ç":"C","ü":"u","Ü":"U"})
def asciiize(s: str) -> str: return s.translate(TR_MAP)

# Pillow 10+: textsize kaldırıldı → textbbox
def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> Tuple[int,int]:
    x0,y0,x1,y1 = draw.textbbox((0,0), text, font=font); return x1-x0, y1-y0

# --------------- I/O ---------------
def load_rgb(path: str) -> np.ndarray:
    im = Image.open(path)
    if MAX_SIDE is not None:
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.BICUBIC)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return np.array(im, dtype=np.uint8)

def to_gray_uint8(arr_rgb: np.ndarray) -> np.ndarray:
    return np.array(Image.fromarray(arr_rgb, "RGB").convert("L"), dtype=np.uint8)

def rgb_to_hsv_uint8(arr: np.ndarray) -> np.ndarray:
    return np.array(Image.fromarray(arr, "RGB").convert("HSV"), dtype=np.uint8)

def hsv_to_rgb_uint8(arr: np.ndarray) -> np.ndarray:
    return np.array(Image.fromarray(arr.astype(np.uint8), "HSV").convert("RGB"), dtype=np.uint8)

# --------------- Histogram & İstatistik (MANUEL) ---------------
def compute_histogram(chan_uint8: np.ndarray) -> np.ndarray:
    hist = np.zeros(256, dtype=np.int64)
    np.add.at(hist, chan_uint8.ravel(), 1)
    return hist

def render_hist_png(hist: np.ndarray, title: str, path: str):
    xs = np.arange(256)
    plt.figure()
    plt.bar(xs, hist)
    plt.title(asciiize(title))
    plt.xlabel("Gray level (0-255)")
    plt.ylabel("Pixel count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def image_stats_from_hist(hist: np.ndarray) -> Dict[str, float]:
    total = int(hist.sum())
    if total == 0:
        return {"mean":0.0,"std":0.0,"entropy":0.0,"min":0,"max":0}
    xs = np.arange(256, dtype=np.float64)
    p = hist / total
    mean = float((xs * p).sum())
    var  = float(((xs - mean) ** 2 * p).sum())
    std  = math.sqrt(var)
    nz = p > 0
    entropy = float(-(p[nz] * np.log2(p[nz])).sum())
    nz_idx = np.where(hist > 0)[0]
    return {"mean":mean,"std":std,"entropy":entropy,"min":int(nz_idx[0]),"max":int(nz_idx[-1])}

# --------------- Nokta İşlemleri (HSV-V), Negatif RGB ---------------
def brightness_on_V(rgb: np.ndarray, delta: int) -> np.ndarray:
    hsv = rgb_to_hsv_uint8(rgb); V = hsv[...,2].astype(np.int16) + delta
    hsv[...,2] = np.clip(V, 0, 255).astype(np.uint8); return hsv_to_rgb_uint8(hsv)

def contrast_on_V(rgb: np.ndarray, factor: float) -> np.ndarray:
    hsv = rgb_to_hsv_uint8(rgb); V = hsv[...,2].astype(np.float32)
    V2 = factor * (V - 128.0) + 128.0
    hsv[...,2] = np.clip(V2, 0, 255).astype(np.uint8); return hsv_to_rgb_uint8(hsv)

def negative_rgb(rgb: np.ndarray) -> np.ndarray: return 255 - rgb

def threshold_on_V(rgb: np.ndarray, thr: int) -> np.ndarray:
    V = rgb_to_hsv_uint8(rgb)[...,2]; mask = (V > thr).astype(np.uint8) * 255
    return np.stack([mask,mask,mask], axis=-1)

def contrast_stretch_on_V(rgb: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv_uint8(rgb); V = hsv[...,2].astype(np.float32)
    vmin, vmax = float(V.min()), float(V.max())
    if vmax <= vmin: V2 = np.zeros_like(V, dtype=np.uint8)
    else: V2 = np.clip((V - vmin)/(vmax - vmin) * 255.0, 0, 255).astype(np.uint8)
    hsv[...,2] = V2; return hsv_to_rgb_uint8(hsv)

def hist_equalize_manual_channel(chan: np.ndarray) -> np.ndarray:
    hist = compute_histogram(chan); cdf = np.cumsum(hist).astype(np.float64) / chan.size
    tf = np.floor(255 * cdf + 0.5).astype(np.uint8); return tf[chan]

def hist_equalize_on_V(rgb: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv_uint8(rgb); hsv[...,2] = hist_equalize_manual_channel(hsv[...,2])
    return hsv_to_rgb_uint8(hsv)

def gamma_on_V(rgb: np.ndarray, gamma: float) -> np.ndarray:
    hsv = rgb_to_hsv_uint8(rgb); V = hsv[...,2].astype(np.float32)/255.0
    Y = np.power(V, gamma) * 255.0; hsv[...,2] = np.clip(Y,0,255).astype(np.uint8)
    return hsv_to_rgb_uint8(hsv)

# --------------- Kolaj Yardımcıları ---------------
def resize_same_h(im: Image.Image, H: int) -> Image.Image:
    if im.height == H: return im
    new_w = max(1, int(round(im.width * (H / im.height))))
    return im.resize((new_w, H), Image.BICUBIC)

def strip_rgb(images: List[Image.Image], titles: List[str], pad=8, title_h=24) -> Image.Image:
    H = max(im.height for im in images)
    ims = [resize_same_h(im, H) for im in images]
    W = sum(im.width for im in ims) + pad*(len(ims)+1)
    total_h = H + title_h + pad*2
    canvas = Image.new("RGB", (W, total_h), (255,255,255))
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default()
    x = pad
    for im, t in zip(ims, titles):
        t = asciiize(t); tw, th = _text_size(draw, t, font)
        draw.text((x + (im.width - tw)//2, pad), t, fill=(0,0,0), font=font)
        canvas.paste(im, (x, pad + title_h))
        x += im.width + pad
    return canvas

def paste_center(canvas: Image.Image, panel: Image.Image, box: Tuple[int,int,int,int]):
    x,y,w,h = box; sw,sh = panel.size; s = min(w/sw, h/sh)
    nw,nh = max(1,int(sw*s)), max(1,int(sh*s))
    panel2 = panel.resize((nw,nh), Image.BICUBIC)
    canvas.paste(panel2, (x + (w-nw)//2, y + (h-nh)//2))

def grid_2x2_rgb(panels: List[Image.Image], titles: List[str],
                 cell_w=420, cell_h=320, pad=12, title_h=26) -> Image.Image:
    cols, rows = 2,2
    W = cols*cell_w + (cols+1)*pad
    H = rows*(cell_h+title_h) + (rows+1)*pad
    canvas = Image.new("RGB", (W,H), (255,255,255))
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default()
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= len(panels): break
            x = pad + c*(cell_w+pad); y = pad + r*(cell_h+title_h+pad)
            t = asciiize(titles[idx]); tw, th = _text_size(draw, t, font)
            draw.text((x + (cell_w - tw)//2, y), t, fill=(0,0,0), font=font)
            paste_center(canvas, panels[idx], (x, y+title_h, cell_w, cell_h))
            idx += 1
    return canvas

# --------------- Ana Yürütme ---------------
def main():
    files = [f for f in os.listdir(IMG_DIR)
             if os.path.splitext(f)[1].lower() in ALLOWED_EXTS]
    if not files:
        print(f"Uyarı: '{IMG_DIR}' klasöründe işlenecek görsel yok. Görsellerini buraya koy ve tekrar çalıştır.")
        return

    stats_rows = []

    for fname in files:
        try:
            name, ext = os.path.splitext(fname)
            path = os.path.join(IMG_DIR, fname)
            rgb = load_rgb(path)
            pil_orig = Image.fromarray(rgb, 'RGB')
            print(f"\n==> İşleniyor: {fname}")

            # --- S1 ---
            s1_imgs = [
                pil_orig,
                Image.fromarray(brightness_on_V(rgb, +40), 'RGB'),
                Image.fromarray(contrast_on_V(rgb, 1.5), 'RGB'),
                Image.fromarray(negative_rgb(rgb), 'RGB'),
                Image.fromarray(threshold_on_V(rgb, 128), 'RGB'),
            ]
            strip_rgb(s1_imgs, ["Orijinal","Parlaklik +40","Kontrast 1.5","Negatif","Esik 128"])\
                .save(os.path.join(OUT_DIR, f"{name}_S1_yanyana.png"))
            print("[S1] tamam")

            # --- S2 ---
            gray = to_gray_uint8(rgb)
            h_gray = compute_histogram(gray)
            render_hist_png(h_gray, f"{name} - Gri Histogram", os.path.join(OUT_DIR, f"{name}_S2_hist_gray.png"))
            stats = image_stats_from_hist(h_gray)
            stats_rows.append({"image": name, **stats})
            print(f"[S2] mean={stats['mean']:.2f}, std={stats['std']:.2f}, entropy={stats['entropy']:.4f}, "
                  f"min={stats['min']}, max={stats['max']}")

            # --- S3 ---
            cs_rgb = contrast_stretch_on_V(rgb)
            V_orig = rgb_to_hsv_uint8(rgb)[...,2]
            V_cs   = rgb_to_hsv_uint8(cs_rgb)[...,2]
            p1 = os.path.join(OUT_DIR, f"{name}_S3_hist_V_orig.png")
            p2 = os.path.join(OUT_DIR, f"{name}_S3_hist_V_cs.png")
            render_hist_png(compute_histogram(V_orig), f"{name} - V Hist (Orj.)", p1)
            render_hist_png(compute_histogram(V_cs),   f"{name} - V Hist (Germe)", p2)
            grid_2x2_rgb(
                [Image.fromarray(rgb,'RGB'), Image.fromarray(cs_rgb,'RGB'),
                 Image.open(p1).convert("RGB"), Image.open(p2).convert("RGB")],
                ["Orijinal", "Kontrast Germe (V)", "V Hist (Orj.)", "V Hist (Germe)"]
            ).save(os.path.join(OUT_DIR, f"{name}_S3_2x2.png"))
            print("[S3] tamam")

            # --- S4 ---
            he_rgb = hist_equalize_on_V(rgb)
            V_he = rgb_to_hsv_uint8(he_rgb)[...,2]
            p3 = os.path.join(OUT_DIR, f"{name}_S4_hist_V_orig.png")
            p4 = os.path.join(OUT_DIR, f"{name}_S4_hist_V_he.png")
            render_hist_png(compute_histogram(V_orig), f"{name} - V Hist (Orj.)", p3)
            render_hist_png(compute_histogram(V_he),   f"{name} - V Hist (HE)", p4)
            strip_rgb([Image.fromarray(rgb,'RGB'), Image.fromarray(he_rgb,'RGB')],
                      ["Orijinal","Hist. Esitleme (V, manuel)"])\
                .save(os.path.join(OUT_DIR, f"{name}_S4_yanyana.png"))
            grid_2x2_rgb(
                [Image.fromarray(rgb,'RGB'), Image.fromarray(he_rgb,'RGB'),
                 Image.open(p3).convert("RGB"), Image.open(p4).convert("RGB")],
                ["Orijinal","Hist. Esitleme (V, manuel)","V Hist (Orj.)","V Hist (HE)"]
            ).save(os.path.join(OUT_DIR, f"{name}_S4_2x2.png"))
            print("[S4] tamam")

            # --- S5 ---
            gammas = [0.5, 1.0, 1.5, 2.0, 2.5]
            panels = [pil_orig] + [Image.fromarray(gamma_on_V(rgb, g), 'RGB') for g in gammas]
            titles = ["Orijinal"] + [f"gamma={g}" for g in gammas]
            strip_rgb(panels, titles).save(os.path.join(OUT_DIR, f"{name}_S5_gamma_strip.png"))
            with open(os.path.join(OUT_DIR, f"{name}_S5_gamma_analysis.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join([
                    f"{name} - Gamma Analizi:",
                    "  gamma=0.5: karanlik alanlar aydinlanir, detay artar.",
                    "  gamma=1.0: degisim yok (referans).",
                    "  gamma=1.5: orta tonlar koyulasir, parlak alanlar baskilanir.",
                    "  gamma=2.0: daha cok koyulastirma; parlak ayrintilar kaybolabilir.",
                    "  gamma=2.5: asiri koyulastirma; sadece cok parlak bolgeler belirgin kalir.",
                    "  Kullanim: <1 aydinlatma; >1 parlakligi baskilama/koyulastirma.",
                    ""
                ]))
            print("[S5] tamam")

        except Exception as e:
            print(f"[HATA] {fname} işlenemedi: {e}")

    # S2 CSV
    with open(os.path.join(OUT_DIR, "S2_stats.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image","mean","std","entropy","min","max"])
        w.writeheader()
        for r in stats_rows: w.writerow(r)

    print("\nBitti ✅  Çıktılar:", os.path.abspath(OUT_DIR))
    print("Not: Görseller input/ klasöründen alınmıştır.")

if __name__ == "__main__":
    main()
