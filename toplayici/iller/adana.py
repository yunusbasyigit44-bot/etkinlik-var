"""Adana kaynakları (pilot il). Kaynak haritası: 2026-10-29.

Her kaynak bir sözlük: ad, tur, url, (ilce), cek=fonksiyon.
`cek` yoksa kaynak sitede "durum" notuyla listelenir — böylece eksikler görünür kalır.
"""
import datetime as dt
import json
import re
import urllib.request

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Aladağ", "Ceyhan", "Çukurova", "Feke", "İmamoğlu", "Karaisalı", "Karataş", "Kozan",
           "Pozantı", "Saimbeyli", "Sarıçam", "Seyhan", "Tufanbeyli", "Yumurtalık", "Yüreğir"]

# Bilinen salonların ilçeleri (etkinlikte ilçe yazmıyorsa buradan bulunur)
SALON_ILCE = {
    "ramazanoğlu": "Seyhan", "büyükşehir belediyesi tiyatro": "Seyhan", "sabancı kültür": "Seyhan",
    "balcalı": "Sarıçam", "çukurova üniversitesi": "Sarıçam", "atü": "Sarıçam", "alparslan türkeş": "Sarıçam",
}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 2) Adana Büyükşehir Belediyesi Şehir Tiyatrosu — etkinlik sayfası (HTML)
# ------------------------------------------------------------------
def sehir_tiyatrosu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in re.split(r'<div class="[^"]*\bevent-item\b', sayfa)[1:]:
        ay = re.search(r'data-month="(\d{4})-(\d{2})"', blok)
        gun = re.search(r'event-date[^>]*>\s*<div[^>]*>\s*(\d{1,2})\s*<', blok)
        baslik = re.search(r"<h4[^>]*>(.*?)</h4>", blok, re.S)
        if not (ay and gun and baslik):
            continue
        saat = re.search(r"bi-clock[^>]*></i>\s*([0-2]?\d[:.][0-5]\d)", blok)
        mekan = re.search(r"bi-geo-alt[^>]*></i>\s*([^<]+)", blok)
        topluluk = re.search(r'</h4>\s*<p class="mb-1 text-muted">(.*?)</p>', blok, re.S)
        mekan_ad = ortak.temizle(mekan[1]) if mekan else "Adana Büyükşehir Belediyesi Tiyatro Salonu"
        tur = re.search(r'data-category="([^"]*)"', blok)
        resim = re.search(r'<img[^>]+src="(https?://[^"]+)"', blok)
        yield {
            "baslik": basliklar(ortak.temizle(baslik[1])),
            "tarih": dt.date(int(ay[1]), int(ay[2]), int(gun[1])),
            "saat": saat[1].replace(".", ":") if saat else None,
            "mekan": mekan_ad,
            "ilce": salon_ilce(mekan_ad, "Seyhan"),
            "gorsel": resim[1] if resim else None,
            "kategori": "Çocuk" if tur and "çocuk" in ortak.kucuk(tur[1]) else "Tiyatro",
            "ozet": ortak.temizle(topluluk[1]) if topluluk else None,
        }


# ------------------------------------------------------------------
# 3) Adana Alparslan Türkeş Bilim ve Teknoloji Üniversitesi — OData (JSON)
# ------------------------------------------------------------------
ATU_URL = ("https://odata.atu.edu.tr/odata/DataService.svc/V_GuncelIcerik"
           "?$filter=GrupTipi%20eq%204&$orderby=BaslamaTarihi%20desc&$top=100")


def _odata_tarih(s):
    """'/Date(1675416794903)/' -> Türkiye saati. Gece yarısı (UTC 00:00) kayıtlarda saat girilmemiştir."""
    ms = int(re.search(r"-?\d+", s or "0")[0])
    utc = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(milliseconds=ms)
    saatsiz = utc.hour == 0 and utc.minute == 0
    return utc.astimezone(dt.timezone(dt.timedelta(hours=3))), saatsiz


