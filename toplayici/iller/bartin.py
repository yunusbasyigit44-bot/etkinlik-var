"""Bartın kaynakları (plaka 74). Kaynak haritası: 2026-10-29.

Okunan kaynak: Bartın Üniversitesi (ana sayfadaki etkinlik kartları: tarih, saat, yer yazıyor).
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor. Belediye sitesi hata veriyor (500).
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Amasra", "Kurucaşile", "Ulus"]
SALON_ILCE = {"kutlubey": "Merkez", "bartın üniversitesi": "Merkez", "amasra": "Amasra", "ulus": "Ulus"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

BUY = "https://www.bartin.edu.tr"


def buy(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in sayfa.split('class="event-card"')[1:]:
        baslik = re.search(r"<h5>(.*?)</h5>", blok, re.S)
        link = re.search(r'<a href="(/etkinlikler/[^"]+)"', blok)
        tarih = re.search(r"<strong>Tarih:</strong>\s*([^<]+)<", blok)
        if not (baslik and link and tarih) or link[1] in goruldu:
            continue
        goruldu.add(link[1])
        bas, bit = ortak.tarih_bul(tarih[1].replace("/", "."), bugun)
        if not bas:
            continue
        saat = re.search(r"<strong>Saat:</strong>\s*([^<]+)<", blok)
        yer = re.search(r"<strong>Yer:</strong>\s*([^<]+)<", blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        mekan = ortak.temizle(yer[1]) if yer else "Bartın Üniversitesi"
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        if ortak.baska_il_mi(mekan, "Bartın"):
            continue
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(resim[1], safe=":/") if resim else None,
            "url": urllib.parse.urljoin(BUY + "/", link[1]),
        }


KAYNAKLAR = [
    {"ad": "Bartın Üniversitesi", "tur": "universite", "url": BUY + "/", "cek": buy},
    {"ad": "Bartın İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bartin.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bartın", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bartin", "cek": etkinlik_io,
     "sehir": "Bartın", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bartın Belediyesi", "tur": "belediye", "url": "https://www.bartin.bel.tr", "not": "site hata veriyor (500)"},
    {"ad": "Amasra Belediyesi", "tur": "belediye", "ilce": "Amasra", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Bartın Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Amasra Turizm ve Kültür Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
