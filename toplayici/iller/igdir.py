"""Iğdır kaynakları (plaka 76). Kaynak haritası: 2026-10-29.

Okunan kaynak: Iğdır Üniversitesi etkinlik listesi (Odoo etkinlik sayfası, tarih ISO biçiminde).
Belediye ve valilik sitelerinde etkinlik takvimi yok. Devlet Tiyatroları sahnesi yok.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Aralık", "Karakoyunlu", "Tuzluca"]
SALON_ILCE = {"iğdır üniversitesi": "Merkez", "tuzluca": "Tuzluca", "karakoyunlu": "Karakoyunlu", "aralık": "Aralık"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

UNI = "https://www.igdir.edu.tr"


# ------------------------------------------------------------------
# 1) Iğdır Üniversitesi — etkinlik listesi (Odoo; tarih "2026-10-27 08:00:00" UTC)
# ------------------------------------------------------------------
def igdir_uni(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<a class="text-decoration-none" href="')[1:]:
        ad = re.search(r'itemprop="name">(.*?)</span>', blok, re.S)
        zaman = re.search(r'datetime="(\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}"', blok)
        link = re.match(r'([^"]+)"', blok)
        if not (ad and zaman):
            continue
        bas = dt.datetime.fromisoformat(zaman[1]) + dt.timedelta(hours=3)      # UTC -> Türkiye saati
        resim = re.search(r"url\((/web/image/[^)]+)\)", blok)
        baslik = basliklar(ortak.temizle(html.unescape(ad[1])))
        yield {
            "baslik": baslik,
            "tarih": bas.date(),
            "saat": None if bas.strftime("%H:%M") == "00:00" else bas.strftime("%H:%M"),
            "mekan": "Iğdır Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(baslik),
            "gorsel": UNI + resim[1] if resim else None,
            "url": urllib.parse.urljoin(UNI, link[1]) if link else UNI + "/events",
        }


KAYNAKLAR = [
    {"ad": "Iğdır Üniversitesi", "tur": "universite", "url": UNI + "/events/", "cek": igdir_uni},
    {"ad": "Iğdır İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://igdir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Iğdır", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/igdir", "cek": etkinlik_io,
     "sehir": "Iğdır", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Iğdır Belediyesi", "tur": "belediye", "url": "https://www.igdir.bel.tr/duyurular", "not": "duyurular idari; etkinlik takvimi yok"},
    {"ad": "Iğdır Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.igdir.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Aralık, Karakoyunlu, Tuzluca belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Kayısı, Ağrı Dağı Kültür Sanat vb.)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
