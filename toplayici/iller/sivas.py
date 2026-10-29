"""Sivas kaynakları (plaka 58). Kaynak haritası: 2026-10-29.

Okunan kaynak: Sivas Cumhuriyet Üniversitesi etkinlik sayfası (sayfaya gömülü ETKINLIKLER verisi; arşivi de içerir,
geçmişleri toplayıcı eler). Devlet Tiyatroları Sivas sahnesi ortak okuyucuyla gelir. Sivas Belediyesi'nin etkinlik
sayfası çalışıyor ama şu an hiç etkinlik listelemiyor (örnek görülemediği için okuyucu yazılmadı).
"""
import datetime as dt
import html
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Akıncılar", "Altınyayla", "Divriği", "Doğanşar", "Gemerek", "Gölova", "Gürün", "Hafik", "İmranlı",
           "Kangal", "Koyulhisar", "Suşehri", "Şarkışla", "Ulaş", "Yıldızeli", "Zara"]
SALON_ILCE = {"cumhuriyet üniversitesi": "Merkez", "ihramcızade": "Merkez", "fidan yazıcıoğlu": "Merkez",
              "dt sivas": "Merkez", "sivas devlet": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)
CU = "https://www.cumhuriyet.edu.tr"


def cumhuriyet(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    i = sayfa.find("const ETKINLIKLER = ")
    if i < 0:
        return
    olaylar, _ = json.JSONDecoder().raw_decode(sayfa[i + len("const ETKINLIKLER = "):])
    for o in olaylar:
        try:
            bas = dt.date.fromisoformat(o["d"][:10])
        except (KeyError, ValueError):
            continue
        if bas < bugun:
            continue                       # arşiv binlerce eski kayıt içeriyor
        ad = basliklar(ortak.temizle(html.unescape(o.get("t") or "")))
        if not ad:
            continue
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Sivas Cumhuriyet Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": o.get("a") or None,
            "url": urllib.parse.urljoin(CU + "/", o["u"]) if o.get("u") else kaynak["url"],
            "ozet": ortak.temizle(html.unescape(o.get("ac") or ""))[:200] or None,
        }


KAYNAKLAR = [
    {"ad": "Sivas Cumhuriyet Üniversitesi", "tur": "universite", "url": CU + "/etkinlik/", "cek": cumhuriyet},
    {"ad": "Sivas İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://sivas.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Sivas", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/sivas", "cek": etkinlik_io,
     "sehir": "Sivas", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Sivas Belediyesi", "tur": "belediye", "url": "https://www.sivas.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama şu an boş (tarih/tür/mekân süzgeçleri hazır); etkinlik girilince eklenecek"},
    {"ad": "Sivas Bilim ve Teknoloji Üniversitesi", "tur": "universite", "url": None, "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Sivas Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.sivas.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Sivas Kültür Yolu, Divriği Ulu Camii anma günleri, Kangal Balıklı Kaplıca…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
