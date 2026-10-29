"""Aydın kaynakları (plaka 09). Kaynak haritası: 2026-10-29.

Gelecek tarihli etkinlik veren kaynak: Aydın Adnan Menderes Üniversitesi (ADÜ Haber etkinlik sayfası).
Büyükşehir belediyesi sayfasında etkinlik yok ("etkinlikYok" görseli). Aydın'da Devlet Tiyatroları sahnesi yok.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Efeler", "Bozdoğan", "Buharkent", "Çine", "Didim", "Germencik", "İncirliova", "Karacasu", "Karpuzlu",
           "Koçarlı", "Köşk", "Kuşadası", "Kuyucak", "Nazilli", "Söke", "Sultanhisar", "Yenipazar"]
SALON_ILCE = {"atatürk kongre": "Efeler", "merkez kampüs": "Efeler", "atça": "Nazilli", "emine kutlu": "Kuşadası",
              "adü": "Efeler", "aydın adnan menderes": "Efeler"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# Aydın Adnan Menderes Üniversitesi — ADÜ Haber, Etkinlikler (HTML kartları)
# ------------------------------------------------------------------
def adu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="card mb-3 border-0">')[1:]:
        baslik = re.search(r'card-title[^>]*>\s*(.*?)\s*</h5>', blok, re.S)
        link = re.search(r'<a href="(/etkinlik/[^"]+)"', blok)
        zaman = re.search(r'fa-clock"></i>\s*(\d{1,2}\.\d{1,2}\.\d{4})\s+([0-2]?\d:[0-5]\d)?', blok)
        if not (baslik and zaman):
            continue
        tarih, _ = ortak.tarih_bul(zaman[1], bugun)
        if not tarih:
            continue
        yer = re.search(r'map-location-dot"></i>\s*(.*?)\s*<br>', blok, re.S)
        tur = re.search(r'badge[^>]*>\s*(.*?)\s*</span>', blok, re.S)
        resim = re.search(r"background-image:url\('([^']+)'\)", blok)
        mekan = ortak.temizle(yer[1]) if yer else "Adnan Menderes Üniversitesi"
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": zaman[2],
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Efeler"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": urllib.parse.quote(resim[1], safe=":/%") if resim else None,
            "url": "https://haber.adu.edu.tr" + link[1] if link else kaynak["url"],
            "ozet": ortak.temizle(tur[1]) if tur else None,
        }


KAYNAKLAR = [
    {"ad": "Aydın Adnan Menderes Üniversitesi", "tur": "universite", "url": "https://haber.adu.edu.tr/etkinlik/", "cek": adu},
    {"ad": "Aydın İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://aydin.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Aydın", "ilce_bul": salon_ilce, "varsayilan_ilce": "Efeler"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/aydin", "cek": etkinlik_io,
     "sehir": "Aydın", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Aydın Büyükşehir Belediyesi", "tur": "belediye", "url": "https://aydin.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama şu an boş (etkinlik yok görseli)"},
    {"ad": "Kuşadası Belediyesi", "tur": "belediye", "ilce": "Kuşadası", "url": "https://www.kusadasi.bel.tr/tr/etkinlikler",
     "not": "etkinlik sayfası var; otomatik okunmuyor"},
    {"ad": "Efeler ve Nazilli belediyeleri", "tur": "belediye", "url": "https://www.efeler.bel.tr/guncel/duyurular",
     "not": "duyurular/haberler; etkinlik takvimi okunmuyor"},
    {"ad": "Aydın Valiliği, ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.aydin.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Şehir tiyatrosu, kültür merkezleri", "tur": "belediye", "url": None, "not": "oyun/konser takvimi yayımlanmıyor"},
    {"ad": "İlçe festivalleri (Söke, Çine, Didim vb.)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
