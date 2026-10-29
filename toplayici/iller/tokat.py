"""Tokat kaynakları (plaka 60). Kaynak haritası: 2026-10-29.

Okunan kaynak: Tokat Belediyesi (ana sayfadaki aylık takvim: gün + etkinlik adı + afiş; etkinlik sayfaları zaman aşımına
uğradığı için saat/mekân okunmuyor). Tokat Gaziosmanpaşa Üniversitesi etkinlikleri ayrı bir alt sitede
(etkinlikler.gop.edu.tr) ve okunmadı. Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Almus", "Artova", "Başçiftlik", "Erbaa", "Niksar", "Pazar", "Reşadiye", "Sulusaray", "Turhal",
           "Yeşilyurt", "Zile"]
SALON_ILCE = {"26 haziran": "Merkez", "atatürk kültür merkezi": "Merkez", "gaziosmanpaşa üniversitesi": "Merkez",
              "taşlıçiftlik": "Merkez", "tokat": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

BEL = "https://www.tokat.bel.tr"
AYLAR = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
         "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12}


def belediye(kaynak, bugun):
    # Ana sayfadaki aylık takvim: her gün hücresinde gün numarası ve etkinlik bağlantıları (alt = başlık) vardır.
    # Etkinlik sayfaları zaman aşımına uğrayabildiği için sadece ana sayfa okunur; saat/mekân alınmaz.
    sayfa = ortak.indir(kaynak["url"])
    ay = re.search(r"(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık) (20\d\d)", sayfa)
    if not ay:
        return
    ay_no, yil = AYLAR[ortak.kucuk(ay[1])], int(ay[2])
    gorulen = set()
    parcalar = re.split(r'z-10"[^>]*>(\d{1,2})</span>', sayfa)
    for i in range(1, len(parcalar) - 1, 2):
        gun, govde = int(parcalar[i]), parcalar[i + 1]
        govde = govde.split('z-10"')[0]
        for slug, ic in re.findall(r'<a href="/etkinlikler/([a-z0-9-]+)"(.*?)</a>', govde, re.S):
            adi = re.search(r'alt="([^"]+)"', ic)
            if (slug, gun) in gorulen or not adi or "basvuru" in slug:
                continue                   # kayıt/başvuru duyurusu etkinlik değildir
            gorulen.add((slug, gun))
            resim = re.search(r"https://assets\.tokat\.bel\.tr/tokatbld/events/[\w.-]+", ic)
            try:
                tarih = dt.date(yil, ay_no, gun)
            except ValueError:
                continue
            yield {
                "baslik": basliklar(ortak.temizle(html.unescape(adi[1]))),
                "tarih": tarih,
                "mekan": "Tokat Belediyesi",
                "ilce": "Merkez",
                "gorsel": resim[0] if resim else None,
                "url": BEL + "/etkinlikler/" + slug,
                "ucretsiz": True,
            }


KAYNAKLAR = [
    {"ad": "Tokat Belediyesi", "tur": "belediye", "url": BEL + "/", "cek": belediye},
    {"ad": "Tokat İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://tokat.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Tokat", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/tokat", "cek": etkinlik_io,
     "sehir": "Tokat", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Tokat Gaziosmanpaşa Üniversitesi", "tur": "universite", "url": "http://etkinlikler.gop.edu.tr",
     "not": "etkinlik takvimi ayrı alt sitede; okuyucu sonraki tura kaldı"},
    {"ad": "Erbaa, Niksar, Turhal, Zile belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Tokat Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.tokat.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Tokat Yaz Festivali, Niksar Kültür ve Turizm, Zile Pekmez…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
