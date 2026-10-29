"""Hatay kaynakları (plaka 31). Kaynak haritası: 2026-10-29.

Hatay Büyükşehir Belediyesi etkinlik sayfası (sitenin kendi JSON ucu; şu an yaklaşan etkinlik yok, açıldığında gelir).
Hatay Mustafa Kemal Üniversitesi sitesi sadece JavaScript ile açıldığı için okunamıyor.
Devlet Tiyatroları Hatay sahnesi ortak kaynakla izlenir.
"""
import datetime as dt
import html
import json
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Antakya", "Altınözü", "Arsuz", "Belen", "Defne", "Dörtyol", "Erzin", "Hassa", "İskenderun", "Kırıkhan",
           "Kumlu", "Payas", "Reyhanlı", "Samandağ", "Yayladağı"]
SALON_ILCE = {"devlet tiyatro": "Antakya", "hatay kültür": "Antakya", "mkü": "Antakya", "mustafa kemal": "Antakya",
              "habib-i neccar": "Antakya", "sahil": "İskenderun"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

HB = "https://www.hatay.bel.tr"


# ------------------------------------------------------------------
# 1) Hatay Büyükşehir Belediyesi — /api/events (sayfanın kendi kullandığı uç)
# ------------------------------------------------------------------
def buyuksehir(kaynak, bugun):
    veri = json.loads(ortak.indir(HB + "/api/events?language=tr-TR&skip=0&take=40&search="))
    for e in veri.get("data", []):
        try:
            zaman = dt.datetime.fromisoformat(e["date"])
        except (KeyError, ValueError):
            continue
        ad = basliklar(ortak.temizle(html.unescape(e["name"])))
        resim = e.get("image")
        yield {
            "baslik": ad,
            "tarih": zaman.date(),
            "saat": zaman.strftime("%H:%M") if (zaman.hour or zaman.minute) else None,
            "mekan": None,
            "ilce": "Antakya",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(HB + resim, safe=":/%") if resim else None,
            "url": HB + e["url"] if e.get("url") else kaynak["url"],
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "Hatay Büyükşehir Belediyesi", "tur": "belediye", "url": HB + "/etkinlikler", "cek": buyuksehir},
    {"ad": "Hatay İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://hatay.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Hatay", "ilce_bul": salon_ilce, "varsayilan_ilce": "Antakya"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/hatay", "cek": etkinlik_io,
     "sehir": "Hatay", "ilce_bul": salon_ilce, "varsayilan_ilce": "Antakya"},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Hatay Mustafa Kemal Üniversitesi", "tur": "universite", "ilce": "Antakya", "url": "https://www.mku.edu.tr",
     "not": "site sadece JavaScript ile açılıyor — okunamıyor"},
    {"ad": "İskenderun Teknik Üniversitesi", "tur": "universite", "ilce": "İskenderun", "url": None,
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Hatay Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.hatay.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "İskenderun, Defne, Samandağ, Arsuz belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Zeytin Festivali, Uluslararası Antakya Medeniyetler Korosu…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
