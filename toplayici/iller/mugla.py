"""Muğla kaynakları (plaka 48). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Muğla Sıtkı Koçman Üniversitesi ana sayfa etkinlik kutuları, Bodrum Belediyesi etkinlik takvimi.
Muğla Büyükşehir sitesi sonsuz yönlendirme (302) veriyor; Milas sertifikası bozuk — ikisi de okunamıyor.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Bodrum", "Dalaman", "Datça", "Fethiye", "Kavaklıdere", "Köyceğiz", "Marmaris", "Menteşe", "Milas", "Ortaca",
           "Seydikemer", "Ula", "Yatağan"]
SALON_ILCE = {"msku": "Menteşe", "mskü": "Menteşe", "sıtkı koçman": "Menteşe", "kötekli": "Menteşe", "ula gölet": "Ula",
              "şevket sabancı": "Bodrum", "b.b ": "Bodrum", "ölüdeniz": "Fethiye", "çalış": "Fethiye"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

MSKU = "https://www.mu.edu.tr"
BODRUM = "https://www.bodrum.bel.tr/"


# ------------------------------------------------------------------
# 1) Muğla Sıtkı Koçman Üniversitesi — ana sayfadaki etkinlik kutuları (HTML)
# ------------------------------------------------------------------
def msku(kaynak, bugun):
    sayfa = ortak.indir(MSKU)
    for blok in sayfa.split("<div class='lsitem")[1:]:
        link = re.search(r"<a href='(/tr/etkinlik/[^']+)'", blok)
        gun = re.search(r"class='trh'>\s*([^<]+?)\s*</span>\s*<span class='year'>\s*(\d{4})", blok)
        baslik = re.search(r"class='ect_name'>(.*?)</div>", blok, re.S)
        if not (link and gun and baslik):
            continue
        bas, _ = ortak.tarih_bul(f"{gun[1]} {gun[2]}", bugun)
        if not bas:
            continue
        yer = re.search(r"fa-map-marker'>\s*</i>\s*([^<]*?)\s*<i", blok, re.S)
        saat = re.search(r"fa-clock-o'>\s*</i>\s*([^<]*)<", blok)
        tur = re.search(r"class='etk_tur[^']*'>([^<]*)<", blok)
        mekan = ortak.temizle(html.unescape(yer[1])).strip(" -") if yer else ""
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan or "Muğla Sıtkı Koçman Üniversitesi",
            "ilce": salon_ilce(mekan, "Menteşe"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "url": urllib.parse.urljoin(MSKU, urllib.parse.quote(link[1], safe=":/%")),
        }


# ------------------------------------------------------------------
# 2) Bodrum Belediyesi — etkinlik takvimi (HTML kartlar)
# ------------------------------------------------------------------
def bodrum(kaynak, bugun):
    sayfa = ortak.indir(BODRUM + "etkinlik_takvimi")
    for blok in sayfa.split("card event-card")[1:]:
        link = re.search(r'href="(etkinlik\.php\?id=[^"]+)"', blok)
        baslik = re.search(r'<h5 class="card-title">.*?<a[^>]*>\s*(.*?)\s*</a>', blok, re.S)
        gun = re.search(r'fw-bold">\s*(\d{1,2})\s*</div>\s*<div class="small">\s*([^<]+?)\s*</div>\s*<div class="small">\s*(\d{4})',
                        blok, re.S)
        if not (link and baslik and gun):
            continue
        bas, _ = ortak.tarih_bul(f"{gun[1]} {gun[2]} {gun[3]}", bugun)
        if not bas:
            continue
        bit_m = re.search(r"Bitiş:\s*([^<]+)<", blok)
        bit = ortak.tarih_bul(bit_m[1], bugun)[0] if bit_m else None
        saat = re.search(r'bi-clock[^>]*></i>\s*<span[^>]*>\s*([^<]*)<', blok)
        yer = re.search(r'bi-geo-alt[^>]*></i>\s*<span[^>]*>\s*([^<]*?)\s*</span>', blok, re.S)
        tur = re.search(r'badge bg-secondary">([^<]*)<', blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        mekan = ortak.temizle(html.unescape(yer[1])) if yer else None
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": "Bodrum",
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": urllib.parse.urljoin(BODRUM, urllib.parse.quote(resim[1], safe=":/%")) if resim else None,
            "url": BODRUM + urllib.parse.quote(link[1], safe=":/?=%&"),
        }


KAYNAKLAR = [
    {"ad": "Muğla Sıtkı Koçman Üniversitesi", "tur": "universite", "ilce": "Menteşe", "url": MSKU, "cek": msku},
    {"ad": "Bodrum Belediyesi", "tur": "belediye", "ilce": "Bodrum", "url": BODRUM + "etkinlik_takvimi", "cek": bodrum},
    {"ad": "Muğla İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://mugla.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Muğla", "ilce_bul": salon_ilce, "varsayilan_ilce": "Menteşe"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/mugla", "cek": etkinlik_io,
     "sehir": "Muğla", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Muğla Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.mugla.bel.tr",
     "not": "site sonsuz yönlendirme veriyor — okunamıyor"},
    {"ad": "Fethiye Belediyesi", "tur": "belediye", "ilce": "Fethiye", "url": "https://www.fethiye.bel.tr",
     "not": "etkinlik takvimi yok; sadece haber (Ölüdeniz Hava Oyunları gibi)"},
    {"ad": "Marmaris Belediyesi", "tur": "belediye", "ilce": "Marmaris", "url": "https://www.marmaris.bel.tr",
     "not": "etkinlik takvimi yok; sadece haber"},
    {"ad": "Menteşe Belediyesi", "tur": "belediye", "ilce": "Menteşe", "url": "https://www.mentese.bel.tr",
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Milas Belediyesi", "tur": "belediye", "ilce": "Milas", "url": "https://www.milas.bel.tr",
     "not": "site sertifikası geçersiz — okunamıyor"},
    {"ad": "Muğla Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.mugla.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Bodrum Sarı Yaz, Ölüdeniz Hava Oyunları, Marmaris Uluslararası Yat Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
