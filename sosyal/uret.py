"""Etkinlik Var — günlük sosyal medya içerikleri (Instagram, X/Twitter, TikTok).

Çalıştırma:  py -X utf8 -I sosyal/uret.py              (bugün için)
             py -X utf8 -I sosyal/uret.py 2026-11-01   (belirli bir gün için)

Çıktı: sosyal/cikti/<tarih>/
  instagram/hikaye_*.png   — 1080x1920, etkinliği olan her il için "Bugün <il>'da" hikâyesi + Türkiye özeti
  instagram/gonderi_*.png  — 1080x1350, günde 3 gönderi (gün özeti, gezilecek yer, yarın/hafta sonu)
  x/*.png + metinler       — X (Twitter) için aynı görseller + 280 karakterlik metinler
  tiktok/tiktok.mp4        — 1080x1920, ~20 sn "Bugün Türkiye'de ne var?" videosu (kendi müziğimizle)
  PAYLASIM_PLANI.md        — hangi dosya, hangi saatte, hangi açıklamayla paylaşılacak

Telif: Kurumların afişleri kullanılmaz; kartlar bizim tasarımımız. Mekân fotoğrafları Wikimedia Commons'tan,
açıklamada fotoğrafçı ve lisans yazılır (CC lisansının şartı).
"""
import datetime as dt
import json
import os
import random
import re
import subprocess
import sys
import textwrap
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageOps

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "toplayici"))
import ortak  # noqa: E402

VERI = os.path.join(KOK, "site", "veri")
SITE = "etkinlikvar.com.tr"          # site yayına girince doğru adres burada güncellenir
HESAP = "@etkinlikvar81"             # Instagram (2026-10-29); X ve TikTok açılınca aynı ad önerilir
TR = dt.timezone(dt.timedelta(hours=3))

# Sitenin renkleri
KREM, KOYU, TURUNCU, SOLUK, BEYAZ = "#f7f5f0", "#1d1b16", "#d9480f", "#6b665c", "#ffffff"
FONT = "C:/Windows/Fonts/"
if not os.path.exists(FONT + "seguibl.ttf"):          # GitHub/Linux'ta çalışırsa yedek yazı tipi
    FONT = "/usr/share/fonts/truetype/dejavu/"
F_SIYAH = lambda b: ImageFont.truetype(FONT + ("seguibl.ttf" if "C:" in FONT else "DejaVuSans-Bold.ttf"), b)  # noqa: E731
F_KALIN = lambda b: ImageFont.truetype(FONT + ("seguisb.ttf" if "C:" in FONT else "DejaVuSans-Bold.ttf"), b)  # noqa: E731
F_NORMAL = lambda b: ImageFont.truetype(FONT + ("segoeui.ttf" if "C:" in FONT else "DejaVuSans.ttf"), b)  # noqa: E731
SIMGE = {"Konser": "🎵", "Tiyatro": "🎭", "Sinema": "🎬", "Sergi": "🖼️", "Çocuk": "🧸", "Spor": "🏅", "Söyleşi": "🎤",
         "Akademik": "🎓", "Atölye": "🛠️", "Festival": "🎪", "Anma / Tören": "🎖️", "Diğer": "📌"}
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


# ------------------------------------------------------------------
# Yardımcılar
# ------------------------------------------------------------------
def de(ad):
    """Türkçe bulunma eki: Adana'da, İzmir'de, Kars'ta."""
    k = ortak.kucuk(ad)
    unlu = [c for c in k if c in "aeıioöuü"][-1]
    return ad + "'" + ("t" if k[-1] in "fstkçşhp" else "d") + ("a" if unlu in "aıou" else "e")


def tarih_yazi(g):
    return f"{g.day} {AYLAR[g.month - 1]} {GUNLER[g.weekday()]}"


