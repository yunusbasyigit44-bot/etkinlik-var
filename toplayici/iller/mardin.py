"""Mardin kaynakları (plaka 47). Kaynak haritası: 2026-10-29.

Okunan kaynak: Mardin Artuklu Üniversitesi ana sayfasındaki etkinlik kutuları. Büyükşehir, Artuklu ve
Kızıltepe belediyelerinde etkinlik takvimi yok (sadece idari duyuru ve haber).
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Artuklu", "Dargeçit", "Derik", "Kızıltepe", "Mazıdağı", "Midyat", "Nusaybin", "Ömerli", "Savur", "Yeşilli"]
SALON_ILCE = {"artuklu üniversitesi": "Artuklu", "kampüs": "Artuklu", "merkezi derslik": "Artuklu"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

MAU = "https://www.artuklu.edu.tr"
_AY = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "eylül": 9,
       "ekim": 10, "kasım": 11, "aralık": 12}


# ------------------------------------------------------------------
# 1) Mardin Artuklu Üniversitesi — ana sayfa etkinlik kutuları (HTML; kutuda yıl yok)
# ------------------------------------------------------------------
def artuklu(kaynak, bugun):
    sayfa = ortak.indir(MAU)
    for blok in sayfa.split('<div class="ma-et"')[1:]:
        gun = re.search(r'etkinlik-takvim[^>]*>\s*(\d{1,2})\s*<span>([^<]+)</span>', blok)
        baslik = re.search(r'class="ed-baslik">(.*?)</div>', blok, re.S)
        link = re.search(r"window\.location = '([^']+)'", blok)
        if not (gun and baslik):
            continue
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        ay = _AY.get(ortak.kucuk(gun[2]).strip())
        if not ay:
            continue
        bas, bit = ortak.tarih_bul(ad, bugun)      # başlıkta tam tarih varsa (ör. "14-15 Mayıs 2026") onu kullan
        if not (re.search(r"\d{4}", ad) and bas):
            # Kutuda yıl yok: yılı etkinliğin kendi sayfasından (gg.aa.yyyy) doğrula; geçmiş etkinlikler için sayfa açma
            aday = dt.date(bugun.year, ay, int(gun[1]))
            if aday < bugun:
                aday = aday.replace(year=bugun.year + 1)
            if aday > bugun + dt.timedelta(days=100):
                continue
            bas, bit = None, None
            if link:
                try:
                    ic = ortak.indir(urllib.parse.urljoin(MAU, link[1]))
                    t = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", re.sub(r"<[^>]+>|&nbsp;", " ", ic))
                    if t and int(t[2]) == ay and int(t[1]) == int(gun[1]):
                        bas = dt.date(int(t[3]), ay, int(gun[1]))
                except Exception:
                    pass
            if not bas:
                continue
        detay = re.search(r'class="ed-detay">(.*?)</div>', blok, re.S)
        d = ortak.temizle(html.unescape(detay[1])) if detay else ""
        yer = re.sub(r"^SAAT\s*[\d:.]+,?\s*", "", d).strip() or "Mardin Artuklu Üniversitesi"
        resim = re.search(r"<img[^>]+src=([^ >]+)", blok)
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(d),
            "mekan": yer,
            "ilce": salon_ilce(yer, "Artuklu"),
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.urljoin(MAU, urllib.parse.quote(resim[1].strip("'\""), safe=":/%")) if resim else None,
            "url": urllib.parse.urljoin(MAU, link[1]) if link else MAU,
        }


KAYNAKLAR = [
    {"ad": "Mardin Artuklu Üniversitesi", "tur": "universite", "ilce": "Artuklu", "url": MAU, "cek": artuklu},
    {"ad": "Mardin İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://mardin.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Mardin", "ilce_bul": salon_ilce, "varsayilan_ilce": "Artuklu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/mardin", "cek": etkinlik_io,
     "sehir": "Mardin", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Mardin Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.mardin.bel.tr",
     "not": "etkinlik sayfası yok; duyurular idari, haberler serbest metin"},
    {"ad": "Artuklu Belediyesi", "tur": "belediye", "ilce": "Artuklu", "url": "https://www.artuklu.bel.tr",
     "not": "etkinlik takvimi yok; duyurular idari"},
    {"ad": "Kızıltepe Belediyesi", "tur": "belediye", "ilce": "Kızıltepe", "url": "https://www.kiziltepe.bel.tr",
     "not": "etkinlik takvimi yok; duyurular idari"},
    {"ad": "Mardin Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.mardin.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Midyat, Nusaybin, Derik belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Mardin Kültür Yolu Festivali, Mardin Uluslararası Film Günleri…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
