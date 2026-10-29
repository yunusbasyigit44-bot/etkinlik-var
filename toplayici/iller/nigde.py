"""Niğde kaynakları (plaka 51). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Niğde Ömer Halisdemir Üniversitesi etkinlik listesi, Niğde Belediyesi Kültür Online (tiyatro/gösteri).
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Altunhisar", "Bor", "Çamardı", "Çiftlik", "Ulukışla"]
SALON_ILCE = {"halisdemir": "Merkez", "kongre ve kültür": "Merkez", "kültür merkezi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

AYLAR = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
         "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12}


# ------------------------------------------------------------------
# 1) Niğde Ömer Halisdemir Üniversitesi — etkinlik listesi (HTML; gün, ay, yıl ayrı alanlarda)
# ------------------------------------------------------------------
OHU = "https://www.ohu.edu.tr"


def ohu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("<article>")[1:]:
        gun = re.search(r'class="day"[^>]*>\s*(\d{1,2})\s*<', blok)
        ay = re.search(r'class="ay"[^>]*>\s*([^<]+?)\s*<', blok)
        yil = re.search(r'fa-calendar-o"></i>(?:&nbsp;)*\s*(\d{4})', blok)
        baslik = re.search(r'<h4><a href="([^"]+)">(.*?)</a></h4>', blok, re.S)
        if not (gun and ay and baslik):
            continue
        a = AYLAR.get(ortak.kucuk(ay[1]))
        if not a:
            continue
        try:
            tarih = dt.date(int(yil[1]) if yil else bugun.year, a, int(gun[1]))
        except ValueError:
            continue
        yer = re.search(r'fa-map-marker"></i>(?:&nbsp;)*\s*([^<]+?)\s*</p>', blok, re.S)
        tur = re.search(r'fa-flag-o"></i>(?:&nbsp;)*\s*([^<]+?)\s*</p>', blok, re.S)
        mekan = ortak.temizle(yer[1]) if yer else "Niğde Ömer Halisdemir Üniversitesi"
        ad = basliklar(ortak.temizle(html.unescape(baslik[2])))
        yield {
            "baslik": ad,
            "tarih": tarih,
            "mekan": mekan or "Niğde Ömer Halisdemir Üniversitesi",
            "ilce": salon_ilce(mekan or "", "Merkez"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "url": urllib.parse.urljoin(OHU + "/", baslik[1]),
        }


# ------------------------------------------------------------------
# 2) Niğde Belediyesi Kültür Online — tiyatro/gösteri listesi (HTML)
# ------------------------------------------------------------------
KO = "https://kulturonline.nigde.bel.tr/"


def kulturonline(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("etkinlik_clip")[1:]:
        baslik = re.search(r'all-time-hit__title"><a href="([^"]+)">(.*?)</a>', blok, re.S)
        t = re.search(r"<span>(\d{1,2})\.(\d{1,2})\.(\d{4})\s*-\s*(\d{1,2}:\d{2})", blok)
        if not (baslik and t):
            continue
        resim = re.search(r'<img src="([^"]+)"', blok)
        fiyat = re.search(r'all-time-hit__text">\s*([^<]+)', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[2])))
        yield {
            "baslik": ad,
            "tarih": dt.date(int(t[3]), int(t[2]), int(t[1])),
            "saat": t[4],
            "mekan": "Niğde Belediyesi Kültür Merkezi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "ucretsiz": bool(fiyat and "ücretsiz" in ortak.kucuk(fiyat[1])),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin(KO, baslik[1]),
        }


KAYNAKLAR = [
    {"ad": "Niğde Ömer Halisdemir Üniversitesi", "tur": "universite", "url": "https://www.ohu.edu.tr/etkinlikler", "cek": ohu},
    {"ad": "Niğde Belediyesi Kültür Online (tiyatro, gösteri)", "tur": "belediye", "url": KO + "etkinlikler.php", "cek": kulturonline},
    {"ad": "Niğde İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://nigde.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Niğde", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/nigde", "cek": etkinlik_io,
     "sehir": "Niğde", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Niğde Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.nigde.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Niğde Belediyesi ana sitesi", "tur": "belediye", "url": "https://www.nigde.bel.tr",
     "not": "etkinlikler Kültür Online sitesinde (okunuyor); ana sitede takvim yok"},
    {"ad": "Bor Belediyesi", "tur": "belediye", "ilce": "Bor", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Niğde Elması, Uluslararası Niğde Kültür ve Sanat Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
