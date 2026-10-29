"""Etkinlik Var simgelerini üretir (site, Android uygulaması, Play Store görselleri).
Çalıştırma (05_ETKINLIK_MERKEZI klasöründe):  py android/ikon_uret.py
Gerekli: Pillow, Windows'taki Segoe UI yazı tipi."""
import os

from PIL import Image, ImageDraw, ImageFont

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TURUNCU, PEMBE, KOYU = (217, 72, 15), (194, 37, 92), (29, 27, 22)
YAZI = "C:/Windows/Fonts/seguibl.ttf"   # Segoe UI Black


def gradyan(g, y):
    """Sol üstten sağ alta turuncu → pembe geçiş."""
    im = Image.new("RGB", (g, y))
    px = im.load()
    for i in range(g):
        for j in range(y):
            t = (i / g + j / y) / 2
            px[i, j] = tuple(round(a + (b - a) * t) for a, b in zip(TURUNCU, PEMBE))
    return im


def takvim(ciz, x, y, b):
    """b genişliğinde beyaz takvim yaprağı; içinde 'VAR' yazar."""
    r = b * 0.16
    ciz.rounded_rectangle([x, y, x + b, y + b], radius=r, fill="white")
    ciz.rounded_rectangle([x, y, x + b, y + b * 0.3], radius=r, fill=KOYU)
    ciz.rectangle([x, y + b * 0.18, x + b, y + b * 0.3], fill=KOYU)
    for cx in (x + b * 0.3, x + b * 0.7):     # takvim halkaları
        ciz.rounded_rectangle([cx - b * 0.05, y - b * 0.09, cx + b * 0.05, y + b * 0.12], radius=b * 0.05, fill="white")
    f = ImageFont.truetype(YAZI, round(b * 0.42))
    ciz.text((x + b / 2, y + b * 0.65), "VAR", font=f, fill=TURUNCU, anchor="mm")


def ikon(boyut, guvenli=0.62, yuvarlak=True):
    """guvenli: takvimin kenara oranı (maskable için daha küçük tutulur)."""
    s = 4                                       # yumuşak kenar için büyük çiz, sonra küçült
    g = boyut * s
    im = gradyan(g, g)
    if yuvarlak:
        maske = Image.new("L", (g, g), 0)
        ImageDraw.Draw(maske).rounded_rectangle([0, 0, g - 1, g - 1], radius=g * 0.22, fill=255)
        bos = Image.new("RGBA", (g, g), (0, 0, 0, 0))
        bos.paste(im, mask=maske)
        im = bos
    b = g * guvenli
    takvim(ImageDraw.Draw(im), (g - b) / 2, (g - b) / 2 + g * 0.03, b)
    return im.resize((boyut, boyut), Image.LANCZOS)


def kaydet(im, *yol):
    tam = os.path.join(KOK, *yol)
    os.makedirs(os.path.dirname(tam), exist_ok=True)
    im.save(tam, optimize=True)
    print("yazıldı:", os.path.relpath(tam, KOK))


if __name__ == "__main__":
    kaydet(ikon(192), "site", "ikon", "ikon-192.png")
    kaydet(ikon(512), "site", "ikon", "ikon-512.png")
    kaydet(ikon(512, guvenli=0.5, yuvarlak=False), "site", "ikon", "ikon-maskable-512.png")
    kaydet(ikon(180, yuvarlak=False).convert("RGB"), "site", "ikon", "apple-touch-icon.png")
    for ad, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        kaydet(ikon(px), "android", "app", "src", "main", "res", f"mipmap-{ad}", "ic_launcher.png")
    # Play Store: 512x512 simge (köşesiz; Play kendisi yuvarlar) + 1024x500 öne çıkan görsel
    kaydet(ikon(512, yuvarlak=False).convert("RGB"), "android", "magaza", "play-ikon-512.png")
    s = 2
    og = gradyan(1024 * s, 500 * s)
    c = ImageDraw.Draw(og)
    takvim(c, 90 * s, 120 * s, 250 * s)
    c.text((400 * s, 205 * s), "Etkinlik Var", font=ImageFont.truetype(YAZI, 92 * s), fill="white", anchor="lm")
    c.text((404 * s, 300 * s), "81 ilde bugün ne yapsam?", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44 * s),
           fill=(255, 240, 230), anchor="lm")
    kaydet(og.resize((1024, 500), Image.LANCZOS), "android", "magaza", "ozellik-gorseli-1024x500.png")
