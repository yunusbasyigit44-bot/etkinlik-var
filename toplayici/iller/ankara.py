"""Ankara kaynakları (plaka 06). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Hacettepe Üniversitesi etkinlik sitesi, Çankaya Belediyesi (ana sayfadaki kültür-sanat kartları),
Ankara Büyükşehir Belediyesi etkinlik listesi (şu an arşiv gibi duruyor; yeni kayıt girince gelir).
Ankara'da Devlet Tiyatroları sahneleri var.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_opera, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akyurt", "Altındağ", "Ayaş", "Balâ", "Beypazarı", "Çamlıdere", "Çankaya", "Çubuk", "Elmadağ", "Etimesgut",
           "Evren", "Gölbaşı", "Güdül", "Haymana", "Kahramankazan", "Kalecik", "Keçiören", "Kızılcahamam", "Mamak",
           "Nallıhan", "Polatlı", "Pursaklar", "Sincan", "Şereflikoçhisar", "Yenimahalle"]
SALON_ILCE = {"hacettepe": "Çankaya", "gençlik parkı": "Altındağ", "göksu": "Etimesgut", "koru": "Çankaya",
              "odtü": "Çankaya", "bilkent": "Çankaya", "cso": "Çankaya", "cer modern": "Altındağ", "çankaya": "Çankaya",
              "beytepe": "Çankaya", "sıhhiye": "Çankaya", "ostim": "Yenimahalle", "atatürk kültür merkezi": "Çankaya"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Hacettepe Üniversitesi — etkinlik sitesi (HTML kartlar)
# ------------------------------------------------------------------
def hacettepe(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="haber_card h-100">')[1:]:
        baslik = re.search(r'haber_card_baslik">(.*?)</div>', blok, re.S)
        link = re.search(r'<a href="(/tr/[^"]+)">Devamı', blok)
        alt = re.search(r'haber_alt">(.*?)</div>', blok, re.S)
        if not (baslik and alt):
            continue
        bilgi = ortak.temizle(alt[1])
        bas, _ = ortak.tarih_bul(bilgi, bugun)
        tur = bilgi.split("|")[-1].strip() if "|" in bilgi else ""
        resim = re.search(r"url\(([^)]+)\)", blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(bilgi),
            "mekan": "Hacettepe Üniversitesi",
            "ilce": "Çankaya",
            "kategori": ortak.kategori_tahmin(ad + " " + tur),
            "gorsel": resim[1].replace(" ", "%20") if resim else None,
            "url": urllib.parse.urljoin("https://etkinlikler.hacettepe.edu.tr/", link[1]) if link else kaynak["url"],
        }


# ------------------------------------------------------------------
# 2) Çankaya Belediyesi — ana sayfadaki "Kültür Sanat Etkinlikleri" kartları
# ------------------------------------------------------------------
def cankaya(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for link, blok in re.findall(r'<a\s+href="(https://www\.cankaya\.bel\.tr/kultur-sanat/[^"]+)"\s+class="etkinlik-card(.*?)</a>', sayfa, re.S):
        baslik = re.search(r"<h3[^>]*>(.*?)</h3>", blok, re.S)
        tarih = re.search(r"(\d{2}\.\d{2}\.\d{4})", blok)
        resim = re.search(r'<img\s+src="([^"]+)"', blok)
        if not (baslik and tarih):
            continue
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": "Çankaya Belediyesi",
            "ilce": "Çankaya",
            "gorsel": resim[1] if resim else None,
            "url": link,
        }


# ------------------------------------------------------------------
# 3) Ankara Büyükşehir Belediyesi — etkinlik listesi (HTML kartlar)
# ------------------------------------------------------------------
def abb(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for link, blok in re.findall(r'<a href="(/etkinlik/[^"]+)"[^>]*class="event-list-item(.*?)</a>', sayfa, re.S):
        baslik = re.search(r"<strong>(.*?)</strong>", blok, re.S)
        spans = re.findall(r"<span>(.*?)</span>", blok, re.S)
        tur = re.search(r'class="category">(.*?)</span>', blok, re.S)
        resim = re.search(r'<img src="([^"]+)"', blok)
        if not baslik or len(spans) < 2:
            continue
        bas, _ = ortak.tarih_bul(spans[0], bugun)
        mekan = ortak.temizle(spans[1])
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(spans[0]),
            "mekan": basliklar(mekan) if len(mekan) < 90 else mekan[:90],
            "ilce": salon_ilce(mekan, "Çankaya"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": resim[1] if resim else None,
            "url": "https://www.ankara.bel.tr" + link,
        }


KAYNAKLAR = [
    {"ad": "Devlet Opera ve Balesi", "tur": "kultur", "url": "https://www.operabale.gov.tr", "cek": devlet_opera,
     "mudurluk": 1, "ilce_bul": salon_ilce, "varsayilan_ilce": "Çankaya"},
    {"ad": "Hacettepe Üniversitesi", "tur": "universite", "url": "https://etkinlikler.hacettepe.edu.tr/", "cek": hacettepe},
    {"ad": "Çankaya Belediyesi", "tur": "belediye", "ilce": "Çankaya", "url": "https://www.cankaya.bel.tr", "cek": cankaya},
    {"ad": "Ankara Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.ankara.bel.tr/etkinlikler", "cek": abb},
    {"ad": "Ankara İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://ankara.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Ankara", "ilce_bul": salon_ilce, "varsayilan_ilce": "Çankaya"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/ankara", "cek": etkinlik_io,
     "sehir": "Ankara", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / okunamayan kaynaklar (eksikler) ---
    {"ad": "Ankara Kültür Sanat (ABB kültür etkinlikleri)", "tur": "belediye", "url": "https://kultursanat.ankara.bel.tr/event",
     "not": "liste şu an Eylül 2026'da kalmış; ABB etkinlik listesi okunuyor"},
    {"ad": "Ankara Üniversitesi", "tur": "universite", "url": "https://www.ankara.edu.tr", "not": "ana sayfada etkinlik takvimi okunamadı"},
    {"ad": "ODTÜ, Bilkent, Gazi, Ankara Bilim, Hacı Bayram Veli üniversiteleri", "tur": "universite", "url": None,
     "not": "düzenli okunabilir bir etkinlik sayfası bulunamadı"},
    {"ad": "Yenimahalle, Keçiören, Mamak, Etimesgut, Altındağ belediyeleri", "tur": "belediye", "url": None,
     "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Ankara Valiliği", "tur": "valilik", "url": "https://www.ankara.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "25 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok / bot koruması"},
    {"ad": "Yıllık festivaller (Beypazarı Havuç, Kalecik Karası, Ankara Film Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
