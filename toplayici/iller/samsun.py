"""Samsun kaynakları (plaka 55). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Samsun Devlet Opera ve Balesi (sitenin program verisi, anahtarsız genel uç), Ondokuz Mayıs Üniversitesi
etkinlik takvimi. Samsun Büyükşehir sayfasında etkinlikler haber biçiminde (tarihsiz) ve aylık takvim sayfası hata veriyor.
Devlet Tiyatroları programında Samsun sahnesi yok; kaynak listede duruyor.
"""
import datetime as dt
import html
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Atakum", "Canik", "İlkadım", "Tekkeköy", "Alaçam", "Asarcık", "Ayvacık", "Bafra", "Çarşamba", "Havza", "Kavak",
           "Ladik", "19 Mayıs", "Salıpazarı", "Terme", "Vezirköprü", "Yakakent"]
SALON_ILCE = {"aydın gün": "İlkadım", "zehra yıldız": "İlkadım", "ondokuz mayıs üniversitesi": "Atakum", "omü": "Atakum",
              "kurupelit": "Atakum", "devlet opera": "İlkadım"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Samsun Devlet Opera ve Balesi — sitenin program verisi (JSON)
# ------------------------------------------------------------------
def opera(kaynak, bugun):
    for p in json.loads(ortak.indir(kaynak["url"])):
        try:
            gun = dt.datetime.fromisoformat(p["oyunTarihi"])
        except (KeyError, ValueError):
            continue
        ad = basliklar(ortak.temizle(p.get("eserAdi") or ""))
        if not ad:
            continue
        mekan = basliklar(p.get("sahneAdi") or "Samsun Devlet Opera ve Balesi")
        afis = (p.get("afisler") or [None])[0]
        gorsel = None
        if afis:
            try:
                gorsel = ortak.gorsel_sakla(afis, "dob-samsun-%s" % p.get("eserKodu"))   # afiş linkleri süreli; indirip sakla
            except Exception as hata:
                print("   afiş alınamadı:", ad, hata)
        saat = (p.get("oyunSaatleri") or [gun.strftime("%H:%M")])[0]
        cocuk = re.search(r"pinokyo|okulumuz|çocuk|masal", ortak.kucuk(ad))
        yield {
            "baslik": ad,
            "tarih": gun.date(),
            "saat": saat,
            "mekan": "Samsun Devlet Opera ve Balesi · " + mekan,
            "ilce": "İlkadım",
            "kategori": "Çocuk" if cocuk else "Tiyatro",
            "ucretsiz": False,
            "gorsel": gorsel,
            "url": p.get("seoFullUrl") or "https://www.operabale.gov.tr/directorates/samsun-opera-ve-balesi-6",
            "ozet": "Devlet Opera ve Balesi",
        }


# ------------------------------------------------------------------
# 2) Ondokuz Mayıs Üniversitesi — etkinlik takvimi (HTML, tarih ISO biçiminde)
# ------------------------------------------------------------------
OMU = "https://www.omu.edu.tr"


def omu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<li class="ht-layout')[1:]:
        baslik = re.search(r'ht-heading-title-text"><a href="([^"]+)">(.*?)</a>', blok, re.S)
        zaman = re.search(r'content="(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})', blok)
        if not (baslik and zaman):
            continue
        tur = re.search(r'ht-etkinlikturu">\s*<a[^>]*>(.*?)</a>', blok, re.S)
        resim = re.search(r'<img[^>]+src="([^"?]+)', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[2])))
        yield {
            "baslik": ad,
            "tarih": dt.date.fromisoformat(zaman[1]),
            "saat": None if zaman[2] == "00:00" else zaman[2],
            "mekan": "Ondokuz Mayıs Üniversitesi",
            "ilce": "Atakum",
            "kategori": ortak.kategori_tahmin(ad + " " + (ortak.temizle(tur[1]) if tur else "")),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin(OMU + "/", baslik[1]),
            "ozet": ortak.temizle(tur[1]) if tur else None,
        }


KAYNAKLAR = [
    {"ad": "Samsun Devlet Opera ve Balesi", "tur": "kultur", "url": "https://apimain.operabale.gov.tr/v1/web/temsil/mudurluk/listele/6",
     "cek": opera},
    {"ad": "Ondokuz Mayıs Üniversitesi", "tur": "universite", "url": OMU + "/tr/etkinlikler", "cek": omu},
    {"ad": "Samsun İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://samsun.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Samsun", "ilce_bul": salon_ilce, "varsayilan_ilce": "İlkadım"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/samsun", "cek": etkinlik_io,
     "sehir": "Samsun", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Samsun Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.samsun.bel.tr/guncel/etkinlikler",
     "not": "etkinlikler haber biçiminde, tarihsiz; aylık 'Kültür Sanat Sezonu' takvim sayfası hata veriyor (500)"},
    {"ad": "Samsun Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Samsun Kültür Turizm portalı", "tur": "belediye", "url": "https://samsunkulturturizm.com/",
     "not": "bağlantıyı kapatıyor — okunamıyor"},
    {"ad": "Canik, İlkadım, Atakum, Tekkeköy belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Samsun Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.samsun.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Samsun Kültür Yolu, Uluslararası Samsun Tiyatro, Bafra Balık…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
