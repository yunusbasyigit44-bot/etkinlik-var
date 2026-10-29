"""Tekirdağ kaynakları (plaka 59, büyükşehir). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Tekirdağ Büyükşehir Belediyesi etkinlik sayfası (aylara göre kartlar), Tekirdağ Namık Kemal Üniversitesi
etkinlik ajandası (bhi.nku.edu.tr). Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Süleymanpaşa", "Çerkezköy", "Çorlu", "Ergene", "Hayrabolu", "Kapaklı", "Malkara", "Marmaraereğlisi", "Muratlı",
           "Saray", "Şarköy"]
SALON_ILCE = {"yılmaz içöz": "Süleymanpaşa", "sahil dolgu": "Süleymanpaşa", "namık kemal üniversitesi": "Süleymanpaşa",
              "nku": "Süleymanpaşa", "rektörlük": "Süleymanpaşa", "rakoczi": "Süleymanpaşa"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

AYLAR_EN = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12}
AYLAR_TR = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
            "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12}


# ------------------------------------------------------------------
# 1) Tekirdağ Büyükşehir Belediyesi — aylık kartlar; geçmiş olanlar "past-event" sınıfını taşır
# ------------------------------------------------------------------
def buyuksehir(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="event-card')[1:]:
        if "past-event" in blok[:30]:
            continue
        ad = re.search(r"<h4>(.*?)</h4>", blok, re.S)
        tarih = re.search(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", blok)
        if not (ad and tarih) or tarih[2].lower() not in AYLAR_EN:
            continue
        yer = re.search(r"fa-map-marker-alt\"></i>\s*<span>(.*?)</span>", blok, re.S)
        resim = re.search(r'<img src="([^"]+)"', blok)
        mekan = ortak.temizle(yer[1]) if yer else None
        yield {
            "baslik": basliklar(ortak.temizle(html.unescape(ad[1]))),
            "tarih": dt.date(int(tarih[3]), AYLAR_EN[tarih[2].lower()], int(tarih[1])),
            "mekan": basliklar(mekan) if mekan else None,
            "ilce": salon_ilce(mekan or "", "Süleymanpaşa"),
            "gorsel": resim[1] if resim else None,
            "url": kaynak["url"],
            "ucretsiz": True,
        }


# ------------------------------------------------------------------
# 2) Namık Kemal Üniversitesi — ajanda (gün başlığı + liste); yıl bugünden çıkarılır
# ------------------------------------------------------------------
def nku(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for gun in sayfa.split('<div class="ajanda-gun">')[1:]:
        t = re.search(r"<b>(\d{1,2})</b>\s*<span>([^<]+)</span>", gun)
        ay = AYLAR_TR.get(ortak.kucuk(t[2]).strip()) if t else None
        if not ay:
            continue
        yil = bugun.year + (1 if ay < bugun.month - 6 else 0)
        try:
            tarih = dt.date(yil, ay, int(t[1]))
        except ValueError:
            continue
        for li in gun.split("<li")[1:]:
            ad = re.search(r"<strong>(.*?)</strong>", li, re.S)
            link = re.search(r'<a href="([^"]+)"', li)
            if not ad:
                continue
            saat = re.search(r"ajanda-saat\">\s*(\d{1,2}:\d{2})", li)
            yer = re.search(r"</svg>\s*([^<]+?)\s*(?:<|$)", li)
            baslik = basliklar(ortak.temizle(html.unescape(ad[1])))
            mekan = (ortak.temizle(yer[1]) if yer else "").strip(" ·")
            if not mekan or mekan in ("Diğer", "Online"):
                mekan = "Tekirdağ Namık Kemal Üniversitesi"
            yield {
                "baslik": baslik,
                "tarih": tarih,
                "saat": saat[1] if saat else None,
                "mekan": mekan,
                "ilce": salon_ilce(mekan, "Süleymanpaşa"),
                "kategori": ortak.kategori_tahmin(baslik),
                "url": link[1] if link else kaynak["url"],
            }


KAYNAKLAR = [
    {"ad": "Tekirdağ Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.tekirdag.bel.tr/etkinlikler", "cek": buyuksehir},
    {"ad": "Tekirdağ Namık Kemal Üniversitesi", "tur": "universite", "url": "https://bhi.nku.edu.tr/etkinlik", "cek": nku},
    {"ad": "Tekirdağ İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://tekirdag.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Tekirdağ", "ilce_bul": salon_ilce, "varsayilan_ilce": "Süleymanpaşa"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/tekirdag", "cek": etkinlik_io,
     "sehir": "Tekirdağ", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Süleymanpaşa, Çorlu, Çerkezköy, Kapaklı belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Tekirdağ Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.tekirdag.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Tekirdağ Kiraz, Şarköy, Rakı Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
