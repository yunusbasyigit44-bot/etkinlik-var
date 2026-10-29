"""Malatya kaynakları (plaka 44). Kaynak haritası: 2026-10-29.

Okunan kaynak: Yeşilyurt Belediyesi etkinlik listesi. Büyükşehir etkinlik sayfası şu an "Etkinlik bulunamadı" diyor
(Şehir Tiyatrosu ve Açık Hava sahneleri filtre olarak var; etkinlik girilince okunabilir). İnönü Üniversitesi sertifika hatası veriyor.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akçadağ", "Arapgir", "Arguvan", "Battalgazi", "Darende", "Doğanşehir", "Doğanyol", "Hekimhan", "Kale", "Kuluncak",
           "Pütürge", "Yazıhan", "Yeşilyurt"]
SALON_ILCE = {"malatya şehir tiyatrosu": "Yeşilyurt", "inönü": "Battalgazi", "i̇nönü": "Battalgazi", "turgut özal": "Battalgazi",
              "kernek": "Battalgazi", "yeşilyurt": "Yeşilyurt", "battalgazi": "Battalgazi"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Yeşilyurt Belediyesi — etkinlik kartları (HTML)
# ------------------------------------------------------------------
def yesilyurt(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    gorulen = set()
    for blok in sayfa.split('<div class="activity-card">')[1:]:
        a = re.search(r'<h3 class="title"><a\s+href="([^"]+)">(.*?)</a>', blok, re.S)
        tarihler = re.findall(r'fa-calendar-alt"></i></span>\s*<div class="text">([^<]+)<', blok)
        if not (a and tarihler) or a[1] in gorulen:
            continue
        gorulen.add(a[1])
        bas, _ = ortak.tarih_bul(tarihler[0], bugun)
        bit, _ = ortak.tarih_bul(tarihler[-1], bugun)
        if not bas:
            continue
        saat = re.search(r'fa-clock"></i></span>\s*<div class="text">([^<]+)<', blok)
        konu = re.search(r'class="text"\s+href="[^"]*/konu/[^"]*">([^<]+)<', blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(a[2]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": "Yeşilyurt Belediyesi",
            "ilce": "Yeşilyurt",
            "kategori": ortak.kategori_tahmin(ad + " " + (konu[1] if konu else "")),
            "gorsel": resim[1].replace(" ", "%20") if resim else None,
            "url": a[1],
            "ucretsiz": True,
            "ozet": ortak.temizle(konu[1]) if konu else None,
        }


KAYNAKLAR = [
    {"ad": "Yeşilyurt Belediyesi", "tur": "belediye", "ilce": "Yeşilyurt", "url": "https://yesilyurt.bel.tr/etkinlikler", "cek": yesilyurt},
    {"ad": "Malatya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://malatya.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/malatya", "cek": etkinlik_io,
     "sehir": "Malatya", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Malatya Büyükşehir Belediyesi (Şehir Tiyatrosu, Açık Hava)", "tur": "belediye", "url": "https://www.malatya.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama şu an boş ('Etkinlik bulunamadı'); okunmuyor"},
    {"ad": "İnönü Üniversitesi", "tur": "universite", "ilce": "Battalgazi", "url": "https://www.inonu.edu.tr",
     "not": "sitenin sertifikası doğrulanamıyor (SSL hatası) — okunmuyor"},
    {"ad": "Malatya Turgut Özal Üniversitesi", "tur": "universite", "ilce": "Battalgazi", "url": "https://etkinlik.ozal.edu.tr",
     "not": "etkinlik sistemi sadece idari duyuru veriyor; okunmuyor"},
    {"ad": "Battalgazi Belediyesi", "tur": "belediye", "ilce": "Battalgazi", "url": "https://www.battalgazi.bel.tr/etkinlik/",
     "not": "etkinlik sayfasında okunabilir liste bulunamadı (sonraki tur)"},
    {"ad": "Malatya Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.malatya.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://malatya.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Malatya Kayısı Festivali, Uluslararası Malatya Film Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
