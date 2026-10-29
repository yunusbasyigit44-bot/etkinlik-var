"""Adıyaman kaynakları (plaka 02). Kaynak haritası: 2026-10-29.

Gelecek tarihli etkinlik veren tek kaynak Adıyaman Üniversitesi'nin etkinlik takvimi.
Adıyaman'da Devlet Tiyatroları sahnesi yok; kaynak yine de listede, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Besni", "Çelikhan", "Gerger", "Gölbaşı", "Kahta", "Samsat", "Sincik", "Tut"]
SALON_ILCE = {"adyü": "Merkez", "adıyaman üniversitesi": "Merkez", "mustafa v. koç": "Merkez", "mediko sosyal": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# Adıyaman Üniversitesi — aylık etkinlik takvimi sayfaları (HTML)
# ------------------------------------------------------------------
def _url_duzelt(url):
    """Dosya adlarında boşluk ve Türkçe harf var; tarayıcıların açabileceği hâle getir."""
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path)), p.query, ""))


def adyu(kaynak, bugun):
    # Bu ay + sonraki 2 ay
    aylar, y, a = [], bugun.year, bugun.month
    for _ in range(3):
        aylar.append((y, a))
        y, a = (y + 1, 1) if a == 12 else (y, a + 1)
    for y, a in aylar:
        sayfa = ortak.indir(f"https://adiyaman.edu.tr/tr/etkinlikler/{y}/{a:02d}")
        bolum = sayfa.split('class="events-wrapper"', 1)
        if len(bolum) < 2:
            continue
        for link, icerik in re.findall(r'<a href="(/tr/etkinlikler/\d{4}/\d{2}/\d{2}/[^"]+)">(.*?)</a>', bolum[1], re.S):
            baslik = re.search(r'class="title">(.*?)</span>', icerik, re.S)
            gun = re.search(r'class="day">(\d{1,2})<', icerik)
            ay = re.search(r'class="month">([^<]+)<', icerik)
            yil = re.search(r'class="year">\s*(\d{4})', icerik)
            if not (baslik and gun and ay and yil):
                continue
            tarih, _ = ortak.tarih_bul(f"{gun[1]} {ay[1]} {yil[1]}", bugun)
            saat = re.search(r'class="time">([0-2]?\d[:.][0-5]\d)<', icerik)
            yer = re.search(r'icon-location"></span></i>([^<]+)<', icerik)
            resim = re.search(r'<img src="([^"]+)"', icerik)
            mekan = ortak.temizle(yer[1]) if yer else "Adıyaman Üniversitesi"
            ad = basliklar(ortak.temizle(baslik[1]))
            yield {
                "baslik": ad,
                "tarih": tarih,
                "saat": saat[1].replace(".", ":") if saat else None,
                "mekan": mekan,
                "ilce": salon_ilce(mekan, "Merkez"),
                "gorsel": _url_duzelt(resim[1]) if resim else None,
                "url": "https://adiyaman.edu.tr" + link,
            }


KAYNAKLAR = [
    {"ad": "Adıyaman Üniversitesi", "tur": "universite", "url": "https://adiyaman.edu.tr/tr/etkinlikler", "cek": adyu},
    {"ad": "Adıyaman İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://adiyaman.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Adıyaman", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/adiyaman", "cek": etkinlik_io,
     "sehir": "Adıyaman", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Adıyaman Belediyesi", "tur": "belediye", "url": "https://adiyaman.bel.tr",
     "not": "etkinlik sayfası var ama güncel değil (son kayıt Eylül 2025)"},
    {"ad": "Adıyaman Valiliği", "tur": "valilik", "url": "https://www.adiyaman.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "8 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": "https://www.kahta.gov.tr/duyurular",
     "not": "duyurular idari (ihale vb.); etkinlik yok"},
    {"ad": "Kahta, Besni, Gölbaşı belediyeleri", "tur": "belediye", "url": None, "not": "sadece olmuş etkinliklerin haberleri"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://adiyaman.gsb.gov.tr", "not": "bot koruması — okunamıyor"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://adiyaman.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Nemrut Gastronomi Buluşmaları, Kommagene Bienali", "tur": "diger", "url": None,
     "not": "yıllık etkinlikler; 2026 programı henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
