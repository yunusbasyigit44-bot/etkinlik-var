"""Her gün açık yerlere Vikipedi'den fotoğraf ve bilgi bağlantısı ekler.

Çalıştırma: py -X utf8 -I toplayici/mekan_gorsel.py adana
Fotoğraflar Wikimedia Commons'tan gelir (serbest lisanslı); yeni mekan eklenince bir kez çalıştırmak yeter.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

KLASOR = os.path.dirname(os.path.abspath(__file__))
BASLIK = {"User-Agent": "EtkinlikVar/1.0 (etkinlik derleyici; iletisim: github.com/yunusbasyigit44-bot)"}


def ozet(madde):
    url = "https://tr.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(madde.replace(" ", "_"))
    for deneme in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=BASLIK), timeout=20) as y:
                return json.load(y)
        except urllib.error.HTTPError as h:
            if h.code == 404:
                return None
            if h.code == 429:              # çok hızlı istek: bekle, tekrar dene
                time.sleep(10 * (deneme + 1))
                continue
            raise
    print("   Vikipedi 429 (çok hızlı istek) — sonra tekrar dene:", madde)
    return "429"


# Harita, uydu görüntüsü, şema: "yer fotoğrafı" değildir
FOTO_DEGIL = re.compile(r"(map|harita|location|locator|landsat|satellite|uydu|plan\b|\.svg|\.tif|flag|bayrak|logo|arma|"
                        r"illu_|diagram|şema|nasa|modis|sentinel|topograph|relief|district|ilçe|ilce|tabela|sign\b)", re.I)


def main(il):
    sys.path.insert(0, KLASOR)
    import ortak
    il_adi = next((a for a in ortak.ILLER if re.sub(r"[^a-z0-9]", "", ortak.kucuk(a).translate(
        str.maketrans("çğıöşü", "cgiosu"))) == il), il)
    yol = os.path.join(KLASOR, "..", "site", "veri", il + "_mekanlar.json")
    mekanlar = json.load(open(yol, encoding="utf-8"))
    for m in mekanlar:
        madde = m.get("vikipedi")
        if not madde or m.get("gorsel"):
            continue
        s = ozet(madde)
        time.sleep(2)
        if s == "429":
            continue                       # madde adı silinmez; program tekrar çalıştırılınca denenir
        if not s or s.get("type") == "disambiguation":
            print("bulunamadı" if not s else "anlam ayrımı sayfası (daha belirli ad yaz, ör. 'X (İl)'):", madde)
            continue
        m["bilgi_url"] = s["content_urls"]["desktop"]["page"]
        # Vikipedi başka maddeye yönlendirdiyse (ör. "Frig Vadisi" -> "Frigya") fotoğraf başka yeri gösterebilir.
        # Hedef madde ilin ya da ilçenin adını geçiriyorsa aynı yerdir (ör. "Laodikeia" -> "Laodikya") ve kabul edilir.
        if s.get("title", "").replace("_", " ") != madde:
            ozet_metni = ortak.kucuk(s.get("extract", "") + " " + s.get("description", ""))
            # Kısa açıklamada başka bir il geçiyorsa (ör. "Paşabağı" -> "Karaman'da bir köy") başka yerdir
            aciklama = ortak.kucuk(s.get("description", ""))
            baska = any(ortak.kucuk(i) in aciklama for i in ortak.ILLER if i != il_adi)
            if baska or (ortak.kucuk(il_adi) not in ozet_metni and ortak.kucuk(m.get("ilce", "-")) not in ozet_metni):
                print("yönlendirme, fotoğraf alınmadı:", madde, "->", s.get("title"))
                m["vikipedi"] = None
                continue
            print("yönlendirme kabul (aynı il):", madde, "->", s.get("title"))
            m["vikipedi"] = s["title"].replace("_", " ")
        if s.get("thumbnail"):
            dosya = urllib.parse.unquote(s["thumbnail"]["source"].split("/")[-1])
            if FOTO_DEGIL.search(dosya):
                print("harita/şema, fotoğraf alınmadı:", m["ad"], "->", dosya)
                continue
            m["gorsel"] = re.sub(r"\?.*$", "", s["thumbnail"]["source"])
        print("tamam:", m["ad"], "| görsel" if m.get("gorsel") else "| görselsiz")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(mekanlar, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "adana")
