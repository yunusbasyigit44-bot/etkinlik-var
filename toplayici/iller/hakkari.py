"""Hakkari kaynakları (plaka 30). Kaynak haritası: 2026-10-29.

Hakkari Üniversitesi etkinlik listesi (HTML) tek verimli kaynak. Belediye sitesinin sertifikası bozuk
olduğu için okunamıyor. Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Çukurca", "Derecik", "Şemdinli", "Yüksekova"]
SALON_ILCE = {"yüksekova": "Yüksekova", "şemdinli": "Şemdinli", "çukurca": "Çukurca", "derecik": "Derecik"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Hakkari Üniversitesi — etkinlik arşivi sayfası (HTML)
# ------------------------------------------------------------------
HU = "https://www.hakkari.edu.tr"


def universite(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="event-archive-card"')[1:]:
        baslik = re.search(r'<h3 class="event-archive-card__title"[^>]*>(.*?)</h3>', blok, re.S)
        zaman = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})', blok)
        link = re.search(r'<a class="event-archive-card__detail"\s+href="([^"]+)"', blok)
        if not (baslik and zaman):
            continue
        yer = re.search(r'event-archive-card__place">.*?</i>([^<]*)<', blok, re.S)
        resim = re.search(r'<img src="([^"]+)"', blok)
        tur = re.search(r'categoryId=\d+">([^<]+)<', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = ortak.temizle(yer[1]) if yer and yer[1].strip() else "Hakkari Üniversitesi"
        if ortak.baska_il_mi(mekan, "Hakkari") or "yüzüncü yıl" in ortak.kucuk(mekan):   # Van YYÜ
            continue
        yield {
            "baslik": ad,
            "tarih": dt.date.fromisoformat(zaman[1]),
            "saat": zaman[2] if zaman[2] != "00:00" else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": resim[1] if resim else None,
            "url": HU + urllib.parse.quote(html.unescape(link[1]), safe="/%") if link else kaynak["url"],
            "ozet": tur[1] if tur else None,
        }


KAYNAKLAR = [
    {"ad": "Hakkari Üniversitesi", "tur": "universite", "url": HU + "/etkinlikler", "cek": universite},
    {"ad": "Hakkari İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://hakkari.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/hakkari", "cek": etkinlik_io,
     "sehir": "Hakkari", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Hakkari Belediyesi", "tur": "belediye", "url": "https://www.hakkari.bel.tr", "not": "site sertifikası geçersiz — okunamıyor"},
    {"ad": "Hakkari Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.hakkari.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Yüksekova, Şemdinli, Çukurca belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "not": "Hakkari'de sahne yok"},
    {"ad": "Yıllık festivaller (Cilo Dağcılık, Yüksekova Kültür-Sanat…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