def emoji(img, karakter, merkez, boyut):
    """Renkli emoji çizer (Segoe UI Emoji sadece 109 punto çizebildiği için büyütülür)."""
    try:
        f = ImageFont.truetype(FONT + "seguiemj.ttf", 109)
    except OSError:
        return
    katman = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    ImageDraw.Draw(katman).text((160, 160), karakter, font=f, embedded_color=True, anchor="mm")
    kutu = katman.getbbox()
    if not kutu:
        return
    katman = katman.crop(kutu).resize((boyut, boyut), Image.LANCZOS)
    img.paste(katman, (merkez[0] - boyut // 2, merkez[1] - boyut // 2), katman)


def satirla(d, metin, font, genislik, en_fazla=2):
    """Metni verilen genişliğe sığacak satırlara böler; sığmazsa son satırı '…' ile keser."""
    kelimeler, satirlar, satir = metin.split(), [], ""
    for k in kelimeler:
        dene = (satir + " " + k).strip()
        if d.textlength(dene, font=font) <= genislik:
            satir = dene
        else:
            if satir:
                satirlar.append(satir)
            satir = k
    if satir:
        satirlar.append(satir)
    if len(satirlar) > en_fazla:
        satirlar = satirlar[:en_fazla]
        while d.textlength(satirlar[-1] + "…", font=font) > genislik and " " in satirlar[-1]:
            satirlar[-1] = satirlar[-1].rsplit(" ", 1)[0]
        satirlar[-1] += "…"
    return satirlar


def ust_bant(img, alt_yazi):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width, 150], fill=KOYU)
    d.text((60, 75), "Etkinlik", font=F_SIYAH(58), fill=BEYAZ, anchor="lm")
    d.text((60 + d.textlength("Etkinlik ", font=F_SIYAH(58)), 75), "Var", font=F_SIYAH(58), fill="#ff8a4c", anchor="lm")
    d.text((img.width - 60, 75), alt_yazi, font=F_KALIN(34), fill="#d8d2c4", anchor="rm")


