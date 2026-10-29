"""Van kaynakları (plaka 65). Kaynak haritası: 2026-10-29.

Okunan kaynak: İpekyolu Belediyesi etkinlik sayfası (kartlarda tarih aralığı, saat, mekan var). Van Büyükşehir sitesinde
etkinlik bölümü yok; Yüzüncü Yıl Üniversitesi sertifika hatası veriyor. Devlet Tiyatroları sahnesi var; kaynak listede.
"""
import datetime as dt
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["İpekyolu", "Tuşba", "Edremit", "Erciş", "Bahçesaray", "Başkale", "Çaldıran", "Çatak", "Gevaş", "Gürpınar",
           "Muradiye", "Özalp", "Saray"]
SALON_ILCE = {"atatürk sanat galerisi": "İpekyolu", "devlet tiyatro": "İpekyolu", "yüzüncü yıl": "Tuşba",
              "van gölü": "Tuşba", "sanat galerisi": "İpekyolu"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

IPEK = "https://www.ipekyolu.bel.tr"
_TARIH = re.compile(r"(\d{2})-(\d{2})-(\d{4})")


# ------------------------------------------------------------------
# 1) İpekyolu Belediyesi — etkinlik kartları (HTML, tarih GG-AA-YYYY)
# ------------------------------------------------------------------
def ipekyolu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in sayfa.split('class="activity-card"')[1:]:
        baslik = re.search(r'<h3 class="title"><a href="([^"]+)">(.*?)</a>', blok, re.S)
        yer = re.search(r'class="heading"[^>]*>(.*?)</a>', blok, re.S)
        tarihler = _TARIH.findall(blok)
        if not (baslik and tarihler) or baslik[1] in goruldu:
            continue
        goruldu.add(baslik[1])
        try:
            gun = [dt.date(int(y), int(a), int(g)) for g, a, y in tarihler]
        except ValueError:
            continue
        bas, bit = gun[0], gun[-1]
        saat = re.search(r'fa-clock"></i></span>\s*<div class="text">\s*([0-9]{1,2}:[0-9]{2})', blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[2]))
        mekan = ortak.temizle(yer[1]) if yer else None
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit > bas else None,
            "saat": saat[1] if saat else None,
            "mekan": mekan,
            "ilce": "İpekyolu",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": (resim[1] if resim[1].startswith("http") else IPEK + "/" + resim[1].lstrip("/")) if resim else None,
            "url": baslik[1],
        }


KAYNAKLAR = [
    {"ad": "İpekyolu Belediyesi", "tur": "belediye", "ilce": "İpekyolu", "url": IPEK + "/etkinlikler", "cek": ipekyolu},
    {"ad": "Van İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://van.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Van", "ilce_bul": salon_ilce, "varsayilan_ilce": "İpekyolu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/van", "cek": etkinlik_io,
     "sehir": "Van", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Van Yüzüncü Yıl Üniversitesi", "tur": "universite", "url": "https://www.yyu.edu.tr",
     "not": "sertifika hatası — okunamıyor"},
    {"ad": "Van Büyükşehir Belediyesi", "tur": "belediye", "url": "https://van.bel.tr",
     "not": "sitede etkinlik/takvim bölümü yok (haber ve duyuru)"},
    {"ad": "Tuşba ve Edremit belediyeleri", "tur": "belediye", "url": "https://www.edremit.bel.tr",
     "not": "etkinlik takvimi yok / okunmuyor"},
    {"ad": "Van Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.van.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Van Kahvaltı Festivali, Akdamar Etkinlikleri, Van Gölü Kültür Şenliği…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
