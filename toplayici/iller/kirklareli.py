"""Kırklareli kaynakları (plaka 39). Kaynak haritası: 2026-10-29.

Okunan kaynak: Lüleburgaz Belediyesi Etkinlik Hizmeti (sitenin herkese açık "güncel etkinlikler" verisi).
Kırklareli Üniversitesi sitesi sertifika hatası veriyor; Kırklareli Belediyesi duyuruları idari.
Devlet Tiyatroları'nın Kırklareli sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import json

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Babaeski", "Demirköy", "Kofçaz", "Lüleburgaz", "Pehlivanköy", "Pınarhisar", "Vize"]
SALON_ILCE = {"lysa": "Lüleburgaz"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Lüleburgaz Belediyesi — etkinlik hizmeti (JSON; sitenin kendi ana sayfasının kullandığı uç)
# ------------------------------------------------------------------
LB = "https://luleburgaz.bel.tr/api/v1/events/get-latest-events"


def luleburgaz(kaynak, bugun):
    for e in json.loads(ortak.indir(LB)):
        ad = ortak.temizle(e.get("title") or "")
        try:
            tarih = dt.date.fromisoformat((e.get("date") or "")[:10])
        except ValueError:
            continue
        if not ad:
            continue
        yer = ortak.temizle(e.get("adres") or "")
        yield {
            "baslik": basliklar(ad),
            "tarih": tarih,
            "mekan": yer or "Lüleburgaz",
            "ilce": "Lüleburgaz",
            "kategori": ortak.kategori_tahmin(ad),
            "url": "https://etkinlik.luleburgaz.bel.tr/etkinlik/%s" % e["id"],
        }


KAYNAKLAR = [
    {"ad": "Lüleburgaz Belediyesi", "tur": "belediye", "ilce": "Lüleburgaz", "url": "https://etkinlik.luleburgaz.bel.tr/", "cek": luleburgaz},
    {"ad": "Kırklareli İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kirklareli.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kırklareli", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kirklareli", "cek": etkinlik_io,
     "sehir": "Kırklareli", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kırklareli Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": "https://www.kirklareli.edu.tr",
     "not": "site sertifika hatası veriyor — okunamıyor"},
    {"ad": "Kırklareli Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://www.kirklareli.bel.tr/duyurular",
     "not": "duyurular idari (ihale, imar); etkinlik takvimi yok"},
    {"ad": "Babaeski, Vize, Pınarhisar, Demirköy belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Kırklareli Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kirklareli.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Kakava Şenlikleri, Kıyıköy ve İğneada etkinlikleri…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
