"""Karaman kaynakları (plaka 70). Kaynak haritası: 2026-10-29.

Okunan kaynak: Karamanoğlu Mehmetbey Üniversitesi etkinlik takvimi (aylık takvim sayfası, içinde bulunulan ay).
Karaman Belediyesi'nin etkinlik sayfası yok (haber/duyuru). Devlet Tiyatroları sahnesi yok.
"""
import datetime as dt
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ayrancı", "Başyayla", "Ermenek", "Kazımkarabekir", "Sarıveliler"]
SALON_ILCE = {"kmü": "Merkez", "karamanoğlu": "Merkez", "kmu": "Merkez", "yunus emre": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KMU = "https://etkinlik.kmu.edu.tr/"


# 1) Karamanoğlu Mehmetbey Üniversitesi — aylık takvim (gün bağlantısı + etkinlik satırları)
def kmu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for parca in re.split(r'day\.aspx\?day=', sayfa)[1:]:
        gun = re.match(r"(\d{4})-(\d{2})-(\d{2})", parca)
        if not gun:
            continue
        tarih = dt.date(int(gun[1]), int(gun[2]), int(gun[3]))
        # bu günün bölümü: bir sonraki gün hücresine kadar (split zaten orada bitirir)
        for olay in re.finditer(r'<div class="CalendarEvent"[^>]*>(.*?)</div>', parca, re.S):
            a = re.search(r"event_id=(\d+)[^>]*>([^<]+)</a>", olay[1])
            if not a:
                continue
            ad = basliklar(ortak.temizle(html.unescape(a[2])))
            if not ad:
                continue
            saat = re.search(r"(\d{2}:\d{2})", olay[1])
            yield {
                "baslik": ad,
                "tarih": tarih,
                "saat": saat[1] if saat and saat[1] != "00:00" else None,
                "mekan": "Karamanoğlu Mehmetbey Üniversitesi",
                "ilce": "Merkez",
                "kategori": ortak.kategori_tahmin(ad),
                "url": KMU + "event_view_popup.aspx?event_id=" + a[1],
            }


KAYNAKLAR = [
    {"ad": "Karamanoğlu Mehmetbey Üniversitesi", "tur": "universite", "url": KMU + "index.aspx", "cek": kmu},
    {"ad": "Karaman İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://karaman.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Karaman", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/karaman", "cek": etkinlik_io,
     "sehir": "Karaman", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Karaman Belediyesi", "tur": "belediye", "url": "https://www.karaman.bel.tr",
     "not": "etkinlik sayfası yok; haber ve duyurular tarihsiz"},
    {"ad": "Karaman Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.karaman.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Uluslararası Türkçe Olimpiyatları, Karaman Dil Bayramı: 27 Mayıs Türk Dil Bayramı, Ermenek Kiraz…)",
     "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
