"""Kocaeli kaynakları (plaka 41). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Gebze Belediyesi (kendi JSON etkinlik listesi), İzmit Belediyesi (yıllık etkinlik zaman çizelgesi).
Büyükşehir etkinlik sayfası dinamik yükleniyor ve şu an boş dönüyor; Kocaeli Üniversitesi sertifika hatası veriyor.
"""
import datetime as dt
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel",
           "Kartepe", "Körfez"]
SALON_ILCE = {"arapçeşme": "Gebze", "gebze": "Gebze", "gtü": "Gebze", "seka": "İzmit", "oyuncak müzesi": "İzmit",
              "kocaeli üniversitesi": "İzmit", "sabancı": "İzmit"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Gebze Belediyesi — sitenin kullandığı JSON etkinlik listesi
# ------------------------------------------------------------------
GEBZE = "https://www.gebze.bel.tr/"


def gebze(kaynak, bugun):
    for e in json.loads(ortak.indir(kaynak["url"])):
        try:
            tarih = dt.date.fromisoformat(e["tarih"])
        except (KeyError, ValueError):
            continue
        if tarih < bugun:
            continue
        ad = basliklar(ortak.temizle(e.get("baslik")))
        mekan = basliklar(ortak.temizle(e.get("konum"))) or None
        resim = e.get("resim")
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": ortak.saat_bul(e.get("saat") or ""),
            "mekan": mekan,
            "ilce": "Gebze",
            "kategori": ortak.kategori_tahmin(ad + " " + (e.get("kategori") or "")),
            "gorsel": urllib.parse.quote(GEBZE + resim, safe=":/%") if resim else None,
            "url": GEBZE + e["url"] if e.get("url") else None,
            "ozet": e.get("kategori") or None,
        }


# ------------------------------------------------------------------
# 2) İzmit Belediyesi — "2026 Yılı Etkinliklerimiz" zaman çizelgesi (başlık: topluluk/etkinlik, tarih: h2)
# ------------------------------------------------------------------
def izmit(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="bold_timeline_item_header">')[1:]:
        baslik = re.search(r'supertitle_inner">(.*?)</span>', blok, re.S)
        tarih_m = re.search(r'header_title">(.*?)</h2>', blok, re.S)
        alt = re.search(r'header_subtitle">(.*?)</p>', blok, re.S)
        if not (baslik and tarih_m):
            continue
        t = ortak.temizle(tarih_m[1])
        bas, _ = ortak.tarih_bul(t, bugun)
        if not bas:
            continue
        bit = None
        ikinci = re.findall(r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+", t)
        if len(ikinci) > 1:
            bit, _ = ortak.tarih_bul(ikinci[-1] + (" " + str(bas.year)), bugun)
        resim = re.search(r'<img[^>]+src="([^"]+)"', blok)
        tur = ortak.temizle(alt[1]) if alt else ""
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": None,
            "ilce": "İzmit",
            "kategori": ortak.kategori_tahmin(tur) if ortak.kategori_tahmin(tur) != "Diğer" else ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": kaynak["url"],
            "ucretsiz": True,
            "ozet": basliklar(tur) if tur else None,
        }


KAYNAKLAR = [
    {"ad": "Gebze Belediyesi", "tur": "belediye", "ilce": "Gebze", "url": "https://www.gebze.bel.tr/json/etkinlik.json", "cek": gebze},
    {"ad": "İzmit Belediyesi", "tur": "belediye", "ilce": "İzmit", "url": "https://izmit.bel.tr/2026-etkinliklerimiz/", "cek": izmit},
    {"ad": "Kocaeli İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kocaeli.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kocaeli", "cek": etkinlik_io,
     "sehir": "Kocaeli", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kocaeli Büyükşehir Belediyesi (etkinlikler, Şehir Tiyatrosu)", "tur": "belediye", "url": "https://www.kocaeli.bel.tr/etkinlikler/",
     "not": "liste sayfaya sonradan yükleniyor ve şu an boş dönüyor; okunamıyor"},
    {"ad": "Kocaeli Üniversitesi", "tur": "universite", "ilce": "İzmit", "url": "https://www.kocaeli.edu.tr",
     "not": "sitenin sertifikası doğrulanamıyor (SSL hatası) — okunmuyor"},
    {"ad": "Gebze Teknik Üniversitesi", "tur": "universite", "ilce": "Gebze", "url": "https://takvim.gtu.edu.tr/",
     "not": "takvim sayfası çok büyük (14 MB) ve ders programı karışık; okunmuyor"},
    {"ad": "Kocaeli Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kocaeli.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gölcük, Körfez, Darıca, Başiskele, Kartepe belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://kocaeli.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Kartepe Kış Festivali, Kocaeli Kitap Fuarı…", "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
