"""Kahramanmaraş kaynakları (plaka 46). Kaynak haritası: 2026-10-29.

Okunan kaynak: Kahramanmaraş Sütçü İmam Üniversitesi ana sayfasındaki "Yaklaşan Etkinlikler".
Büyükşehir Belediyesi'nin etkinlik sayfası var ama şu an "Etkinlik bulunamadı" diyor; Onikişubat
Belediyesi'nin de etkinlik sayfası boş. İkisi de listede duruyor (boşluk dolarsa okuyucu yazılır).
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Afşin", "Andırın", "Çağlayancerit", "Dulkadiroğlu", "Ekinözü", "Elbistan", "Göksun", "Nurhak", "Onikişubat",
           "Pazarcık", "Türkoğlu"]
SALON_ILCE = {"ksü": "Onikişubat", "sütçü imam": "Onikişubat", "avşar": "Onikişubat", "yunus emre kongre": "Onikişubat",
              "kongre ve kültür": "Onikişubat", "maraş kültür": "Dulkadiroğlu", "kahramanmaraş kültür": "Dulkadiroğlu"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KSU = "https://www.ksu.edu.tr/"


# ------------------------------------------------------------------
# 1) Kahramanmaraş Sütçü İmam Üniversitesi — ana sayfa "Yaklaşan Etkinlikler" (HTML)
# ------------------------------------------------------------------
def ksu(kaynak, bugun):
    sayfa = ortak.indir(KSU)
    bolum = sayfa.split("Yaklaşan Etkinlikler", 1)
    if len(bolum) < 2:
        return
    for blok in bolum[1].split('<div style="margin: 0 15px 25px 15px;">')[1:]:
        link = re.search(r"<a href='([^']+)'", blok)
        baslik = re.search(r'class="title[^"]*">(.*?)</p>', blok, re.S)

        def alan(ad):
            r = re.search(r"<b>\s*" + ad + r"\s*:\s*</b>\s*([^<]*)<", blok)
            return ortak.temizle(html.unescape(r[1])) if r else ""

        bas, bit = ortak.tarih_bul(alan("Tarih"), bugun)
        if not (baslik and bas):
            continue
        resim = re.search(r'<img src="([^"]+)"', blok)
        yer = alan("Yer") or "Kahramanmaraş Sütçü İmam Üniversitesi"
        if " / " in yer or ortak.baska_il_mi(yer, "Kahramanmaraş"):
            continue                       # ör. "Almanya / Stuttgart" — Kahramanmaraş'ta değil
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(alan("Saat")),
            "mekan": yer,
            "ilce": salon_ilce(yer, "Onikişubat"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.urljoin(KSU, urllib.parse.quote(resim[1], safe=":/%")) if resim else None,
            "url": urllib.parse.urljoin(KSU, link[1]) if link else KSU,
            "ozet": alan("Düzenleyen") or None,
        }


KAYNAKLAR = [
    {"ad": "Kahramanmaraş Sütçü İmam Üniversitesi", "tur": "universite", "ilce": "Onikişubat", "url": KSU, "cek": ksu},
    {"ad": "Kahramanmaraş İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kahramanmaras.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kahramanmaraş", "ilce_bul": salon_ilce, "varsayilan_ilce": "Dulkadiroğlu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kahramanmaras", "cek": etkinlik_io,
     "sehir": "Kahramanmaraş", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kahramanmaraş Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.kahramanmaras.bel.tr/etkinlik",
     "not": "etkinlik sayfası var ama şu an boş ('Etkinlik bulunamadı'); dolunca okunacak"},
    {"ad": "Onikişubat Belediyesi", "tur": "belediye", "ilce": "Onikişubat", "url": "https://www.onikisubat.bel.tr/Etkinlikler",
     "not": "etkinlik sayfası var ama şu an boş"},
    {"ad": "Dulkadiroğlu Belediyesi", "tur": "belediye", "ilce": "Dulkadiroğlu", "url": "https://www.dulkadiroglu.bel.tr/sosyal-ve-kulturel",
     "not": "etkinlik takvimi yok; sadece haber"},
    {"ad": "Kahramanmaraş İstiklal Üniversitesi", "tur": "universite", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Kahramanmaraş Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kahramanmaras.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Kahramanmaraş Edebiyat Şehri etkinlikleri, Dondurma / Tarhana festivalleri…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
