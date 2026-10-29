"""Uşak kaynakları (plaka 64). Kaynak haritası: 2026-10-29.

Okunan kaynak: Uşak Belediyesi etkinlik sayfası (kartlarda tarih, saat, mekan var). Uşak Üniversitesi etkinlik
akışı oturum açma sayfasına yönleniyor (okunamıyor). Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Banaz", "Eşme", "Karahallı", "Sivaslı", "Ulubey"]
SALON_ILCE = {"atatürk kültür merkezi": "Merkez", "ssk pazar": "Merkez", "uşak üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

BEL = "https://usak.bel.tr"


# ------------------------------------------------------------------
# 1) Uşak Belediyesi — etkinlik kartları (HTML)
# ------------------------------------------------------------------
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in sayfa.split('<a class="ev" href="')[1:]:
        link = re.match(r'([^"]+)"', blok)
        baslik = re.search(r"<h3>(.*?)</h3>", blok, re.S)
        meta = re.findall(r'<i class="ri-(map-pin|calendar)-line"></i>([^<]*)<', blok)
        yer = next((ortak.temizle(v) for k, v in meta if k == "map-pin"), None)
        zaman = next((v for k, v in meta if k == "calendar"), "")
        bas, bit = ortak.tarih_bul(zaman, bugun)
        if not (link and baslik and bas) or link[1] in goruldu:
            continue
        goruldu.add(link[1])
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(zaman),
            "mekan": yer or "Uşak",
            "ilce": salon_ilce(yer or "", "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.urljoin(BEL + "/", resim[1]) if resim else None,
            "url": urllib.parse.urljoin(BEL + "/", link[1]),
        }


KAYNAKLAR = [
    {"ad": "Uşak Belediyesi", "tur": "belediye", "url": BEL + "/etkinlikler?d=yaklasan", "cek": belediye},
    {"ad": "Uşak İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://usak.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Uşak", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/usak", "cek": etkinlik_io,
     "sehir": "Uşak", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Uşak Üniversitesi", "tur": "universite", "url": "https://www.usak.edu.tr",
     "not": "etkinlik akışı oturum açma sayfasına yönleniyor — okunamıyor"},
    {"ad": "Uşak Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.usak.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Eşme, Banaz, Sivaslı belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Uşak Kitap Fuarı, Ulubey Kanyonu etkinlikleri, Eşme Kilim…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
