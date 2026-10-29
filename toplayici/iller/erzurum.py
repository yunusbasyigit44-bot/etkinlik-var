"""Erzurum kaynakları (plaka 25). Kaynak haritası: 2026-10-29.

Atatürk Üniversitesi (kendi takvim eklentisinin JSON ucu) ve Erzurum Teknik Üniversitesi (HTML kartlar) çalışıyor.
Erzurum'da Devlet Tiyatroları sahnesi var; kaynak listede. Büyükşehir belediyesinde etkinlik takvimi bulunamadı,
Palandöken Belediyesi'nin etkinlik sayfası 2021'den kalma.
"""
import datetime as dt
import html
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Yakutiye", "Palandöken", "Aziziye", "Aşkale", "Çat", "Hınıs", "Horasan", "İspir", "Karaçoban", "Karayazı",
           "Köprüköy", "Narman", "Oltu", "Olur", "Pasinler", "Pazaryolu", "Şenkaya", "Tekman", "Tortum", "Uzundere"]
SALON_ILCE = {"atatürk üniversitesi": "Yakutiye", "atauni": "Yakutiye", "15 temmuz milli irade": "Yakutiye",
              "teknik üniversite": "Yakutiye", "kongre": "Yakutiye", "devlet tiyatro": "Yakutiye", "erzurum teknik": "Yakutiye",
              "kayak": "Palandöken", "kültür sanat merkezi": "Yakutiye", "tarihi çifte": "Yakutiye"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Atatürk Üniversitesi — takvim eklentisinin JSON ucu (ay ay)
# ------------------------------------------------------------------
def atauni(kaynak, bugun):
    y, a = bugun.year, bugun.month
    for _ in range(3):                      # bu ay + sonraki 2 ay
        veri = json.loads(ortak.indir(f"https://atauni.edu.tr/wp-json/event-calendar-evo/v1/events?month={a}&year={y}"))
        for gun in (veri.get("days") or {}).values():
            for e in gun:
                try:
                    tarih = dt.date.fromisoformat(e["date"])
                except (KeyError, ValueError):
                    continue
                if not (tarih.year == y and tarih.month == a):
                    continue
                mekan = ortak.temizle(e.get("loc") or "") or "Atatürk Üniversitesi"
                ad = basliklar(ortak.temizle(e["title"]))
                yield {
                    "baslik": ad,
                    "tarih": tarih,
                    "saat": e.get("time") or None,
                    "mekan": mekan,
                    "ilce": salon_ilce(mekan, "Yakutiye"),
                    "kategori": ortak.kategori_tahmin(ad + " " + (e.get("cat_name") or "")),
                    "gorsel": e.get("thumb") or None,
                    "url": e.get("link"),
                }
        y, a = (y + 1, 1) if a == 12 else (y, a + 1)


# ------------------------------------------------------------------
# 2) Erzurum Teknik Üniversitesi — ana sayfadaki etkinlik kartları (HTML)
# ------------------------------------------------------------------
def etu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for link, icerik in re.findall(r'<a [^>]*href="(/etkinlik/[^"]+)"[^>]*>(.*?)</a>', sayfa, re.S):
        if link in goruldu:
            continue
        zaman = re.search(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})', icerik)
        alt = re.search(r'alt="Etkinlik görseli:\s*([^"]+)"', html.unescape(icerik))
        resim = re.search(r'<img[^>]*src="([^"]+)"', icerik)
        if not (zaman and alt):
            continue
        goruldu.add(link)
        r = resim[1].replace("&amp;", "&") if resim else None
        if r and r.startswith("/"):
            r = "https://erzurum.edu.tr" + r
        yield {
            "baslik": basliklar(ortak.temizle(alt[1])),
            "tarih": dt.date.fromisoformat(zaman[1]),
            "mekan": "Erzurum Teknik Üniversitesi",
            "ilce": "Yakutiye",
            "gorsel": r,
            "url": "https://erzurum.edu.tr" + link,
        }


KAYNAKLAR = [
    {"ad": "Atatürk Üniversitesi", "tur": "universite", "url": "https://atauni.edu.tr/tum-etkinlikler/", "cek": atauni},
    {"ad": "Erzurum Teknik Üniversitesi", "tur": "universite", "url": "https://erzurum.edu.tr/", "cek": etu},
    {"ad": "Erzurum İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://erzurum.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Erzurum", "ilce_bul": salon_ilce, "varsayilan_ilce": "Yakutiye"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/erzurum", "cek": etkinlik_io,
     "sehir": "Erzurum", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Erzurum Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.erzurum.bel.tr",
     "not": "etkinlik takvimi sayfası bulunamadı; kültür hizmetleri sayfası sabit bilgi"},
    {"ad": "Palandöken Belediyesi", "tur": "belediye", "ilce": "Palandöken", "url": "https://www.palandoken.bel.tr/etkinlikler",
     "not": "etkinlik sayfası güncel değil (kayıtlar 2021)"},
    {"ad": "Yakutiye ve Aziziye belediyeleri", "tur": "belediye", "url": "https://www.yakutiye.bel.tr",
     "not": "etkinlik takvimi yok; sadece haberler"},
    {"ad": "Erzurum Valiliği ve 19 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.erzurum.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://erzurum.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://erzurum.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık etkinlikler (Kış Festivali, Palandöken kayak yarışları, Uluslararası Kış Oyunları…)", "tur": "diger",
     "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
