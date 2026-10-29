"""Kırşehir kaynakları (plaka 40). Kaynak haritası: 2026-10-29.

Okunan kaynak: Kırşehir Belediyesi etkinlikler sayfası (tarih + saat + başlık). Ahi Evran Üniversitesi sitesinde
okunabilir etkinlik takvimi bulunamadı. Devlet Tiyatroları'nın Kırşehir sahnesi yok; kaynak listede duruyor.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Akçakent", "Akpınar", "Boztepe", "Çiçekdağı", "Kaman", "Mucur"]
SALON_ILCE = {}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Kırşehir Belediyesi — etkinlik kartları (HTML): tarih (2026-10-29), saat (19:00), başlık
# ------------------------------------------------------------------
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("activity-item shadow-sm")[1:]:
        tarih = re.search(r'cvzico-calendar"></i>\s*(\d{4}-\d{2}-\d{2})', blok)
        saat = re.search(r'cvzico-clock"></i>\s*(\d{1,2}:\d{2})', blok)
        baslik = re.search(r'class="title mt-2">(.*?)</div>', blok, re.S)
        link = re.search(r'href="(https://www\.kirsehir\.bel\.tr/etkinlikler/[^"]+)"', blok)
        resim = re.search(r'<img src="(https://www\.kirsehir\.bel\.tr/storage/events/[^"]+)"', blok)
        if not (tarih and baslik):
            continue
        t, _ = ortak.tarih_bul(tarih[1], bugun)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": t,
            "saat": saat[1] if saat else None,
            "mekan": "Kırşehir Belediyesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": link[1] if link else kaynak["url"],
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "Kırşehir Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://www.kirsehir.bel.tr/etkinlikler", "cek": belediye},
    {"ad": "Kırşehir İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kirsehir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kırşehir", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kirsehir", "cek": etkinlik_io,
     "sehir": "Kırşehir", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kırşehir Ahi Evran Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": "https://www.ahievran.edu.tr",
     "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Kırşehir Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kirsehir.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Kaman, Mucur, Çiçekdağı belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Neşet Ertaş Anma Programı, Ahilik Haftası, Kaman Ceviz Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
