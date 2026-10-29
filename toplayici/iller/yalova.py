"""Yalova kaynakları (plaka 77). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Yalova Belediyesi etkinlik sitesi (etkinlik.yalova.bel.tr, HTML), Yalova Üniversitesi etkinlik listesi (HTML).
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Altınova", "Armutlu", "Çiftlikköy", "Çınarcık", "Termal"]
SALON_ILCE = {"yalova üniversitesi": "Merkez", "yalova belediyesi": "Merkez", "termal": "Termal", "armutlu": "Armutlu",
              "çınarcık": "Çınarcık", "altınova": "Altınova", "çiftlikköy": "Çiftlikköy"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

AYLAR = {"oca": 1, "şub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6, "tem": 7, "ağu": 8, "eyl": 9, "eki": 10, "kas": 11, "ara": 12}


# ------------------------------------------------------------------
# 1) Yalova Belediyesi — etkinlik sitesi (kayan slayt kartları)
# ------------------------------------------------------------------
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in sayfa.split("modern-slider-item")[1:]:
        baslik = re.search(r"<h2[^>]*>(.*?)</h2>", blok, re.S)
        link = re.search(r'href="(https://etkinlik\.yalova\.bel\.tr/etkinlikler/[^"]+)"', blok)
        tarih = re.search(r"bi-calendar2-week[^>]*></i>\s*([^<]+)<", blok)
        if not (baslik and link and tarih) or link[1] in goruldu:
            continue
        goruldu.add(link[1])
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        yerler = re.findall(r"bi-pin-map[^>]*></i>\s*<span>([^<]+)</span>", blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = basliklar(ortak.temizle(yerler[0])) if yerler else "Yalova Belediyesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(resim[1], safe=":/%") if resim else None,
            "url": link[1],
        }


# ------------------------------------------------------------------
# 2) Yalova Üniversitesi — etkinlik listesi (geçmiş etkinlikler de var; toplayıcı eler)
# ------------------------------------------------------------------
UNI = "https://www.yalova.edu.tr"


def uni(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("gdlr-core-event-item-thumbnail")[1:]:
        baslik = re.search(r'gdlr-core-event-item-title"[^>]*><a href="([^"]+)">(.*?)</a>', blok, re.S)
        gun = re.search(r'gdlr-core-date">(\d+)</span><span class="gdlr-core-month">(\w+)</span><span class="gdlr-core-year">(\d+)', blok)
        if not (baslik and gun) or gun[2].lower()[:3] not in AYLAR:
            continue
        tarih = dt.date(int(gun[3]), AYLAR[gun[2].lower()[:3]], int(gun[1]))
        saat = re.search(r"gdlr-core-type-time.*?gdlr-core-tail\">\s*(\d{1,2}:\d{2})", blok, re.S)
        tur = re.search(r'fa-list"></i>\s*([^<]+)<', blok)
        yer = re.search(r"gdlr-core-type-location.*?gdlr-core-tail\">\s*([^<]+)<", blok, re.S)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[2])))
        mekan = ortak.temizle(html.unescape(yer[1])) if yer else "Yalova Üniversitesi"
        gorsel = None
        if resim and "etkinlik-img" not in resim[1]:
            gorsel = UNI + urllib.parse.quote(html.unescape(resim[1]), safe="/%")
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": saat[1].zfill(5) if saat and saat[1] != "00:00" else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": gorsel,
            "url": urllib.parse.urljoin(UNI, baslik[1]),
            "ozet": ortak.temizle(tur[1]) if tur else None,
        }


KAYNAKLAR = [
    {"ad": "Yalova Belediyesi", "tur": "belediye", "url": "https://etkinlik.yalova.bel.tr/", "cek": belediye},
    {"ad": "Yalova Üniversitesi", "tur": "universite", "url": UNI + "/tr/Etkinlik", "cek": uni},
    {"ad": "Yalova İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://yalova.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Yalova", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/yalova", "cek": etkinlik_io,
     "sehir": "Yalova", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Yalova Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.yalova.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Çınarcık, Armutlu, Altınova, Çiftlikköy, Termal belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Armutlu, Çınarcık şenlikleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
