"""Mersin kaynakları (plaka 33). Kaynak haritası: 2026-10-29.

Okunan: Mersin Üniversitesi etkinlik listesi (sayfaya gömülü JSON). Büyükşehir Belediyesi etkinlik sayfasında
tarih yalnızca tek tek detay sayfalarında olduğundan okunmuyor. Mersin Devlet Opera ve Balesi için
okunabilir bir program sayfası bulunamadı (devlet sitesi sertifika hatası veriyor).
"""
import datetime as dt
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_opera, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akdeniz", "Anamur", "Aydıncık", "Bozyazı", "Çamlıyayla", "Erdemli", "Gülnar", "Mezitli", "Mut", "Silifke",
           "Tarsus", "Toroslar", "Yenişehir"]
SALON_ILCE = {"mersin üniversitesi": "Yenişehir", "çiftlikköy": "Yenişehir", "meüsem": "Yenişehir", "arkeoloji müzesi": "Akdeniz",
              "opera": "Yenişehir", "kültür merkezi": "Akdeniz", "uğur": "Yenişehir"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

MEU = "https://www.mersin.edu.tr"


# ------------------------------------------------------------------
# 1) Mersin Üniversitesi — etkinlik listesi (sayfaya gömülü JSON)
# ------------------------------------------------------------------
def universite(kaynak, bugun):
    sayfa = html.unescape(ortak.indir(kaynak["url"]))
    gorulen = set()
    for parca in sayfa.split('"baslangic_tarihi":"')[1:]:
        parca = parca[:6000]
        bas_m = re.match(r"(\d{4}-\d{2}-\d{2})", parca)
        baslik = re.search(r'"title":"((?:[^"\\]|\\.)*)"', parca)
        slug = re.search(r'"slug":"([^"]+)"', parca)
        if not (bas_m and baslik and slug) or slug[1] in gorulen:
            continue
        gorulen.add(slug[1])
        kat = re.search(r'"categories":\[\{"id":"[^"]*","label":"([^"]+)"', parca)
        kategori_ad = kat[1] if kat else ""
        if ortak.kucuk(kategori_ad) in ("eğitim",):
            continue                       # kurslar/eğitimler halka açık etkinlik değil
        bit_m = re.search(r'"bitis_tarihi":"(\d{4}-\d{2}-\d{2})', parca[:200])
        bas = dt.date.fromisoformat(bas_m[1])
        bit = dt.date.fromisoformat(bit_m[1]) if bit_m else None
        yer = re.search(r'"location":"((?:[^"\\]|\\.)*)"', parca)
        saat = re.search(r'"time":"(\d{2}:\d{2})', parca)
        resim = re.search(r'"image":"(https://[^"]+)"', parca)
        mekan = ortak.temizle(yer[1]) if yer and yer[1] else "Mersin Üniversitesi"
        ad = basliklar(ortak.temizle(baslik[1].replace('\\"', '"')))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bas < bit <= bas + dt.timedelta(days=45) else None,
            "saat": saat[1] if saat else None,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Yenişehir"),
            "kategori": ortak.kategori_tahmin(ad + " " + kategori_ad),
            "gorsel": resim[1] if resim else None,
            "url": MEU + slug[1],
            "ozet": kategori_ad or None,
        }


KAYNAKLAR = [
    {"ad": "Devlet Opera ve Balesi", "tur": "kultur", "url": "https://www.operabale.gov.tr", "cek": devlet_opera,
     "mudurluk": 4, "ilce_bul": salon_ilce, "varsayilan_ilce": "Yenişehir"},
    {"ad": "Mersin Üniversitesi", "tur": "universite", "url": MEU + "/etkinlikler", "cek": universite},
    {"ad": "Mersin İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://mersin.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/mersin", "cek": etkinlik_io,
     "sehir": "Mersin", "ilce_bul": salon_ilce, "varsayilan_ilce": "Yenişehir"},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Mersin Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.mersin.bel.tr/etkinlikler",
     "not": "liste sayfasında tarih yok (sadece tek tek detay sayfalarında); henüz okunmuyor"},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "not": "Mersin'de sahne yok"},
    {"ad": "Tarsus Üniversitesi, Toros Üniversitesi, Çağ Üniversitesi", "tur": "universite", "url": None,
     "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Mersin Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Akdeniz, Mezitli, Yenişehir, Toroslar, Tarsus, Silifke belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Mersin Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.mersin.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Uluslararası Mersin Müzik Festivali, Narenciye Festivali, Silifke Müzik ve Folklor…)", "tur": "diger",
     "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
