"""Yozgat kaynakları (plaka 66). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Yozgat Bozok Üniversitesi (ana sayfadaki etkinlik kartları) ve Yozgat Belediyesi etkinlik sitesi
(şu an listesi 2025'te kalmış; yeni etkinlik girilince kendiliğinden gelir). Devlet Tiyatroları sahnesi yok.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Akdağmadeni", "Aydıncık", "Boğazlıyan", "Çandır", "Çayıralan", "Çekerek", "Kadışehri", "Saraykent",
           "Sarıkaya", "Sorgun", "Şefaatli", "Yenifakılı", "Yerköy"]
SALON_ILCE = {"bozok": "Merkez", "cumhuriyet meydanı": "Merkez", "sürmeli": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

BOZOK = "https://www.bozok.edu.tr/"


# 1) Yozgat Bozok Üniversitesi — ana sayfadaki "post-event" kartları (gün + ay + başlık)
def bozok(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="post-event">')[1:]:
        link = re.search(r'href="(/etkinlik/etkinlik/\d+)"', blok)
        gun = re.search(r'h3 font-weight-bold[^>]*>\s*(\d{1,2})\s*</div>\s*<span[^>]*>\s*([^<]+?)\s*</span>', blok)
        baslik = re.search(r"<h6[^>]*>(.*?)</h6>", blok, re.S)
        if not (link and gun and baslik):
            continue
        bas, _ = ortak.tarih_bul(f"{gun[1]} {gun[2]}", bugun)
        if not bas:
            continue
        resim = re.search(r'<img[^>]+src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Yozgat Bozok Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(urllib.parse.urljoin(BOZOK, resim[1]), safe=":/%") if resim else None,
            "url": urllib.parse.urljoin(BOZOK, link[1]),
        }


# 2) Yozgat Belediyesi — etkinlik sitesi, ana sayfa slaytları ("21 Ağustos 2025 - 20:00")
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="swiper-slide">')[1:]:
        link = re.search(r'href="(https://etkinlik\.yozgat\.bel\.tr/etkinlikler/[^"]+)"', blok)
        zaman = re.search(r"bi-calendar2-week\"></i>\s*([^<]+)<", blok)
        baslik = re.search(r"<h2>(.*?)</h2>", blok, re.S)
        if not (link and zaman and baslik):
            continue
        bas, _ = ortak.tarih_bul(zaman[1], bugun)
        yer = re.search(r"bi-pin-map\"></i>\s*([^<]+)<", blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(zaman[1]),
            "mekan": ortak.temizle(yer[1]) if yer else None,
            "ilce": "Merkez",
            "gorsel": resim[1] if resim else None,
            "url": link[1],
        }


KAYNAKLAR = [
    {"ad": "Yozgat Bozok Üniversitesi", "tur": "universite", "url": "https://www.bozok.edu.tr/", "cek": bozok},
    {"ad": "Yozgat Belediyesi", "tur": "belediye", "url": "https://etkinlik.yozgat.bel.tr/", "cek": belediye},
    {"ad": "Yozgat İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://yozgat.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Yozgat", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/yozgat", "cek": etkinlik_io,
     "sehir": "Yozgat", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Yozgat Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.yozgat.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Sorgun, Yerköy, Boğazlıyan belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Sürmeli Şenlikleri, Çamlık Şenlikleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
