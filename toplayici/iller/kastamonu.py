"""Kastamonu kaynakları (plaka 37). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Kastamonu Belediyesi etkinlik takvimi (sayfaya gömülü JSON-LD), Kastamonu Üniversitesi etkinlik listesi.
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import html
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Abana", "Ağlı", "Araç", "Azdavay", "Bozkurt", "Cide", "Çatalzeytin", "Daday", "Devrekani",
           "Doğanyurt", "Hanönü", "İhsangazi", "İnebolu", "Küre", "Pınarbaşı", "Seydiler", "Şenpazar", "Taşköprü", "Tosya"]
SALON_ILCE = {"belediye meydan": "Merkez", "turhan topçuoğlu": "Merkez", "kü ": "Merkez", "kastamonu üniversitesi": "Merkez",
              "merkezi kütüphane": "Merkez", "kastamonu": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

_AYLAR = ["ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]


# ------------------------------------------------------------------
# 1) Kastamonu Belediyesi — etkinlik sayfasındaki schema.org JSON-LD
# ------------------------------------------------------------------
def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in re.findall(r'<script type="application/ld\+json">(.*?)</script>', sayfa, re.S):
        try:
            veri = json.loads(blok)
        except ValueError:
            continue
        for e in veri if isinstance(veri, list) else [veri]:
            if e.get("@type") != "Event" or not e.get("startDate"):
                continue
            bas = dt.datetime.fromisoformat(e["startDate"])
            bit = dt.datetime.fromisoformat(e["endDate"]) if e.get("endDate") else None
            yer = (e.get("location") or {}).get("name") or None
            ad = basliklar(ortak.temizle(html.unescape(e["name"])))
            ozet = ortak.temizle(html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(e.get("description") or ""))))
            yield {
                "baslik": ad,
                "tarih": bas.date(),
                "bitis": bit.date() if bit and bit.date() > bas.date() else None,
                "saat": bas.strftime("%H:%M") if bas.hour else None,
                "mekan": yer,
                "ilce": salon_ilce(yer or "", "Merkez"),
                "kategori": ortak.kategori_tahmin(ad + " " + ozet),
                "gorsel": urllib.parse.quote(e["image"], safe=":/%") if e.get("image") else None,
                "url": e.get("url") or kaynak["url"],
                "ucretsiz": True,
                "ozet": ozet[:240] or None,
            }


# ------------------------------------------------------------------
# 2) Kastamonu Üniversitesi — etkinlik kartları (Next.js sayfası, ay başlıkları altında)
# ------------------------------------------------------------------
KU = "https://kastamonu.edu.tr"


def universite(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    sayfa = sayfa.split("</footer>")[0]
    ogeler = sorted(
        [(m.start(), "ay", m) for m in re.finditer(r'fw-700 c-ct-1">([^<]+?) (\d{4})</h6>', sayfa)]
        + [(m.start(), "kart", m) for m in re.finditer(r'<a class="events-card listed" href="([^"]+)">', sayfa)],
        key=lambda x: x[0])
    yil = bugun.year
    for i, (konum, tur, m) in enumerate(ogeler):
        if tur == "ay":
            yil = int(m[2])
            continue
        son = ogeler[i + 1][0] if i + 1 < len(ogeler) else len(sayfa)
        blok = sayfa[konum:son]
        ay = re.search(r'fs-36 fw-100 c-15">([^<]+)</span><span[^>]*>(\d{1,2})</span>', blok)
        baslik = re.search(r'fs-16 fw-700 c-15">([^<]+)</span>', blok)
        if not (ay and baslik) or ortak.kucuk(ay[1]) not in _AYLAR:
            continue
        try:
            tarih = dt.date(yil, _AYLAR.index(ortak.kucuk(ay[1])) + 1, int(ay[2]))
        except ValueError:
            continue
        if tarih < bugun - dt.timedelta(days=1):
            continue                       # liste 2025'ten beri tüm geçmişi içeriyor
        yer = re.search(r'location[^"]*\.svg"/><span[^>]*>([^<]+)</span>', blok)
        resim = re.search(r"url=(https?%3A%2F%2F[^&\"]+)", blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = ortak.temizle(html.unescape(yer[1])) if yer else "Kastamonu Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": tarih,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(urllib.parse.unquote(resim[1]), safe=":/") if resim else None,
            "url": KU + m[1],
        }


KAYNAKLAR = [
    {"ad": "Kastamonu Belediyesi", "tur": "belediye", "url": "https://www.kastamonu.bel.tr/etkinlik/", "cek": belediye},
    {"ad": "Kastamonu Üniversitesi", "tur": "universite", "url": KU + "/tr/etkinlikler", "cek": universite},
    {"ad": "Kastamonu İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kastamonu.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kastamonu", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kastamonu", "cek": etkinlik_io,
     "sehir": "Kastamonu", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kastamonu Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kastamonu.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Tosya, İnebolu, Taşköprü, Cide, Araç belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "İlçe festivalleri (Taşköprü Sarımsak, Cide Deniz, İnebolu Kültür-Sanat…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
