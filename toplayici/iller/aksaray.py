"""Aksaray kaynakları (plaka 68). Kaynak haritası: 2026-10-29.

Okunan kaynak: Aksaray Üniversitesi etkinlik takvimi (HTML liste). Aksaray Belediyesi'nin etkinlik sayfası var ama
son kayıt Eylül 2026'da kalmış (yaklaşan etkinlik yok) — "not" olarak listede. Devlet Tiyatroları sahnesi yok.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ağaçören", "Eskil", "Gülağaç", "Güzelyurt", "Ortaköy", "Sarıyahşi", "Sultanhanı"]
SALON_ILCE = {"aksaray üniversitesi": "Merkez", "asü": "Merkez", "iibf": "Merkez", "i̇i̇bf": "Merkez", "kampüs": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

ASU = "https://www.aksaray.edu.tr/"


# 1) Aksaray Üniversitesi — etkinlik takvimi (Başlama / Bitiş / Yeri alanları)
def asu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<ul class="event-list">')[-1].split("<li>"):
        baslik = re.search(r'<a href="([^"]+)" title="([^"]*)"', blok)
        bas_m = re.search(r"Başlama:</div>\s*<div[^>]*>([^<]+)<", blok)
        if not (baslik and bas_m):
            continue
        bit_m = re.search(r"Bitiş:</div>\s*<div[^>]*>([^<]+)<", blok)
        yer_m = re.search(r"Yeri:</div>\s*<div[^>]*>([^<]*)<", blok)
        resim = re.search(r'<img[^>]+src="([^"]+)"', blok)
        bas, _ = ortak.tarih_bul(bas_m[1], bugun)
        bit, _ = ortak.tarih_bul(bit_m[1], bugun) if bit_m else (None, None)
        if not bas:
            continue
        yer = ortak.temizle(yer_m[1]) if yer_m else ""
        ad = basliklar(ortak.temizle(baslik[2]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(bas_m[1]),
            "mekan": yer or "Aksaray Üniversitesi",
            "ilce": salon_ilce(yer, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            # sayfadaki resim şablon (dj-set) küçük resmi; kullanma
            "url": urllib.parse.urljoin(ASU, baslik[1]),
        }


KAYNAKLAR = [
    {"ad": "Aksaray Üniversitesi", "tur": "universite", "url": "https://www.aksaray.edu.tr/Etkinlik-takvimi", "cek": asu},
    {"ad": "Aksaray İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://aksaray.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Aksaray", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/aksaray", "cek": etkinlik_io,
     "sehir": "Aksaray", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Aksaray Belediyesi", "tur": "belediye", "url": "https://www.aksaray.bel.tr/Etkinlikler.aspx",
     "not": "etkinlik sayfası var ama son kayıt Eylül 2026'da kalmış (yaklaşan etkinlik yok); yenilenince okunabilir"},
    {"ad": "Aksaray Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.aksaray.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Ihlara Kültür ve Turizm, Hasan Dağı…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
