"""Tunceli kaynakları (plaka 62). Kaynak haritası: 2026-10-29.

Okunan kaynak: Munzur Üniversitesi etkinlik listesi (kartlarda tarih var; şu an listedeki en yeni kayıt geçmişte,
yaklaşan etkinlik eklenince kendiliğinden gelir). Tunceli Belediyesi sertifika hatası veriyor (okunamıyor).
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Çemişgezek", "Hozat", "Mazgirt", "Nazımiye", "Ovacık", "Pertek", "Pülümür"]
SALON_ILCE = {"munzur": "Merkez", "tunceli": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

MZ = "https://www.munzur.edu.tr"


# ------------------------------------------------------------------
# 1) Munzur Üniversitesi — etkinlik listesi (kart: bağlantı, görsel, tarih, başlık)
# ------------------------------------------------------------------
def munzur(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in sayfa.split('<a href="/etkinlikler/')[1:]:
        slug = re.match(r'([^"]+)"', blok)
        tarih = re.search(r'site-news__date[^>]*>\s*([^<]+?)\s*<', blok)
        baslik = re.search(r'site-news__title[^>]*>(.*?)</h3>', blok, re.S)
        if not (slug and tarih and baslik) or slug[1] in goruldu:
            continue
        goruldu.add(slug[1])
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        if not bas:
            continue
        resim = re.search(r'<img src="([^"]+)"', blok.split("</a>")[0])
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Munzur Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin(MZ + "/etkinlikler/", slug[1]),
        }


KAYNAKLAR = [
    {"ad": "Munzur Üniversitesi", "tur": "universite", "url": MZ + "/etkinlikler", "cek": munzur},
    {"ad": "Tunceli İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://tunceli.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Tunceli", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/tunceli", "cek": etkinlik_io,
     "sehir": "Tunceli", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Tunceli Belediyesi", "tur": "belediye", "url": "https://www.tunceli.bel.tr",
     "not": "sertifika hatası — okunamıyor"},
    {"ad": "Tunceli Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.tunceli.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Tunceli Kültür Merkezi, Belediye Şehir Tiyatrosu", "tur": "belediye", "url": None,
     "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Munzur Kültür ve Doğa Festivali, Ovacık Kültür Şenliği…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
