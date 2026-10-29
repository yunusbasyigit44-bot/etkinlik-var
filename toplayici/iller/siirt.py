"""Siirt kaynakları (plaka 56). Kaynak haritası: 2026-10-29.

Siirt Üniversitesi ana sayfasındaki etkinlik şeridi (afiş görseli + tarih; başlık dosya adından). Siirt Belediyesi/Valiliği
etkinlik takvimi yayınlamıyor. Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Aydınlar", "Baykan", "Eruh", "Kurtalan", "Pervari", "Şirvan", "Tillo"]
SALON_ILCE = {"siirt üniversitesi": "Merkez", "kezer": "Merkez", "botan": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

SIIRT_EDU = "https://www.siirt.edu.tr"


def siirt_edu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for dosya, tur, g, a, y in re.findall(
            r'<a href="(/foto/etkinlik/[^"]+)"[^>]*>.*?</a><span class="postdate">([^<\d]*?)\s*(\d{1,2})\.(\d{1,2})\.(\d{4})</span>',
            sayfa, re.S):
        ad = re.sub(r"\d{4}\d+\.\w+$", "", dosya.rsplit("/", 1)[-1])
        ad = re.sub(r"\.\w+$", "", ad) if re.search(r"\.\w+$", ad) else ad
        ad = basliklar(ad.replace("-", " ").strip().title().replace(" I ", " İ "))
        if not ad:
            continue
        bas, _ = ortak.tarih_bul(f"{g}.{a}.{y}", bugun)
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Siirt Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad + " " + tur),
            "gorsel": SIIRT_EDU + dosya,
            "url": SIIRT_EDU + "/etkinliktakvimi.html",
            "ozet": tur.strip() or None,
        }


KAYNAKLAR = [
    {"ad": "Siirt Üniversitesi", "tur": "universite", "url": SIIRT_EDU + "/etkinliktakvimi.html", "cek": siirt_edu},
    {"ad": "Siirt İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://siirt.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Siirt", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/siirt", "cek": etkinlik_io,
     "sehir": "Siirt", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Siirt Belediyesi", "tur": "belediye", "url": None, "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Siirt Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.siirt.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Siirt Fıstık Festivali, Siirt Kültür ve Turizm günleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
