"""Burdur kaynakları (plaka 15). Kaynak haritası: 2026-10-29.

Tek verimli kaynak Burdur Mehmet Akif Ersoy Üniversitesi (ana sayfadaki etkinlik kutuları).
Burdur Belediyesi etkinlikleri duyururken tarihi sadece afişin içine yazıyor (görsel) — okunamıyor.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ağlasun", "Altınyayla", "Bucak", "Çavdır", "Çeltikçi", "Gölhisar", "Karamanlı", "Kemer", "Tefenni",
           "Yeşilova"]
SALON_ILCE = {"mehmet akif": "Merkez", "makü": "Merkez", "istiklal": "Merkez", "kültür pasta": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# Burdur Mehmet Akif Ersoy Üniversitesi — ana sayfadaki etkinlik kutuları (sunucuda üretilmiş HTML)
# ------------------------------------------------------------------
def makü(kaynak, bugun):
    sayfa = ortak.indir("https://www.mehmetakif.edu.tr/")
    goruldu = set()
    for blok in re.split(r'<a href="(?=/content/)', sayfa)[1:]:
        link = re.match(r'(/content/[^"]+)"', blok)
        # Etkinlik kutusunda takvim simgesi, başlık, tarih ve saat sırayla gelir
        takvim = re.search(r'calendar_blue\.svg.*?<div[^>]*>([^<]+)</div>', blok[:3000], re.S)
        baslik = re.search(r'font-semibold[^>]*>([^<]+)</div>', blok[:3000])
        if not (link and takvim and baslik) or link[1] in goruldu:
            continue
        goruldu.add(link[1])
        tarih, _ = ortak.tarih_bul(takvim[1], bugun)
        if not tarih:
            continue
        saat = re.search(r'clock_blue\.svg.*?<div[^>]*>([^<]+)</div>', blok[:3000], re.S)
        yer = re.search(r'location_blue\.svg.*?<p[^>]*>([^<]+)</p>', blok[:3000], re.S)
        resim = re.search(r'<img src="(https://depo[^"]+)"', blok[:3000])
        mekan = ortak.temizle(yer[1]) if yer else "Burdur Mehmet Akif Ersoy Üniversitesi"
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin("https://www.mehmetakif.edu.tr/", link[1]),
        }


KAYNAKLAR = [
    {"ad": "Burdur Mehmet Akif Ersoy Üniversitesi", "tur": "universite", "url": "https://www.mehmetakif.edu.tr/", "cek": makü},
    {"ad": "Burdur İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://burdur.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Burdur", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/burdur", "cek": etkinlik_io,
     "sehir": "Burdur", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Burdur Belediyesi", "tur": "belediye", "url": "https://burdur.bel.tr/feed/",
     "not": "konser/tiyatro duyuruları var ama tarih sadece afişin görselinde; otomatik okunmuyor"},
    {"ad": "Burdur Valiliği", "tur": "valilik", "url": "https://www.burdur.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "10 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Bucak, Gölhisar belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://burdur.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Salda, Bucak Kiraz, Kuyucak Yoğurt…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
