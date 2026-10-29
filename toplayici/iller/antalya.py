"""Antalya kaynakları (plaka 07). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Akdeniz Üniversitesi ve Antalya Bilim Üniversitesi etkinlik takvimleri.
Antalya Büyükşehir Belediyesi etkinlik sayfası tarayıcıda (JS ile) yükleniyor; okunamadı.
Antalya'da Devlet Tiyatroları sahnesi var.
"""
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_opera, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akseki", "Aksu", "Alanya", "Demre", "Döşemealtı", "Elmalı", "Finike", "Gazipaşa", "Gündoğmuş", "İbradı", "Kaş",
           "Kemer", "Kepez", "Konyaaltı", "Korkuteli", "Kumluca", "Manavgat", "Muratpaşa", "Serik"]
SALON_ILCE = {"akdeniz üniversitesi": "Konyaaltı", "atatürk konferans": "Konyaaltı", "antalya bilim": "Döşemealtı",
              "expo": "Aksu", "antalya devlet opera": "Muratpaşa", "kültür merkezi": "Muratpaşa",
              "fakültesi": "Konyaaltı", "yüksekokulu": "Konyaaltı", "rektörlük": "Konyaaltı"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Akdeniz Üniversitesi — etkinlik listesi (HTML)
# ------------------------------------------------------------------
def akdeniz(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for link, blok in re.findall(r'<a href="(/tr/etkinlik/[^"]+)" class="list-group-item[^"]*">(.*?)</a>', sayfa, re.S):
        zaman = re.search(r'item-dateplace">\s*([^<]+?)\s*<', blok)
        yer = re.search(r"fa-map-marker[^>]*></i>\s*([^<]+)<", blok)
        baslik = re.search(r'event-name">(.*?)</div>', blok, re.S)
        if not (zaman and baslik):
            continue
        bas, _ = ortak.tarih_bul(zaman[1], bugun)
        mekan = ortak.temizle(yer[1]) if yer else None
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": ("Akdeniz Üniversitesi, " + mekan) if mekan and mekan.lower() != "online" else (mekan or "Akdeniz Üniversitesi"),
            "ilce": "Konyaaltı",
            "url": "https://www.akdeniz.edu.tr" + urllib.parse.quote(link, safe="/_-"),
        }


# ------------------------------------------------------------------
# 2) Antalya Bilim Üniversitesi — takvim sayfasına gömülü JSON
# ------------------------------------------------------------------
def abu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    veri = re.search(r'id="abu-etkinlik-events-data">(.*?)</script>', sayfa, re.S)
    if not veri:
        return
    for e in json.loads(veri[1]):
        bas, _ = ortak.tarih_bul(e.get("start") or "", bugun)
        bit, _ = ortak.tarih_bul(e.get("end") or "", bugun)
        if not bas:
            continue
        yield {
            "baslik": basliklar(ortak.temizle(e["title"])),
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": e.get("startTime") or None,
            "mekan": e.get("location") or "Antalya Bilim Üniversitesi",
            "ilce": "Döşemealtı",
            "url": "https://www.antalya.edu.tr" + e["url"] if e.get("url", "").startswith("/") else kaynak["url"],
            "ozet": ortak.temizle(e.get("summary")) or None,
        }


KAYNAKLAR = [
    {"ad": "Devlet Opera ve Balesi", "tur": "kultur", "url": "https://www.operabale.gov.tr", "cek": devlet_opera,
     "mudurluk": 5, "ilce_bul": salon_ilce, "varsayilan_ilce": "Muratpaşa"},
    {"ad": "Akdeniz Üniversitesi", "tur": "universite", "url": "https://www.akdeniz.edu.tr/tr/etkinlikler", "cek": akdeniz},
    {"ad": "Antalya Bilim Üniversitesi", "tur": "universite", "url": "https://www.antalya.edu.tr/tr/etkinlik-takvimi", "cek": abu},
    {"ad": "Antalya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://antalya.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Antalya", "ilce_bul": salon_ilce, "varsayilan_ilce": "Muratpaşa"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/antalya", "cek": etkinlik_io,
     "sehir": "Antalya", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / okunamayan kaynaklar (eksikler) ---
    {"ad": "Antalya Büyükşehir Belediyesi (kültür-sanat, şehir tiyatrosu)", "tur": "belediye", "url": "https://www.antalya.bel.tr/tr/etkinlikler",
     "not": "etkinlikler JavaScript ile yükleniyor; okunamadı"},
    {"ad": "Muratpaşa, Konyaaltı, Kepez belediyeleri", "tur": "belediye", "url": "https://www.konyaalti.bel.tr",
     "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Alanya, Manavgat, Aksu, Kemer belediyeleri", "tur": "belediye", "url": None, "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Alanya Alaaddin Keykubat, Akev ve diğer üniversiteler", "tur": "universite", "url": None, "not": "etkinlik sayfası bulunamadı"},
    {"ad": "Antalya Valiliği", "tur": "valilik", "url": "https://www.antalya.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "19 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok / bot koruması"},
    {"ad": "Altın Portakal Film Festivali, Antalya Piano Festivali, Uluslararası Aspendos Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; 2027 programları henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
