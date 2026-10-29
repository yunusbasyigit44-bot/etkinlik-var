"""Erzincan kaynakları (plaka 24). Kaynak haritası: 2026-10-29.

Erzincan Binali Yıldırım Üniversitesi (The Events Calendar eklentisi, iCal akışı) ve belediyenin etkinlik sayfası çalışıyor.
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Çayırlı", "İliç", "Kemah", "Kemaliye", "Otlukbeli", "Refahiye", "Tercan", "Üzümlü"]
SALON_ILCE = {"ebyü": "Merkez", "ebyu": "Merkez", "erdoğan büyükkasap": "Merkez", "kültür sanat merkezi": "Merkez",
              "binali yıldırım": "Merkez", "üniversite": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Erzincan Binali Yıldırım Üniversitesi — iCal akışı (The Events Calendar)
# ------------------------------------------------------------------
def _ical_olaylar(metin):
    metin = re.sub(r"\r?\n[ \t]", "", metin)          # katlanmış satırları birleştir
    for blok in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", metin, re.S):
        alan = {}
        for satir in blok.strip().splitlines():
            ad, _, deger = satir.partition(":")
            alan.setdefault(ad.split(";")[0], re.sub(r"\\n", " ", re.sub(r"\\([,;])", r"\1", deger)))
        yield alan


def _ical_zaman(deger):
    r = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2}))?", deger or "")
    if not r:
        return None, None
    return dt.date(int(r[1]), int(r[2]), int(r[3])), (f"{r[4]}:{r[5]}" if r[4] else None)


def ebyu(kaynak, bugun):
    for o in _ical_olaylar(ortak.indir(kaynak["url"])):
        bas, saat = _ical_zaman(o.get("DTSTART"))
        bit, _ = _ical_zaman(o.get("DTEND"))
        if not (bas and o.get("SUMMARY")):
            continue
        ad = basliklar(ortak.temizle(o["SUMMARY"].replace("''", '"')))
        yer = ortak.temizle(o.get("LOCATION") or "") or "Erzincan Binali Yıldırım Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": saat if saat != "00:00" else None,
            "mekan": yer,
            "ilce": salon_ilce(yer, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad + " " + (o.get("CATEGORIES") or "")),
            "url": o.get("URL") or "https://ebyu.edu.tr/etkinlik/",
            "ozet": o.get("CATEGORIES") or None,
        }


# ------------------------------------------------------------------
# 2) Erzincan Belediyesi — etkinlik kartları (HTML; kartta yıl yok, görselin yüklenme yılından anlaşılır)
# ------------------------------------------------------------------
KISA_AY = {"oca": 1, "şub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6, "tem": 7, "ağu": 8, "eyl": 9, "eki": 10, "kas": 11, "ara": 12}


def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("group bg-white rounded-[1.5rem]")[1:]:
        link = re.search(r'href="(https://erzincan\.bel\.tr/etkinlikler/[^"]+)"', blok)
        baslik = re.search(r"<h3[^>]*>\s*(.*?)\s*</h3>", blok, re.S)
        gun = re.search(r'leading-none">(\d{1,2})</span>\s*<span[^>]*>\s*([^<]+?)\s*</span>', blok)
        resim = re.search(r'<img src="(https://erzincan\.bel\.tr/upload/etkinlikler/(\d{4})_(\d{2})_(\d{2})[^"]+)"', blok)
        if not (link and baslik and gun and resim):
            continue
        ay = KISA_AY.get(ortak.kucuk(gun[2])[:3])
        if not ay:
            continue
        yuklenme = dt.date(int(resim[2]), int(resim[3]), int(resim[4]))
        try:
            tarih = dt.date(yuklenme.year, ay, int(gun[1]))
        except ValueError:
            continue
        if tarih < yuklenme - dt.timedelta(days=45):
            continue                       # yıl belirsiz (eski kayıt toplu yüklenmiş olabilir); tahminle etkinlik ekleme
        # Kartta saat ve yer var: ilk kısa metin saat, kalan satır yer
        saat = re.search(r"far fa-clock.*?<span[^>]*>\s*([^<]+?)\s*</span>", blok, re.S)
        yer = re.search(r"fa-map-marker-alt.*?<span[^>]*>\s*([^<]+?)\s*</span>", blok, re.S)
        mekan = ortak.temizle(yer[1]) if yer else None
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan or "", "Merkez"),
            "gorsel": resim[1],
            "url": link[1],
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "Erzincan Binali Yıldırım Üniversitesi", "tur": "universite", "url": "https://ebyu.edu.tr/etkinlik/?ical=1", "cek": ebyu},
    {"ad": "Erzincan Belediyesi", "tur": "belediye", "url": "https://erzincan.bel.tr/etkinlikler", "cek": belediye},
    {"ad": "Erzincan İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://erzincan.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Erzincan", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/erzincan", "cek": etkinlik_io,
     "sehir": "Erzincan", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Erzincan Valiliği", "tur": "valilik", "url": "https://www.erzincan.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "8 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "duyurular idari (ihale vb.); etkinlik yok"},
    {"ad": "Tercan, Kemah, Refahiye, Kemaliye belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi yok; çoğu sadece olmuş etkinliklerin haberi"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://erzincan.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://erzincan.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık festivaller (Kemaliye Uluslararası Kültür ve Sanat, Tulum Peyniri, Kemah Cevizi…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