def atu(kaynak, bugun):
    istek = urllib.request.Request(ATU_URL, headers={"User-Agent": ortak.TARAYICI, "Accept": "application/json;odata=verbose"})
    with urllib.request.urlopen(istek, timeout=30) as y:
        veri = json.loads(y.read().decode("utf-8"))
    kayitlar = veri["d"]["results"] if isinstance(veri["d"], dict) else veri["d"]
    for k in kayitlar:
        (bas, saatsiz), (bit, _) = _odata_tarih(k.get("BaslamaTarihi")), _odata_tarih(k.get("BitisTarihi"))
        if bas.year > 2100 or k.get("DilKodu") not in (None, "TR") or k.get("Durum") == 0:
            continue                       # 9999 yılı = "süresiz" kayıt, etkinlik değil
        baslik = k.get("Baslik") or ""
        if "akademik ve sektör seminerleri" in ortak.kucuk(baslik):
            continue                       # her hafta tekrarlanan genel başlık
        yer = ortak.temizle(k.get("Yeri") or "")
        yield {
            "baslik": basliklar(baslik),
            "tarih": bas.date(),
            # Bitiş çoğu kayıtta başvuru/yayın sonu; 7 günden uzunsa tek günlük etkinlik say
            "bitis": bit.date() if bas.date() <= bit.date() <= bas.date() + dt.timedelta(days=7) else None,
            "saat": None if saatsiz else bas.strftime("%H:%M"),
            "mekan": yer if yer and yer != "-" else "Adana Alparslan Türkeş BTÜ",
            "ilce": "Sarıçam",
            "gorsel": "https://www.atu.edu.tr" + k["KapakFotograf"] if k.get("KapakFotograf") else None,
            "kategori": ortak.kategori_tahmin(baslik + " " + (k.get("Tipi") or "")),
            "url": kaynak["url"],
            "ozet": k.get("Tipi"),
        }


# ------------------------------------------------------------------
# 4) Çukurova Üniversitesi — ana sayfadaki "Yaklaşan Etkinlikler" (HTML)
# ------------------------------------------------------------------
def cukurova_uni(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    bolum = sayfa.split("Yaklaşan Etkinlikler", 1)
    if len(bolum) < 2:
        raise RuntimeError("'Yaklaşan Etkinlikler' bölümü bulunamadı (site değişmiş olabilir)")
    for blok in bolum[1].split('class="oc-item"')[1:]:
        baslik = re.search(r'title="([^"]+)"', blok)
        link = re.search(r'href="(/[^"]+)"', blok)
        resim = re.search(r'<img[^>]+src="([^"]+)"', blok)
        tarih = re.search(r"icon-calendar3[^>]*></i>\s*([^<]+)", blok)
        if not (baslik and tarih):
            continue
        bas, bit = ortak.tarih_bul(ortak.temizle(tarih[1]), bugun)
        yield {
            "baslik": ortak.temizle(baslik[1]),
            "tarih": bas, "bitis": bit,
            "mekan": "Çukurova Üniversitesi",
            "ilce": "Sarıçam",
            "gorsel": ("https://www.cu.edu.tr" + resim[1] if resim[1].startswith("/") else resim[1]) if resim else None,
            "url": "https://www.cu.edu.tr" + link[1] if link else kaynak["url"],
        }


# ------------------------------------------------------------------
# Kaynak listesi
# ------------------------------------------------------------------
KAYNAKLAR = [
    {"ad": "Devlet Tiyatroları Adana", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Adana", "ilce_bul": salon_ilce, "varsayilan_ilce": "Seyhan"},
    {"ad": "Adana Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": "https://sehirtiyatrosu.adana.bel.tr/etkinlikler", "cek": sehir_tiyatrosu},
    {"ad": "Adana Alparslan Türkeş BTÜ", "tur": "universite", "url": "https://www.atu.edu.tr", "cek": atu},
    {"ad": "Çukurova Üniversitesi", "tur": "universite", "url": "https://www.cu.edu.tr", "cek": cukurova_uni},
    {"ad": "Adana İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://adana.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/adana", "cek": etkinlik_io,
     "sehir": "Adana", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Adana Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.adana.bel.tr",
     "not": "sitede etkinlik takvimi yok (sadece haber/duyuru)"},
    {"ad": "Adana Valiliği", "tur": "valilik", "url": "https://www.adana.gov.tr", "not": "duyurular ihale/ilan; etkinlik yok"},
    {"ad": "15 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": "https://www.seyhan.gov.tr/duyurular",
     "not": "duyurular idari (TYP, ihale); etkinlik yok"},
    {"ad": "Seyhan Belediyesi", "tur": "belediye", "ilce": "Seyhan", "url": "https://www.seyhan.bel.tr",
     "not": "etkinlik sayfası var ama güncel değil (son kayıt 2025)"},
    {"ad": "Çukurova Belediyesi", "tur": "belediye", "ilce": "Çukurova", "url": "https://www.cukurova.bel.tr",
     "not": "sadece olmuş etkinliklerin haberleri"},
    {"ad": "Yüreğir Belediyesi", "tur": "belediye", "ilce": "Yüreğir", "url": "https://yuregir.bel.tr",
     "not": "sadece olmuş etkinliklerin haberleri"},
    {"ad": "Sarıçam, Ceyhan, Kozan ve diğer ilçe belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi yok / bazıları erişilemiyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://adana.gsb.gov.tr", "not": "bot koruması — okunamıyor"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://adana.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Altın Koza Film Festivali", "tur": "diger", "url": None, "not": "sitesi bakımda (eylül festivali)"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