def alt_bant(img, metin):
    d = ImageDraw.Draw(img)
    d.rectangle([0, img.height - 120, img.width, img.height], fill=TURUNCU)
    d.text((img.width // 2, img.height - 60), metin, font=F_KALIN(38), fill=BEYAZ, anchor="mm")


def etkinlik_karti(img, e, x, y, gen, yuk):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + gen, y + yuk], radius=28, fill=BEYAZ, outline="#e4dfd4", width=2)
    d.ellipse([x + 24, y + yuk // 2 - 50, x + 124, y + yuk // 2 + 50], fill="#fff0e6")
    emoji(img, SIMGE.get(e["kategori"], "📌"), (x + 74, y + yuk // 2), 58)
    metin_x, metin_gen = x + 150, gen - 180 - (170 if e.get("ucretsiz") is True else 0)
    satirlar = satirla(d, e["baslik"], F_KALIN(40), metin_gen, 2)
    bilgi = " · ".join(p for p in (e.get("saat"), (e.get("mekan") or e.get("ilce") or "")[:40]) if p)
    toplam = len(satirlar) * 50 + 44
    ty = y + (yuk - toplam) // 2
    for s in satirlar:
        d.text((metin_x, ty), s, font=F_KALIN(40), fill=KOYU)
        ty += 50
    d.text((metin_x, ty + 4), bilgi, font=F_NORMAL(32), fill=SOLUK)
    if e.get("ucretsiz") is True:
        d.rounded_rectangle([x + gen - 170, y + 18, x + gen - 20, y + 62], radius=12, fill="#ebfbee")
        d.text((x + gen - 95, y + 40), "Ücretsiz", font=F_KALIN(26), fill="#2b8a3e", anchor="mm")


# ------------------------------------------------------------------
# Veri
# ------------------------------------------------------------------
def il_kodu(ad):
    return re.sub(r"[^a-z0-9]", "", ortak.kucuk(ad).translate(str.maketrans("çğıöşü", "cgiosu")))


def verileri_oku():
    hazir = json.load(open(os.path.join(VERI, "hazir.json"), encoding="utf-8"))
    iller = {}
    for ad in hazir:
        k = il_kodu(ad)
        v = json.load(open(os.path.join(VERI, k + ".json"), encoding="utf-8"))
        myol = os.path.join(VERI, k + "_mekanlar.json")
        v["mekanlar"] = json.load(open(myol, encoding="utf-8")) if os.path.exists(myol) else []
        iller[ad] = v
    return iller


def o_gun(etkinlikler, gun):
    """O günkü etkinlikler; aynı etkinliğin birkaç seansı tek kayıtta birleşir ("11:00, 14:00")."""
    g = gun.isoformat()
    tek = {}
    for e in sorted([e for e in etkinlikler if e["tarih"] <= g <= (e.get("bitis") or e["tarih"])],
                    key=lambda e: (e["tarih"] != g, e.get("saat") or "99")):
        anahtar = (ortak.kucuk(e["baslik"]), e.get("mekan"))
        if anahtar in tek:
            if e.get("saat") and e["saat"] not in (tek[anahtar].get("saat") or ""):
                tek[anahtar]["saat"] = ", ".join(filter(None, (tek[anahtar].get("saat"), e["saat"])))
        else:
            tek[anahtar] = dict(e)
    return list(tek.values())


def secilmis(liste, n):
    """Önce tek günlük ve saatli etkinlikler, ardından uzun süreliler; akademik/tören en sona."""
    oncelik = lambda e: (e["kategori"] in ("Akademik", "Anma / Tören", "Diğer"), bool(e.get("bitis")), e.get("saat") or "99")  # noqa: E731
    return sorted(liste, key=oncelik)[:n]


# ------------------------------------------------------------------
# Görseller
# ------------------------------------------------------------------
def mekan_kutusu(img, mekan, y, yuk):
    """Hikâyenin boş kalan altına: 'Etkinlik dışında: <yer>' fotoğraflı kutu."""
    d = ImageDraw.Draw(img)
    d.text((60, y), "Bir de buraya uğra", font=F_KALIN(40), fill=TURUNCU)
    y += 64
    yuk -= 64
    foto = foto_indir(mekan.get("gorsel"))
    kutu = Image.new("RGB", (980, yuk), "#fff0e6")
    if foto:
        kutu.paste(ImageOps.fit(foto, (980, yuk), Image.LANCZOS), (0, 0))
    else:
        emoji(kutu, mekan.get("simge", "📍"), (490, yuk // 2), 200)
    maske = Image.new("L", (980, yuk), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, 979, yuk - 1], radius=28, fill=255)
    img.paste(kutu, (50, y), maske)
    d.rounded_rectangle([70, y + yuk - 110, 70 + min(940, d.textlength(mekan["ad"], font=F_SIYAH(46)) + 50), y + yuk - 24],
                        radius=20, fill=KOYU)
    d.text((95, y + yuk - 67), mekan["ad"][:34], font=F_SIYAH(46), fill=BEYAZ, anchor="lm")


def hikaye_il(il, liste, gun, yol, mekan=None):
    img = Image.new("RGB", (1080, 1920), KREM)
    ust_bant(img, tarih_yazi(gun))
    d = ImageDraw.Draw(img)
    d.text((60, 230), "Bugün", font=F_SIYAH(70), fill=TURUNCU)
    satir = satirla(d, de(il), F_SIYAH(104), 960, 2)
    y = 320
    for s in satir:
        d.text((60, y), s, font=F_SIYAH(104), fill=KOYU)
        y += 118
    d.text((60, y + 10), f"{len(liste)} etkinlik var", font=F_KALIN(44), fill=SOLUK)
    y += 100
    gosterilen = secilmis(liste, 5)
    for e in gosterilen:
        etkinlik_karti(img, e, 50, y, 980, 200)
        y += 222
    if len(liste) > len(gosterilen):
        d.text((540, y + 30), f"+{len(liste) - len(gosterilen)} etkinlik daha sitede", font=F_KALIN(40), fill=TURUNCU, anchor="mm")
        y += 80
    bos = 1800 - 30 - y
    if mekan and bos >= 420:
        mekan_kutusu(img, mekan, y + 10, min(bos - 20, 640))
    alt_bant(img, f"Hepsi: {SITE}  ·  Gidiyorum de!")
    img.save(yol)


def hikaye_ozet(iller_gun, gun, yol):
    img = Image.new("RGB", (1080, 1920), KOYU)
    d = ImageDraw.Draw(img)
    d.text((540, 200), tarih_yazi(gun), font=F_KALIN(44), fill="#d8d2c4", anchor="mm")
    d.text((540, 330), "Bugün", font=F_SIYAH(90), fill="#ff8a4c", anchor="mm")
    d.text((540, 450), "Türkiye'de", font=F_SIYAH(110), fill=BEYAZ, anchor="mm")
    toplam = sum(len(l) for l in iller_gun.values())
    d.text((540, 600), f"{len(iller_gun)} ilde {toplam} etkinlik", font=F_SIYAH(72), fill=BEYAZ, anchor="mm")
    y = 740
    for il, liste in sorted(iller_gun.items(), key=lambda x: -len(x[1]))[:8]:
        d.rounded_rectangle([110, y, 970, y + 110], radius=26, fill="#2b2822")
        d.text((160, y + 55), il, font=F_KALIN(48), fill=BEYAZ, anchor="lm")
        d.text((920, y + 55), f"{len(liste)} etkinlik", font=F_KALIN(40), fill="#ff8a4c", anchor="rm")
        y += 128
    d.text((540, 1800), f"Şehrini seç: {SITE}", font=F_KALIN(42), fill=BEYAZ, anchor="mm")
    img.save(yol)


def gonderi_ozet(iller_gun, gun, yol):
    img = Image.new("RGB", (1080, 1350), KREM)
    ust_bant(img, tarih_yazi(gun))
    d = ImageDraw.Draw(img)
    toplam = sum(len(l) for l in iller_gun.values())
    d.text((60, 220), "Bugün ne yapsam?", font=F_SIYAH(80), fill=KOYU)
    d.text((60, 330), f"{len(iller_gun)} ilde {toplam} etkinlik seni bekliyor", font=F_KALIN(44), fill=TURUNCU)
    hepsi = [(il, e) for il, l in iller_gun.items() for e in l]
    y = 430
    one_cikan = sorted(hepsi, key=lambda x: (x[1]["kategori"] in ("Akademik", "Anma / Tören", "Diğer"), bool(x[1].get("bitis"))))[:4]
    for il, e in one_cikan:
        e2 = dict(e, mekan=f"{il} · {e.get('mekan') or e.get('ilce') or ''}")
        etkinlik_karti(img, e2, 50, y, 980, 180)
        y += 198
    alt_bant(img, f"Tüm liste: {SITE}")
    img.save(yol)


def _commons_bilgi(gorsel_url):
    """Fotoğrafçı ve lisans (CC şartı). Bulunamazsa genel atıf."""
    dosya = urllib.parse.unquote(gorsel_url.split("/")[-1])
    dosya = re.sub(r"^\d+px-", "", dosya)
    url = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata&format=json&titles="
           + urllib.parse.quote("File:" + dosya))
    try:
        istek = urllib.request.Request(url, headers={"User-Agent": "EtkinlikVar/1.0"})
        sayfa = next(iter(json.load(urllib.request.urlopen(istek, timeout=20))["query"]["pages"].values()))
        m = sayfa["imageinfo"][0]["extmetadata"]
        sanatci = ortak.temizle(m.get("Artist", {}).get("value", ""))[:60]
        lisans = m.get("LicenseShortName", {}).get("value", "")
        return f"Fotoğraf: {sanatci or 'Wikimedia Commons'} · {lisans} · Wikimedia Commons"
    except Exception:
        return "Fotoğraf: Wikimedia Commons"


def foto_indir(gorsel):
    """Wikimedia küçük resmini büyük boyda indirir (sadece standart genişlikler veriliyor: 1280, 960)."""
    if not gorsel:
        return None
    for w in ("1280px", "960px", None):
        u = re.sub(r"/\d+px-", f"/{w}-", gorsel) if w else gorsel
        try:
            istek = urllib.request.Request(u, headers={"User-Agent": "EtkinlikVar/1.0"})
            return Image.open(BytesIO(urllib.request.urlopen(istek, timeout=30).read())).convert("RGB")
        except Exception:
            continue
    return None


def gonderi_mekan(il, mekan, yol):
    img = Image.new("RGB", (1080, 1350), KREM)
    foto = foto_indir(mekan.get("gorsel"))
    if foto:
        img.paste(ImageOps.fit(foto, (1080, 820), Image.LANCZOS), (0, 0))
    else:
        ImageDraw.Draw(img).rectangle([0, 0, 1080, 820], fill="#fff0e6")
        emoji(img, mekan.get("simge", "📍"), (540, 410), 300)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 40, 40 + d.textlength("Bugün buraya gidebilirsin", font=F_KALIN(34)) + 50, 110],
                        radius=20, fill=KOYU)
    d.text((65, 75), "Bugün buraya gidebilirsin", font=F_KALIN(34), fill=BEYAZ, anchor="lm")
    y = 860
    for s in satirla(d, mekan["ad"], F_SIYAH(70), 980, 2):
        d.text((50, y), s, font=F_SIYAH(70), fill=KOYU)
        y += 84
    d.text((50, y + 6), f"📍 {mekan['ilce']}, {il}".replace("📍 ", ""), font=F_KALIN(40), fill=TURUNCU)
    y += 70
    for s in satirla(d, mekan["aciklama"], F_NORMAL(36), 980, 3):
        d.text((50, y), s, font=F_NORMAL(36), fill=SOLUK)
        y += 48
    alt_bant(img, f"{il} rehberi: {SITE}")
    img.save(yol)
    return _commons_bilgi(mekan["gorsel"]) if foto else ""


def gonderi_yakinda(baslik, alt, liste, yol):
    """Yarın / hafta sonu gönderisi: il adıyla birlikte öne çıkan etkinlikler."""
    img = Image.new("RGB", (1080, 1350), KREM)
    ust_bant(img, alt)
    d = ImageDraw.Draw(img)
    d.text((60, 220), baslik, font=F_SIYAH(84), fill=KOYU)
    y = 360
    for il, e in liste[:5]:
        etkinlik_karti(img, dict(e, mekan=f"{il} · {e.get('mekan') or ''}"), 50, y, 980, 170)
        y += 186
    alt_bant(img, f"Şehrindekileri gör: {SITE}")
    img.save(yol)


# ------------------------------------------------------------------
# TikTok videosu
# ------------------------------------------------------------------
def tiktok(kareler, muzik, yol):
    """Kareleri 2,5 sn'lik slaytlar olarak birleştirir, müzik ekler (kısık sesle, sonunda kısılır)."""
    ffmpeg = "ffmpeg"
    for aday in (os.environ.get("FFMPEG", ""),
                 os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")):
        if aday and os.path.isdir(aday):
            for kok, _, dosyalar in os.walk(aday):
                if "ffmpeg.exe" in dosyalar:
                    ffmpeg = os.path.join(kok, "ffmpeg.exe")
                    break
    sure = 2.5
    girdiler, filtre = [], []
    for i, k in enumerate(kareler):
        girdiler += ["-loop", "1", "-t", str(sure), "-i", k]
        filtre.append(f"[{i}:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,"
                      f"zoompan=z='min(zoom+0.0006,1.04)':d={int(sure*30)}:s=1080x1920:fps=30[v{i}]")
    birlesik = "".join(f"[v{i}]" for i in range(len(kareler))) + f"concat=n={len(kareler)}:v=1:a=0[v]"
    toplam = sure * len(kareler)
    komut = [ffmpeg, "-y", *girdiler, "-i", muzik, "-filter_complex",
             ";".join(filtre + [birlesik, f"[{len(kareler)}:a]volume=0.5,afade=t=out:st={toplam-1.5}:d=1.5[a]"]),
             "-map", "[v]", "-map", "[a]", "-t", str(toplam), "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", yol]
    subprocess.run(komut, check=True, capture_output=True)


def slayt(baslik, ust, e=None, il=None, yol=None):
    img = Image.new("RGB", (1080, 1920), KOYU if e is None else KREM)
    d = ImageDraw.Draw(img)
    if e is None:
        d.text((540, 760), ust, font=F_KALIN(52), fill="#ff8a4c", anchor="mm")
        y = 860
        for s in satirla(d, baslik, F_SIYAH(110), 960, 3):
            d.text((540, y), s, font=F_SIYAH(110), fill=BEYAZ, anchor="mm")
            y += 130
        d.text((540, 1750), SITE, font=F_KALIN(44), fill=BEYAZ, anchor="mm")
    else:
        ust_bant(img, il)
        emoji(img, SIMGE.get(e["kategori"], "📌"), (540, 560), 260)
        y = 800
        for s in satirla(d, e["baslik"], F_SIYAH(76), 960, 3):
            d.text((540, y), s, font=F_SIYAH(76), fill=KOYU, anchor="mm")
            y += 92
        bilgi = " · ".join(p for p in (e.get("saat"), e.get("mekan")) if p)
        for s in satirla(d, bilgi, F_KALIN(44), 940, 2):
            d.text((540, y + 40), s, font=F_KALIN(44), fill=TURUNCU, anchor="mm")
            y += 56
        alt_bant(img, f"{il} · {SITE}")
    img.save(yol)


# ------------------------------------------------------------------
# Ana akış
# ------------------------------------------------------------------
def uret(gun):
    iller = verileri_oku()
    hedef = os.path.join(KOK, "sosyal", "cikti", gun.isoformat())
    for alt in ("instagram", "x", "tiktok"):
        os.makedirs(os.path.join(hedef, alt), exist_ok=True)
    rnd = random.Random(gun.toordinal())          # aynı gün tekrar çalışırsa aynı seçim

    bugun = {il: o_gun(v["etkinlikler"], gun) for il, v in iller.items()}
    bugun = {il: l for il, l in bugun.items() if l}
    yarin_g = gun + dt.timedelta(days=1)
    yarin = [(il, e) for il, v in iller.items() for e in secilmis(o_gun(v["etkinlikler"], yarin_g), 2)]
    cmt = gun + dt.timedelta(days=(5 - gun.weekday()) % 7)
    hafta_sonu = []
    for il, v in iller.items():
        gorulen, liste = set(), []
        for e in o_gun(v["etkinlikler"], cmt) + o_gun(v["etkinlikler"], cmt + dt.timedelta(days=1)):
            if ortak.kucuk(e["baslik"]) not in gorulen:
                gorulen.add(ortak.kucuk(e["baslik"]))
                liste.append(e)
        hafta_sonu += [(il, e) for e in secilmis(liste, 2)]
    plan = [f"# Paylaşım planı — {tarih_yazi(gun)}\n", f"Site: {SITE} · Hesap: {HESAP}\n"]

    # --- Instagram hikâyeleri ---
    plan.append("\n## Instagram hikâyeleri (sabah 08:30'dan itibaren, sırayla)\n")
    if bugun:
        hikaye_ozet(bugun, gun, os.path.join(hedef, "instagram", "hikaye_00_turkiye.png"))
        plan.append("- `instagram/hikaye_00_turkiye.png` — Türkiye özeti (bağlantı çıkartması: site)\n")
    for i, (il, liste) in enumerate(sorted(bugun.items(), key=lambda x: ortak.ILLER.index(x[0])), 1):
        dosya = f"hikaye_{i:02d}_{il_kodu(il)}.png"
        fotolu = [m for m in iller[il]["mekanlar"] if m.get("gorsel")] or iller[il]["mekanlar"]
        hikaye_il(il, liste, gun, os.path.join(hedef, "instagram", dosya), rnd.choice(fotolu) if fotolu else None)
        plan.append(f"- `instagram/{dosya}` — {il} ({len(liste)} etkinlik) · konum çıkartması: {il} · "
                    f"bağlantı: {SITE}/?il={il_kodu(il)} · öne çıkan: “{il}” klasörü\n")

    # --- Gönderiler ---
    gonderiler = []
    if bugun:
        gonderi_ozet(bugun, gun, os.path.join(hedef, "instagram", "gonderi_1_gunun_ozeti.png"))
        toplam = sum(len(l) for l in bugun.values())
        gonderiler.append(("09:00", "gonderi_1_gunun_ozeti.png",
                           f"Bugün ne yapsam? 🤔 {len(bugun)} ilde {toplam} etkinlik var! Konser, tiyatro, sergi, söyleşi… "
                           f"Şehrini seç, “Gidiyorum” de 🙋 Tüm liste profildeki bağlantıda.",
                           "#etkinlik #bugünneyapsam #" + " #".join(il_kodu(i) for i in list(bugun)[:5])))
    adaylar = [(il, m) for il, v in iller.items() for m in v["mekanlar"] if m.get("gorsel")]
    if adaylar:
        il, m = rnd.choice(adaylar)
        atif = gonderi_mekan(il, m, os.path.join(hedef, "instagram", "gonderi_2_gezilecek_yer.png"))
        gonderiler.append(("13:00", "gonderi_2_gezilecek_yer.png",
                           f"📍 {m['ad']}, {il}\n{m['aciklama']}\nEtkinlik yoksa da gidilecek yer çok! {il} rehberi profilde.\n{atif}",
                           f"#{il_kodu(il)} #gezilecekyerler #{re.sub(r'[^a-zçğıöşü]', '', ortak.kucuk(m['ad']))} #türkiye"))
    if gun.weekday() in (3, 4) and hafta_sonu:          # perşembe-cuma: hafta sonu gönderisi
        paz = cmt + dt.timedelta(days=1)
        ust = (f"{cmt.day}-{paz.day} {AYLAR[cmt.month - 1]}" if cmt.month == paz.month
               else f"{cmt.day} {AYLAR[cmt.month - 1]} - {paz.day} {AYLAR[paz.month - 1]}")
        gonderi_yakinda("Hafta sonu ne var?", ust,
                        sorted(hafta_sonu, key=lambda x: x[1]["kategori"] in ("Akademik", "Diğer")),
                        os.path.join(hedef, "instagram", "gonderi_3_hafta_sonu.png"))
        gonderiler.append(("19:00", "gonderi_3_hafta_sonu.png",
                           "Hafta sonu planın hazır mı? 🎉 Şehrindeki konser, tiyatro ve çocuk etkinlikleri sitede. "
                           "Kiminle gideceğini etiketle 👇", "#haftasonu #etkinlik #ne yapsam".replace(" yapsam", "yapsam")))
    elif yarin:
        gonderi_yakinda("Yarın ne var?", tarih_yazi(yarin_g),
                        sorted(yarin, key=lambda x: x[1]["kategori"] in ("Akademik", "Diğer")),
                        os.path.join(hedef, "instagram", "gonderi_3_yarin.png"))
        gonderiler.append(("19:00", "gonderi_3_yarin.png",
                           "Yarın için plan yap! 📅 Öne çıkan etkinlikler burada, tamamı profildeki bağlantıda. "
                           "Takvimine eklemeyi unutma.", "#etkinlik #yarın #bugünneyapsam"))
    plan.append("\n## Instagram gönderileri\n")
    for saat, dosya, metin, etiket in gonderiler:
        plan.append(f"\n**{saat} — `instagram/{dosya}`**\n\n```\n{metin}\n\n{etiket}\n```\n")

    # --- X (Twitter): aynı görseller + kısa metin ---
    plan.append("\n## X (Twitter) — aynı saatlerde, görseller `x/` klasöründe\n")
    for saat, dosya, metin, etiket in gonderiler:
        Image.open(os.path.join(hedef, "instagram", dosya)).save(os.path.join(hedef, "x", dosya))
        # Fotoğraf atfı (CC lisans şartı) hiçbir zaman kısaltılmaz; kısaltma sadece ana metne uygulanır
        satirlar = metin.split("\n")
        atif = next((x for x in satirlar if x.startswith("Fotoğraf:")), "")
        ana = " ".join(x for x in satirlar if x != atif).replace("profildeki bağlantıda", SITE).replace("profilde", SITE)
        yer = 270 - len(atif) - len(etiket.split()[0]) - 3
        kisa = textwrap.shorten(ana, yer, placeholder="…") + (f"\n{atif}" if atif else "")
        plan.append(f"\n**{saat} — `x/{dosya}`**\n\n```\n{kisa} {etiket.split()[0]}\n```\n")

    # --- TikTok ---
    plan.append("\n## TikTok — 18:00\n")
    if bugun:
        kareler, k = [], os.path.join(hedef, "tiktok")
        slayt("Bugün Türkiye'de ne var?", tarih_yazi(gun), yol=os.path.join(k, "kare_00.png"))
        kareler.append(os.path.join(k, "kare_00.png"))
        secim = sorted(((il, e) for il, l in bugun.items() for e in secilmis(l, 2)),
                       key=lambda x: (x[1]["kategori"] in ("Akademik", "Anma / Tören", "Diğer"), rnd.random()))[:6]
        for i, (il, e) in enumerate(secim, 1):
            slayt("", "", e, il, os.path.join(k, f"kare_{i:02d}.png"))
            kareler.append(os.path.join(k, f"kare_{i:02d}.png"))
        slayt("Şehrini seç, Gidiyorum de!", "Hepsi sitede", yol=os.path.join(k, "kare_99.png"))
        kareler.append(os.path.join(k, "kare_99.png"))
        muzikler = sorted(f for f in os.listdir(os.path.join(KOK, "sosyal", "muzik")) if f.endswith(".wav"))
        try:
            tiktok(kareler, os.path.join(KOK, "sosyal", "muzik", rnd.choice(muzikler)), os.path.join(k, "tiktok.mp4"))
            plan.append(f"\n`tiktok/tiktok.mp4` (~{len(kareler) * 2.5:.0f} sn)\n\n```\nBugün Türkiye'de ne var? 🎭🎵 "
                        f"{len(bugun)} ilde {sum(len(l) for l in bugun.values())} etkinlik! Şehrini yorumlara yaz, "
                        f"sana özel listeyi söyleyelim 👇\n\n#etkinlik #bugünneyapsam #keşfet #türkiye\n```\n")
        except Exception as h:
            plan.append(f"\nVideo üretilemedi: {h}\n")

    plan.append("\n---\nNot: Kurum afişleri kullanılmadı. Mekân fotoğraflarında atıf satırı açıklamada kalmalı (CC lisansı).\n")
    with open(os.path.join(hedef, "PAYLASIM_PLANI.md"), "w", encoding="utf-8") as f:
        f.writelines(plan)
    print(f"{gun}: {len(bugun)} il hikâyesi, {len(gonderiler)} gönderi -> {hedef}")
    return hedef


if __name__ == "__main__":
    gun = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(TR).date()
    uret(gun)
