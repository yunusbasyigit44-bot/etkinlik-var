"""Çankırı kaynakları (plaka 18). Kaynak haritası: 2026-10-29.

Tek verimli kaynak Çankırı Karatekin Üniversitesi'nin "Tüm Etkinlikler" sayfası (ilk 20 kayıt, en yeni önce).
Belediyenin etkinlikler sayfası boş. Çankırı'da Devlet Tiyatroları sahnesi yok; kaynak yine de listede.
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Atkaracalar", "Bayramören", "Çerkeş", "Eldivan", "Ilgaz", "Kızılırmak", "Korgun", "Kurşunlu", "Orta",
           "Şabanözü", "Yapraklı"]
SALON_ILCE = {"karatekin": "Merkez", "yaran": "Merkez", "kongre": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)
KK = "https://www.karatekin.edu.tr"


# ------------------------------------------------------------------
# Çankırı Karatekin Üniversitesi — "Tüm Etkinlikler" kartları (HTML)
# ------------------------------------------------------------------
def karatekin(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="content-list-card"')[1:]:
        link = re.search(r'href="(/etkinlik/[^"]+)"', blok)
        baslik = re.search(r'<h2 class="content-list-card-title">(.*?)</h2>', blok, re.S)
        tarih = re.search(r'<time[^>]+datetime="(\d{4}-\d{2}-\d{2})"', blok)
        if not (link and baslik and tarih):
            continue
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        if re.search(r"Bakü|Antalya|COP31|Azerbaycan", html.unescape(baslik[1])):
            continue                       # üniversitenin katıldığı ama Çankırı'da yapılmayan etkinlikler
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        ozet = re.search(r'data-search-text="([^"]*)"', blok)
        metin = html.unescape(ozet[1]) if ozet else ad
        resim = re.search(r'<img[^>]+src="(https://medya[^"]+)"', blok)
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Çankırı Karatekin Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(metin[:200]),
            "gorsel": urllib.parse.quote(resim[1], safe=":/%") if resim else None,
            "url": KK + link[1],
        }


KAYNAKLAR = [
    {"ad": "Çankırı Karatekin Üniversitesi", "tur": "universite", "url": KK + "/tum-etkinlikler", "cek": karatekin},
    {"ad": "Çankırı İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://cankiri.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Çankırı", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/cankiri", "cek": etkinlik_io,
     "sehir": "Çankırı", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Çankırı Belediyesi", "tur": "belediye", "url": "https://cankiri.bel.tr/etkinlikler",
     "not": "etkinlikler sayfası boş; haberler olmuş etkinlikleri anlatıyor"},
    {"ad": "Çankırı Valiliği ve 11 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.cankiri.gov.tr",
     "not": "duyurular idari; etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://cankiri.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Ilgaz, Çerkeş, Orta belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Uluslararası Çankırı Tuz Festivali", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
