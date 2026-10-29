"""Online etkinlikler (webinar, çevrim içi seminer/atölye, canlı yayın) — tüm Türkiye. Kaynak haritası: 2026-10-29.

Okunan kaynak: Google Developer Groups (GDG) Türkiye toplulukları — gdg.community.dev herkese açık topluluk sayfaları ve
etkinlik sayfalarındaki schema.org (JSON-LD) verisi. Sadece "OnlineEventAttendanceMode" olan (tamamen çevrim içi)
etkinlikler alınır. robots.txt'te yasaklanan /api/ yolu KULLANILMAZ; sitenin istenen bekleme süresine (2 sn) uyulur.

Denenip bağlanamayanlar "not" ile listede: Kommunity, TÜBA, KOSGEB, TÜBİTAK, Türk Omurga Derneği, Anadolu Üniversitesi vb.
"""
import datetime as dt
import html
import json
import re
import time

import ortak
from ortak_kaynaklar import basliklar

ILCELER = []
TUM_TURKIYE = True

GDG = "https://gdg.community.dev"
# Türkiye'deki GDG toplulukları (sayfasında "Türkiye" geçenler). Her topluluk sayfası yaklaşan etkinliklerine bağlantı verir.
GDG_TOPLULUKLAR = ["gdg-istanbul", "gdg-ankara", "gdg-izmir", "gdg-cloud-istanbul", "gdg-cloud-ankara", "gdg-bursa",
                   "gdg-eskisehir", "gdg-antalya"]


def _gdg_etkinlik(url, bugun):
    sayfa = ortak.indir(url)
    time.sleep(1)                                    # gdg.community.dev Crawl-delay: 2
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', sayfa, re.S)
    if not ld:
        return None
    try:
        veri = json.loads(ld[1])
    except ValueError:
        return None
    if not isinstance(veri, dict) or not str(veri.get("eventAttendanceMode", "")).endswith("/OnlineEventAttendanceMode"):
        return None
    if "Cancelled" in str(veri.get("eventStatus", "")):
        return None
    bas = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?", veri.get("startDate") or "")
    if not bas:
        return None
    tarih = dt.date(int(bas[1]), int(bas[2]), int(bas[3]))
    if tarih < bugun:
        return None
    bit = re.match(r"(\d{4})-(\d{2})-(\d{2})", veri.get("endDate") or "")
    bitis = dt.date(int(bit[1]), int(bit[2]), int(bit[3])) if bit else None
    resim = veri.get("image")
    if isinstance(resim, list):
        resim = resim[0] if resim else None
    ozet = ortak.temizle(veri.get("description") or "")
    return {
        "baslik": basliklar(ortak.temizle(html.unescape(veri.get("name") or ""))),
        "tarih": tarih,
        "bitis": bitis if bitis and bitis > tarih else None,
        "saat": f"{bas[4]}:{bas[5]}" if bas[4] and f"{bas[4]}:{bas[5]}" != "00:00" else None,
        "mekan": "Online",
        "ilce": None,
        "kategori": ortak.kategori_tahmin(veri.get("name") or ""),
        "gorsel": resim if isinstance(resim, str) and resim.startswith("http") else None,
        "url": url,
        "ozet": ozet[:240] if ozet else None,
    }


def gdg(kaynak, bugun):
    linkler = []
    for topluluk in GDG_TOPLULUKLAR:
        try:
            sayfa = ortak.indir(f"{GDG}/{topluluk}/")
        except Exception:
            continue                                  # tek topluluk açılmazsa diğerleri okunsun
        time.sleep(1)
        for yol in re.findall(r'(?:https://gdg\.community\.dev)?/?(events/details/[A-Za-z0-9._~%-]+)', sayfa):
            adres = f"{GDG}/{yol}/"
            if adres not in linkler:
                linkler.append(adres)
    for adres in linkler:
        try:
            e = _gdg_etkinlik(adres, bugun)
        except Exception:
            continue
        if e and e["baslik"]:
            yield e


KAYNAKLAR = [
    {"ad": "Google Developer Groups Türkiye (çevrim içi etkinlikler)", "tur": "topluluk", "url": GDG + "/", "cek": gdg},
    # --- Denenip bağlanamayan kaynaklar ---
    {"ad": "Kommunity (topluluk platformu)", "tur": "topluluk", "url": "https://kommunity.com/events",
     "not": "sayfa tarayıcıda (JS) çiziliyor; herkese açık veri ucu yok"},
    {"ad": "TÜBA, Bilim Akademisi", "tur": "kamu", "url": "https://www.tuba.gov.tr",
     "not": "etkinlik takvimi sayfası bulunamadı / çevrim içi program yok"},
    {"ad": "KOSGEB çevrim içi eğitimler", "tur": "kamu", "url": "https://lms.kosgeb.gov.tr",
     "not": "eğitimler giriş (üyelik) gerektiren öğrenme sisteminde; okunmuyor"},
    {"ad": "TÜBİTAK etkinlikleri", "tur": "kamu", "url": "https://www.tubitak.gov.tr/tr/etkinlikler",
     "not": "listedeki etkinlikler yüz yüze; çevrim içi ayrımı yok"},
    {"ad": "Türk Omurga Derneği webinarları", "tur": "stk", "url": "https://turkomurga.org.tr/turkomurga/webinarlar",
     "not": "güncel program yayımlanmamış (son program 2023-2024)"},
    {"ad": "Üniversite webinar sayfaları (iCal)", "tur": "universite", "url": None,
     "not": "denenen büyük üniversitelerde herkese açık iCal akışı yok; Anadolu Ü. listesinde çevrim içi ayrımı yok"},
    {"ad": "Kariyer Kapısı, SALT, TOBB/kalkınma ajansları", "tur": "kamu", "url": None,
     "not": "siteye ulaşılamadı / etkinlik takvimi okunamadı (sonraki tur)"},
]
