"""Bursa kaynakları (plaka 16). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Bursa Teknik Üniversitesi etkinlik listesi, Bursa Büyükşehir Belediyesi ana sayfa etkinlik bölümü
(sergiler/programlar), Nilüfer Belediyesi etkinlik takvimi. Devlet Tiyatroları Bursa sahnesi ayrıca izlenir.
Büyükşehir Şehir Tiyatrosu için okunabilir bir takvim bulunamadı.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Büyükorhan", "Gemlik", "Gürsu", "Harmancık", "İnegöl", "İznik", "Karacabey", "Keles", "Kestel", "Mudanya",
           "Mustafakemalpaşa", "Nilüfer", "Orhaneli", "Orhangazi", "Osmangazi", "Yenişehir", "Yıldırım"]
SALON_ILCE = {"mimar sinan": "Yıldırım", "yıldırım bayezid": "Yıldırım", "btü": "Yıldırım", "merinos": "Osmangazi",
              "teleferik": "Osmangazi", "hünkar": "Osmangazi", "kültürpark": "Osmangazi", "tophane": "Osmangazi",
              "tayyare": "Osmangazi", "santral": "Osmangazi", "konak sinema": "Nilüfer", "bursa devlet": "Osmangazi",
              "kent müzesi": "Osmangazi", "uludağ üniversitesi": "Nilüfer", "bursa kültür sanat": "Osmangazi",
              "ulu cami": "Osmangazi", "heykel": "Osmangazi"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


def _tr_tarih(metin):
    r = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", metin or "")
    try:
        return dt.date(int(r[3]), int(r[2]), int(r[1])) if r else None
    except ValueError:
        return None


# ------------------------------------------------------------------
# 1) Bursa Teknik Üniversitesi — etkinlik listesi (HTML)
# ------------------------------------------------------------------
def btu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for link, icerik in re.findall(r'<li>\s*<a href="(https://btu\.edu\.tr/tr/etkinlik/detay/[^"]+)">(.*?)</a>', sayfa, re.S):
        tarih = _tr_tarih(icerik)
        baslik = re.search(r"<strong>(.*?)</strong>", icerik, re.S)
        if not (tarih and baslik):
            continue
        yer = re.search(r"<i>(.*?)</i>", icerik, re.S)
        saat = re.search(r"<article>(.*?)</article>", icerik, re.S)
        ad = basliklar(ortak.temizle(baslik[1]))
        if "prova" in ortak.kucuk(ad):
            continue                       # kulüp provası halka açık etkinlik değil
        mekan = ortak.temizle(yer[1]) if yer else "Bursa Teknik Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": ortak.saat_bul(ortak.temizle(saat[1])) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Yıldırım"),
            "kategori": ortak.kategori_tahmin(ad),
            "url": urllib.parse.quote(link, safe=":/%"),
        }


# ------------------------------------------------------------------
# 2) Bursa Büyükşehir Belediyesi — ana sayfadaki "Etkinlikler" kutuları (HTML)
# ------------------------------------------------------------------
BB = "https://www.bursa.bel.tr"


def buyuksehir(kaynak, bugun):
    sayfa = ortak.indir(BB)
    bolum = sayfa.split('id="etkinlikler"', 1)
    if len(bolum) < 2:
        return
    for blok in bolum[1].split('<div class="post-item-wrap')[1:]:
        link = re.search(r'href="(/etkinlik/[^"]+)"', blok)
        baslik = re.search(r"<h2><a[^>]*>(.*?)</a></h2>", blok, re.S)
        t = re.search(r'fa-calendar-alt"></i>\s*([^<]+)<', blok)
        if not (link and baslik and t):
            continue
        tarihler = re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", t[1])
        bas = _tr_tarih(tarihler[0]) if tarihler else None
        bit = _tr_tarih(tarihler[-1]) if tarihler else None
        if not bas:
            continue
        tur = re.search(r'fa-theater-masks"></i>\s*([^<]+)<', blok)
        yer = re.search(r'fa-map-marker-alt"></i>\s*([^<]+)<', blok)
        resim = re.search(r'<img[^>]+src="(/storage/[^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = ortak.temizle(yer[1]) if yer else None
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": basliklar(mekan) if mekan else None,
            "ilce": salon_ilce(mekan or "", "Osmangazi"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            # Büyükşehir sitesinin görselleri bu bağlantıdan çok yavaş/açılmıyor; görsel alınmıyor
            "url": BB + link[1],
            "ucretsiz": True,
        }


# ------------------------------------------------------------------
# 3) Nilüfer Belediyesi — etkinlik takvimi (HTML)
# ------------------------------------------------------------------
def nilufer(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div  class="event">')[1:]:
        t = re.search(r"<time[^>]*>([^<]+)</time>", blok)
        a = re.search(r'<h3><a href="([^"]+)">(.*?)</a></h3>', blok, re.S)
        if not (t and a):
            continue
        tarih = _tr_tarih(t[1])
        if not tarih:
            continue
        resim = re.search(r'<img src="([^"]+)"', blok)
        yield {
            "baslik": ortak.temizle(a[2]),
            "tarih": tarih,
            "saat": ortak.saat_bul(t[1].split("|")[-1]),
            "mekan": "Nilüfer",
            "ilce": "Nilüfer",
            "kategori": ortak.kategori_tahmin(ortak.temizle(a[2])),
            "gorsel": resim[1] if resim else None,
            "url": a[1],
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "Bursa Teknik Üniversitesi", "tur": "universite", "url": "https://btu.edu.tr/tr/etkinlik", "cek": btu},
    {"ad": "Bursa Büyükşehir Belediyesi (kültür-sanat, sergiler)", "tur": "belediye", "url": BB, "cek": buyuksehir},
    {"ad": "Nilüfer Belediyesi", "tur": "belediye", "ilce": "Nilüfer", "url": "https://www.nilufer.bel.tr/etkinlikler", "cek": nilufer},
    {"ad": "Bursa İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bursa.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bursa", "ilce_bul": salon_ilce, "varsayilan_ilce": "Osmangazi"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bursa", "cek": etkinlik_io,
     "sehir": "Bursa", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bursa Uludağ Üniversitesi", "tur": "universite", "ilce": "Nilüfer", "url": "https://www.uludag.edu.tr",
     "not": "etkinlik takvimi ana sayfada yok; duyurular idari — okunmuyor"},
    {"ad": "Osmangazi Belediyesi", "tur": "belediye", "ilce": "Osmangazi", "url": "https://www.osmangazi.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama henüz okunmuyor (sonraki tur)"},
    {"ad": "Yıldırım Belediyesi", "tur": "belediye", "ilce": "Yıldırım", "url": "https://www.yildirim.bel.tr",
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Bursa Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": None,
     "not": "oyun takvimi bilet sitesinde; sitenin kendi okunabilir takvimi yok"},
    {"ad": "Bursa Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.bursa.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://bursa.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Gemlik, Mudanya, İnegöl, İznik belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Bursa Uluslararası Festivali, İznik Gölü Festivali, Mudanya Zeytin Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
