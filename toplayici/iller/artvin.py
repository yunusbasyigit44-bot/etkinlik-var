"""Artvin kaynakları (plaka 08). Kaynak haritası: 2026-10-29.

Düzenli kaynak Artvin Çoruh Üniversitesi'nin etkinlik listesi (kongre merkezi, Hopa yerleşkesi vb.).
Belediyenin sitesinde güncel etkinlik yok.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ardanuç", "Arhavi", "Borçka", "Hopa", "Murgul", "Şavşat", "Yusufeli"]
SALON_ILCE = {"nihat gökyiğit": "Merkez", "atapark": "Merkez", "merkez yerleşke": "Merkez", "artvin devlet": "Merkez",
              "aile sağlığı": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# Artvin Çoruh Üniversitesi — etkinlik listesi (HTML, ilk 2 sayfa)
def acu(kaynak, bugun):
    goruldu = set()
    for sayfa_no in (1, 2):
        sayfa = ortak.indir(kaynak["url"] + ("" if sayfa_no == 1 else f"?page={sayfa_no}"))
        for blok in sayfa.split('<div class="media">')[1:]:
            baslik = re.search(r'<h4 class="media-heading"><a href="([^"]+)">(.*?)</a></h4>', blok, re.S)
            zaman = re.search(r"fa-calendar-alt\"></i>\s*([^<]+)<", blok)
            if not (baslik and zaman):
                continue
            ad = basliklar(ortak.temizle(baslik[2]))
            bas, _ = ortak.tarih_bul(zaman[1], bugun)
            if not bas or (ad, bas) in goruldu:
                continue
            goruldu.add((ad, bas))
            yer = re.search(r"fa-map-marker-alt\"></i>\s*([^<]+)", blok)
            resim = re.search(r'<img class="media-object" src="([^"]+)"', blok)
            mekan = ortak.temizle(yer[1]) if yer else "Artvin Çoruh Üniversitesi"
            yield {
                "baslik": ad,
                "tarih": bas,
                "saat": ortak.saat_bul(zaman[1]),
                "mekan": mekan,
                "ilce": salon_ilce(mekan, "Merkez"),
                "gorsel": resim[1].replace(" ", "%20") if resim else None,
                "url": baslik[1] if not baslik[1].lower().endswith(".pdf") else kaynak["url"],
            }


KAYNAKLAR = [
    {"ad": "Artvin Çoruh Üniversitesi", "tur": "universite", "url": "https://www.artvin.edu.tr/tr/etkinlik/tumu", "cek": acu},
    {"ad": "Artvin İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://artvin.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Artvin", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/artvin", "cek": etkinlik_io,
     "sehir": "Artvin", "ilce_bul": salon_ilce},
    {"ad": "Artvin Belediyesi", "tur": "belediye", "url": "https://www.artvin.bel.tr", "not": "etkinlik takvimi yok; haberler eski"},
    {"ad": "Artvin Valiliği", "tur": "valilik", "url": "https://www.artvin.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "8 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Hopa, Arhavi, Yusufeli, Şavşat belediyeleri", "tur": "belediye", "url": "https://www.hopa.bel.tr",
     "not": "etkinlik takvimi yok; sadece haber"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Kafkasör Kültür ve Sanat Festivali, Hopa Kemençe Festivali, Arhavi Çay Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; 2027 programı henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
