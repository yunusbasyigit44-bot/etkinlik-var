"""Manisa kaynakları (plaka 45). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Manisa Büyükşehir Belediyesi Kültür (Şehir Tiyatrosu, konser, sergi) ve Manisa Celal Bayar Üniversitesi
ana sayfasındaki etkinlik kutuları.
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Ahmetli", "Akhisar", "Alaşehir", "Demirci", "Gölmarmara", "Gördes", "Kırkağaç", "Köprübaşı", "Kula", "Salihli",
           "Sarıgöl", "Saruhanlı", "Selendi", "Soma", "Şehzadeler", "Turgutlu", "Yunusemre"]
SALON_ILCE = {"celal bayar": "Yunusemre", "mcbü": "Yunusemre", "mcbu": "Yunusemre", "uğur mumcu": "Şehzadeler",
              "şehir tiyatrosu": "Şehzadeler", "mesir": "Şehzadeler", "spil": "Yunusemre"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Manisa Büyükşehir Belediyesi Kültür — etkinlik kartları (HTML)
# ------------------------------------------------------------------
KULTUR = "https://kultur.manisa.bel.tr"


def buyuksehir(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="event-card ')[1:]:
        a = re.search(r'<a href="(/etkinlik-detay/\d+)"', blok)
        ad_m = re.search(r'class="ech__title">(.*?)</h4>', blok, re.S)
        bas_m = re.search(r'data-start-date="(\d{4}-\d{2}-\d{2})"', blok)
        bit_m = re.search(r'data-end-date="(\d{4}-\d{2}-\d{2})"', blok)
        if not (a and ad_m and bas_m):
            continue
        bas, _ = ortak.tarih_bul(bas_m[1], bugun)
        bit, _ = ortak.tarih_bul(bit_m[1], bugun) if bit_m else (None, None)
        yer = re.search(r'class="ech__address">.*?</i>(.*?)</div>', blok, re.S)
        saat = re.search(r'<span class="label">Saat</span><span class="value">([^<]+)<', blok)
        kat = re.search(r'data-event-type="([^"]*)"', blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        mekan = ortak.temizle(yer[1]) if yer else None
        ad = basliklar(ortak.temizle(ad_m[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan or "", "Şehzadeler"),
            "kategori": ortak.kategori_tahmin(ad + " " + (html.unescape(kat[1]) if kat else "")),
            "gorsel": KULTUR + urllib.parse.quote(html.unescape(resim[1])) if resim else None,
            "url": KULTUR + a[1],
        }


# ------------------------------------------------------------------
# 2) Manisa Celal Bayar Üniversitesi — ana sayfadaki "Etkinlikler" kutuları (HTML)
# ------------------------------------------------------------------
def mcbu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    bolum = sayfa.split('id="etkinlikler"', 1)
    if len(bolum) < 2:
        return
    for blok in bolum[1].split('<a href="')[1:]:
        if "event-card-link" not in blok[:200]:
            continue
        href = blok.split('"', 1)[0]
        ad_m = re.search(r'<img[^>]+alt="([^"]*)"', blok, re.S)
        tarih_m = re.search(r"fa-calendar\"></i>\s*<span>\s*([^<]+?)\s*</span>", blok)
        if not (ad_m and tarih_m):
            continue
        tarihler = re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", tarih_m[1])
        if not tarihler:
            continue
        bas, _ = ortak.tarih_bul(tarihler[0], bugun)
        bit, _ = ortak.tarih_bul(tarihler[-1], bugun)
        saat = re.search(r"fa-clock\"></i>\s*<span>\s*([^<]+?)\s*</span>", blok)
        yer = re.search(r"fa-location-dot\"></i>\s*<span>([^<]+)</span>", blok)
        resim = re.search(r'<img[^>]+src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(ad_m[1]))
        mekan = ortak.temizle(yer[1]) if yer else "Manisa Celal Bayar Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Yunusemre"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin("https://www.mcbu.edu.tr/", html.unescape(href)),
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "Manisa Büyükşehir Belediyesi Kültür (Şehir Tiyatrosu, konser, sergi)", "tur": "belediye",
     "url": "https://kultur.manisa.bel.tr/etkinlikler", "cek": buyuksehir},
    {"ad": "Manisa Celal Bayar Üniversitesi", "tur": "universite", "ilce": "Yunusemre", "url": "https://www.mcbu.edu.tr", "cek": mcbu},
    {"ad": "Manisa İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://manisa.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/manisa", "cek": etkinlik_io,
     "sehir": "Manisa", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Yunusemre Belediyesi", "tur": "belediye", "ilce": "Yunusemre", "url": "https://www.yunusemre.bel.tr/etkinlikler",
     "not": "takvim JavaScript ile yükleniyor; okunmuyor (sonraki tur)"},
    {"ad": "Şehzadeler Belediyesi", "tur": "belediye", "ilce": "Şehzadeler", "url": "https://www.sehzadeler.bel.tr",
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Manisa Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.manisa.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Akhisar, Turgutlu, Salihli, Soma belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://manisa.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Manisa Mesir Macunu Festivali (Mart), Uluslararası Spil Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
