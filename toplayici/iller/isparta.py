"""Isparta kaynakları (plaka 32). Kaynak haritası: 2026-10-29.

Okunan: Isparta Uygulamalı Bilimler Üniversitesi etkinlik merkezi (HTML), Süleyman Demirel Üniversitesi
etkinlik arşivi (sitenin kendi JSON ucu). Belediye sitesinde okunabilir takvim yok. Devlet Tiyatroları sahnesi yok.
"""
import datetime as dt
import html
import json
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Aksu", "Atabey", "Eğirdir", "Gelendost", "Gönen", "Keçiborlu", "Senirkent", "Sütçüler",
           "Şarkikaraağaç", "Uluborlu", "Yalvaç", "Yenişehir"]
SALON_ILCE = {"sdü": "Merkez", "süleyman demirel": "Merkez", "iste": "Merkez", "uygulamalı bilimler": "Merkez",
              "isparta": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Isparta Uygulamalı Bilimler Üniversitesi — etkinlik merkezi (HTML, tarih GG/AA/YYYY)
# ------------------------------------------------------------------
def iste(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="border border-gray border-only-bottom')[1:]:
        link = re.search(r'<a href="(https://www\.iste\.edu\.tr/etkinlik-merkezi/[^"}]+)', blok)
        tarih = re.search(r"(\d{2})/(\d{2})/(\d{4})", blok)
        baslik = re.search(r"<h3[^>]*>(.*?)</h3>", blok, re.S)
        if not (link and tarih and baslik):
            continue
        resim = re.search(r'<img src="([^"]+)"', blok)
        try:
            gun = dt.date(int(tarih[3]), int(tarih[2]), int(tarih[1]))
        except ValueError:
            continue
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        yield {
            "baslik": ad,
            "tarih": gun,
            "mekan": "Isparta Uygulamalı Bilimler Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": link[1],
        }


def _baslik(ad):
    """TAMAMI BÜYÜK başlıkta İngilizce (ASCII) sözcükler Türkçe i/ı kuralına sokulmaz."""
    if ad != ad.upper():
        return ad
    return " ".join(k.capitalize() if k.isascii() else basliklar(k) for k in ad.split())


# ------------------------------------------------------------------
# 2) Süleyman Demirel Üniversitesi — etkinlik arşivi sayfasının kullandığı JSON ucu
# ------------------------------------------------------------------
ATLA_TUR = ("ders", "gezi", "webinar")


def sdu(kaynak, bugun):
    gorulen = set()
    for atla in (0, 12, 24):
        veri = json.loads(ortak.indir(f"https://www.sdu.edu.tr/Etkinlik/GetEtkinliklerAsync?SkipCount={atla}&BaslangicTarihi={bugun.isoformat()}", 60))
        for e in veri.get("data", []):
            if e["etkinlikGuid"] in gorulen:
                continue
            gorulen.add(e["etkinlikGuid"])
            tur = e.get("etkinlikTurAdi") or ""
            if any(x in ortak.kucuk(tur) for x in ATLA_TUR):
                continue
            t = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", e.get("tarih") or "")
            if not t:
                continue
            yer = ortak.temizle(e.get("yapilacagiYer") or "") or "Süleyman Demirel Üniversitesi"
            if ortak.baska_il_mi(yer, "Isparta"):
                continue
            ad = _baslik(ortak.temizle(e["adi"]))
            if "ameliyat günü" in ortak.kucuk(ad) or "cerrahi günü" in ortak.kucuk(ad):
                continue                   # hastane içi eğitim programı
            afis = e.get("afisUrl")
            yield {
                "baslik": ad,
                "tarih": dt.date(int(t[3]), int(t[2]), int(t[1])),
                "mekan": yer,
                "ilce": salon_ilce(yer, "Merkez"),
                "kategori": ortak.kategori_tahmin(ad + " " + tur),
                "gorsel": afis if afis and not e.get("isVarsayilanAfis") else None,
                "url": e.get("link") or "https://www.sdu.edu.tr/Etkinlik/Arsiv",
                "ozet": tur or None,
            }
        if len(veri.get("data", [])) < 12:
            break


KAYNAKLAR = [
    {"ad": "Isparta Uygulamalı Bilimler Üniversitesi", "tur": "universite", "url": "https://www.iste.edu.tr/etkinlik-merkezi", "cek": iste},
    {"ad": "Süleyman Demirel Üniversitesi", "tur": "universite", "url": "https://www.sdu.edu.tr/Etkinlik/Arsiv", "cek": sdu},
    {"ad": "Isparta İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://isparta.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/isparta", "cek": etkinlik_io,
     "sehir": "Isparta", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Isparta Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://isparta.bel.tr/sosyal-ve-kulturel-etkinlikler",
     "not": "sayfa genel bilgi içeriyor; tarihli etkinlik takvimi yok"},
    {"ad": "Isparta Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.isparta.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Eğirdir, Yalvaç, Şarkikaraağaç belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "not": "Isparta'da sahne yok"},
    {"ad": "Yıllık festivaller (Gül Festivali, Eğirdir Elma, Yalvaç Antiocheia…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
