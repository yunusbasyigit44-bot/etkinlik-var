"""Muş kaynakları (plaka 49). Kaynak haritası: 2026-10-29.

Okunan kaynak: Muş Alparslan Üniversitesi etkinlik listesi (liste başlangıç tarihini gösterir; çoğu kayıt
yayınlandığı gün başladığı için yaklaşan etkinlik azdır). Muş Belediyesi sitesi zaman aşımına uğruyor,
Valilik/Kültür Turizm sayfalarında etkinlik takvimi yok.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Bulanık", "Hasköy", "Korkut", "Malazgirt", "Varto"]
SALON_ILCE = {"alparslan": "Merkez", "kültür merkezi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

MAU = "https://www.alparslan.edu.tr"


# ------------------------------------------------------------------
# 1) Muş Alparslan Üniversitesi — etkinlik listesi (HTML)
# ------------------------------------------------------------------
def alparslan(kaynak, bugun):
    sayfa = ortak.indir(MAU + "/tr/page/event")
    goruldu = set()
    for blok in sayfa.split('class="news-type"')[1:]:
        # her blokun başındaki href bir önceki <a ...> etiketindedir; blok içinde ikinci kez geçer
        link = re.search(r'<div class="img" href="([^"]+)"', blok)
        baslik = re.search(r'class="news-title" title="([^"]*)"', blok)
        t = re.search(r'class="news-date">\s*(\d{1,2}\.\d{1,2}\.\d{4})', blok)
        if not (link and baslik and t):
            continue
        bas, _ = ortak.tarih_bul(t[1], bugun)
        if not bas:
            continue
        if link[1] in goruldu:
            continue                       # aynı etkinlik listede iki kez geçebiliyor
        goruldu.add(link[1])
        bit = None
        if bas >= bugun - dt.timedelta(days=14):
            # Listede yalnızca başlangıç var; yakın tarihli kayıtların bitişi ve yeri kendi sayfasında
            try:
                ic = ortak.indir(link[1])
                b = re.search(r"BAŞLANGIÇ TARİHİ:\s*(\d{2})-(\d{2})-(\d{4})", ic)
                e = re.search(r"BİTİŞ TARİHİ:\s*(\d{2})-(\d{2})-(\d{4})", ic)
                if b:
                    bas = dt.date(int(b[3]), int(b[2]), int(b[1]))
                if e:
                    bit = dt.date(int(e[3]), int(e[2]), int(e[1]))
            except Exception:
                pass
        resim = re.search(r'<img\s+src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": "Muş Alparslan Üniversitesi",
            "ilce": "Merkez",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": link[1],
        }


KAYNAKLAR = [
    {"ad": "Muş Alparslan Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": MAU + "/tr/page/event", "cek": alparslan},
    {"ad": "Muş İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://mus.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Muş", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/mus", "cek": etkinlik_io,
     "sehir": "Muş", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Muş Belediyesi", "tur": "belediye", "url": "https://www.mus.bel.tr", "not": "site zaman aşımına uğruyor — okunamıyor"},
    {"ad": "Muş Alparslan Üniversitesi Etkinlik Takvimi (etakvim)", "tur": "universite", "url": "http://etakvim.alparslan.edu.tr/",
     "not": "site zaman aşımına uğruyor — okunamıyor"},
    {"ad": "Muş Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.mus.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Malazgirt, Bulanık, Varto belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Malazgirt Zaferi Anma Etkinlikleri, Muş Lale Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
