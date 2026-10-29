"""Nevşehir kaynakları (plaka 50). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Nevşehir Hacı Bektaş Veli Üniversitesi etkinlik tablosu, Ürgüp Belediyesi etkinlik sayfası
(liste tarihsiz; tarih her etkinliğin kendi sayfasından okunur). Ürgüp'ün etkinlik.urgup.bel.tr sitesi
bilet satış sitesi olduğu için kazınmıyor. Nevşehir Belediyesi'nde etkinlik takvimi yok, sadece haber.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Acıgöl", "Avanos", "Derinkuyu", "Gülşehir", "Hacıbektaş", "Kozaklı", "Ürgüp"]
SALON_ILCE = {"nevü": "Merkez", "hacı bektaş veli üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

NEVU = "https://www.nevsehir.edu.tr"
URGUP = "https://urgup.bel.tr"


# ------------------------------------------------------------------
# 1) Nevşehir Hacı Bektaş Veli Üniversitesi — etkinlik tablosu (HTML)
# ------------------------------------------------------------------
def nevu(kaynak, bugun):
    sayfa = ortak.indir(NEVU + "/tr/etkinlikler")
    for satir in re.findall(r"<tr>(.*?)</tr>", sayfa, re.S):
        a = re.search(r'<a href="([^"]+)"[^>]*>(.*?)</a>', satir, re.S)
        hucre = re.findall(r"<td[^>]*>(.*?)</td>", satir, re.S)
        if not a or len(hucre) < 2:
            continue
        bas, bit = ortak.tarih_bul(ortak.temizle(hucre[1]), bugun)
        if not bas:
            continue
        tur = ortak.temizle(hucre[2]) if len(hucre) > 2 else ""
        ad = basliklar(ortak.temizle(html.unescape(a[2])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": "Nevşehir Hacı Bektaş Veli Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad + " " + tur),
            "url": a[1],
            "ozet": tur or None,
        }


# ------------------------------------------------------------------
# 2) Ürgüp Belediyesi — etkinlik listesi (HTML) + her etkinliğin sayfasındaki tarih
# ------------------------------------------------------------------
def urgup(kaynak, bugun):
    sayfa = ortak.indir(URGUP + "/tr/etkinlikler")
    for link, blok in re.findall(r'<a href="(https://urgup\.bel\.tr/tr/etkinlik/(?!2026-etkinlik-takvimi)[^"]+)">(.*?)</a>', sayfa, re.S):
        baslik = re.search(r'<h3 class="title">(.*?)</h3>', blok, re.S)
        if not baslik:
            continue
        try:
            ic = ortak.indir(link)
        except Exception:
            continue
        metin = ortak.temizle(re.sub(r"<svg.*?</svg>|<script.*?</script>|<style.*?</style>", " ", ic, flags=re.S))
        bas, bit = ortak.tarih_bul(metin, bugun)
        if not bas:
            continue
        resim = re.search(r'data-src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])).replace("EKIM", "EKİM").replace("CUMHURIYET", "CUMHURİYET"))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(metin[:1500]),
            "mekan": "Ürgüp",
            "ilce": "Ürgüp",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": urllib.parse.quote(resim[1], safe=":/%") if resim else None,
            "url": link,
        }


KAYNAKLAR = [
    {"ad": "Nevşehir Hacı Bektaş Veli Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": NEVU + "/tr/etkinlikler", "cek": nevu},
    {"ad": "Ürgüp Belediyesi", "tur": "belediye", "ilce": "Ürgüp", "url": URGUP + "/tr/etkinlikler", "cek": urgup},
    {"ad": "Nevşehir İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://nevsehir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Nevşehir", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/nevsehir", "cek": etkinlik_io,
     "sehir": "Nevşehir", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Nevşehir Belediyesi", "tur": "belediye", "url": "https://www.nevsehir.bel.tr",
     "not": "etkinlik takvimi yok; sadece haber (kahve atölyesi, patates festivali haberleri)"},
    {"ad": "Avanos Belediyesi", "tur": "belediye", "ilce": "Avanos", "url": "https://www.avanos.bel.tr",
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Ürgüp etkinlik bilet sitesi (etkinlik.urgup.bel.tr)", "tur": "belediye", "ilce": "Ürgüp", "url": "https://etkinlik.urgup.bel.tr",
     "not": "bilet satış sitesi; kazınmıyor"},
    {"ad": "Nevşehir Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.nevsehir.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Kapadokya Sanat ve Kültür festivalleri, Ürgüp Bağ Bozumu, Hacıbektaş Anma Törenleri…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
