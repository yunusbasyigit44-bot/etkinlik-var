"""Amasya kaynakları (plaka 05). Kaynak haritası: 2026-10-29.

Amasya Belediyesi'nin etkinlik sayfası (Şehzade Salonu tiyatro/konser programı) düzenli kaynak;
şu an son kaydı Şubat 2026, yeni program girilince kendiliğinden gelir.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Göynücek", "Gümüşhacıköy", "Hamamözü", "Merzifon", "Suluova", "Taşova"]
SALON_ILCE = {"şehzade salonu": "Merkez", "zeynep hatun": "Merkez", "amasya üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# Amasya Belediyesi — etkinlik listesi (HTML), tarih "15/02/2026 20:00"
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="entry-post"')[1:]:
        baslik = re.search(r'<h4><a href="([^"]+)">(.*?)</a></h4>', blok, re.S)
        zamanlar = re.findall(r"mdi-calendar-clock\"></em>\s*([^<]+)<", blok)
        if not (baslik and zamanlar):
            continue
        bas, _ = ortak.tarih_bul(zamanlar[0], bugun)
        bit, _ = ortak.tarih_bul(zamanlar[-1], bugun)
        yer = re.search(r"<b>Yer:\s*</b>\s*([^<]+)<", blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        mekan = ortak.temizle(yer[1]) if yer else None
        ad = basliklar(ortak.temizle(baslik[2]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bas and bit > bas else None,
            "saat": ortak.saat_bul(zamanlar[0]),
            "mekan": mekan,
            "ilce": salon_ilce(mekan or "", "Merkez"),
            "gorsel": resim[1].replace(" ", "%20") if resim else None,
            "url": urllib.parse.urljoin("https://amasya.bel.tr/", baslik[1]),
            "ucretsiz": None,
        }


KAYNAKLAR = [
    {"ad": "Amasya Belediyesi", "tur": "belediye", "url": "https://amasya.bel.tr/etkinlikler", "cek": belediye},
    {"ad": "Amasya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://amasya.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Amasya", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/amasya", "cek": etkinlik_io,
     "sehir": "Amasya", "ilce_bul": salon_ilce},
    {"ad": "Amasya Üniversitesi", "tur": "universite", "url": "https://takvim.amasya.edu.tr/", "not": "etkinlik takvimi var ama şu an boş (JS ile yükleniyor)"},
    {"ad": "Amasya Belediyesi Şehir Tiyatrosu", "tur": "belediye", "url": "https://tiyatro.amasya.bel.tr/", "not": "site hata veriyor (500)"},
    {"ad": "Amasya Valiliği", "tur": "valilik", "url": "https://www.amasya.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "6 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Merzifon, Suluova, Gümüşhacıköy, Taşova belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Amasya Elması Festivali, Uluslararası Amasya Kültür ve Sanat Sempozyumu", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
