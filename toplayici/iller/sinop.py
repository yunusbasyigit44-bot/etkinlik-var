"""Sinop kaynakları (plaka 57). Kaynak haritası: 2026-10-29.

Okunan kaynak: Sinop Üniversitesi etkinlik takvimi (sayfaya gömülü FullCalendar verisi). Sinop Belediyesi'nin okunabilir
bir etkinlik takvimi yok. Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import json
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ayancık", "Boyabat", "Dikmen", "Durağan", "Erfelek", "Gerze", "Saraydüzü", "Türkeli"]
SALON_ILCE = {"sinop üniversitesi": "Merkez", "boyabat": "Boyabat", "gerze": "Gerze", "ayancık": "Ayancık"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


def sinop_edu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    i = sayfa.find("var events = ")
    if i < 0:
        return
    olaylar, _ = json.JSONDecoder().raw_decode(sayfa[i + len("var events = "):])
    for o in olaylar:
        ad = basliklar(ortak.temizle(o.get("title") or ""))
        ek = o.get("extendedProps") or {}
        if not ad or re.search(r"başvuru|son tarih", ortak.kucuk(ad)):
            continue                       # başvuru tarihleri etkinlik değildir
        try:
            bas = dt.date.fromisoformat(o["start"][:10])
            bit = dt.date.fromisoformat(o["end"][:10]) if o.get("end") else None
        except (KeyError, ValueError):
            continue
        saat = o["start"][11:16] if not o.get("allDay") and len(o["start"]) > 15 else None
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": saat if saat and saat != "00:00" else None,
            "mekan": "Sinop Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad + " " + (ek.get("kat") or "")),
            "gorsel": ek.get("img") or None,
            "url": ek.get("permalink") or kaynak["url"],
            "ozet": ek.get("kat") or None,
        }


KAYNAKLAR = [
    {"ad": "Sinop Üniversitesi", "tur": "universite", "url": "https://www.sinop.edu.tr/etkinlik/", "cek": sinop_edu},
    {"ad": "Sinop İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://sinop.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Sinop", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/sinop", "cek": etkinlik_io,
     "sehir": "Sinop", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Sinop Belediyesi", "tur": "belediye", "url": "https://www.sinop.bel.tr", "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Sinop Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.sinop.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gerze, Boyabat, Ayancık belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Sinop Uluslararası Kültür ve Sanat Festivali, Gerze Hamsi Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
