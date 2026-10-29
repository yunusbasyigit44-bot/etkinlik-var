"""Osmaniye kaynakları (plaka 80). Kaynak haritası: 2026-10-29.

Okunan kaynak: Osmaniye Korkut Ata Üniversitesi etkinlik listesi (HTML, "gg.aa.yyyy - gg.aa.yyyy").
Belediyenin etkinlik takvimi 2019'dan beri boş; valilik duyuruları idari. Devlet Tiyatroları sahnesi yok.
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Bahçe", "Düziçi", "Hasanbeyli", "Kadirli", "Sumbas", "Toprakkale"]
SALON_ILCE = {"korkut ata": "Merkez", "osmaniye korkut": "Merkez", "bahçe": "Bahçe", "düziçi": "Düziçi", "kadirli": "Kadirli",
              "sumbas": "Sumbas", "toprakkale": "Toprakkale", "hasanbeyli": "Hasanbeyli"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Osmaniye Korkut Ata Üniversitesi — etkinlik listesi (geçmiş etkinlikler de var; toplayıcı eler)
# ------------------------------------------------------------------
def oku(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for link, ad, tarih in re.findall(
            r'<a href="(https://www\.osmaniye\.edu\.tr/tr/etkinlikler/\d+[^"]*)"[^>]*>\s*<div[^>]*>\s*<h5[^>]*>(.*?)</h5>.*?<small>(\d\d\.\d\d\.\d{4}[^<]*)</small>',
            sayfa, re.S):
        gunler = re.findall(r"(\d\d)\.(\d\d)\.(\d{4})", tarih)
        bas, bit = ortak.tarih_bul(" - ".join(f"{g}.{a}.{y}" for g, a, y in gunler[:1]), bugun)[0], None
        if len(gunler) > 1 and gunler[1] != gunler[0]:
            bit = ortak.tarih_bul("%s.%s.%s" % gunler[1], bugun)[0]
        if not bas:
            continue
        baslik = basliklar(ortak.temizle(html.unescape(ad)))
        yield {
            "baslik": baslik,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": "Osmaniye Korkut Ata Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(baslik),
            "url": link,
        }


KAYNAKLAR = [
    {"ad": "Osmaniye Korkut Ata Üniversitesi", "tur": "universite", "url": "https://www.osmaniye.edu.tr/tr/etkinlikler", "cek": oku},
    {"ad": "Osmaniye İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://osmaniye.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Osmaniye", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/osmaniye", "cek": etkinlik_io,
     "sehir": "Osmaniye", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Osmaniye Belediyesi", "tur": "belediye", "url": "https://www.osmaniye.bel.tr",
     "not": "etkinlik takvimi sayfası 2019'dan beri boş; duyurular idari"},
    {"ad": "Osmaniye Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.osmaniye.gov.tr/duyurular",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Kadirli, Düziçi, Bahçe, Toprakkale belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Yer Fıstığı, Karatepe Kültür Sanat, Zorkun Yayla Şenlikleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
