"""Karabük kaynakları (plaka 78). Kaynak haritası: 2026-10-29.

Okunan kaynak: Karabük Üniversitesi etkinlik takvimi (takvim.karabuk.edu.tr, aylık ASP.NET takvimi; bağlantıda tarih var).
Takvimde idari işler (maaş, bütçe vb.) de var; sadece "...Etkinlik..." ya da "Kültür" etiketli kayıtlar alınır.
Belediye (duyurular.asp) ve valilik sitelerinde etkinlik takvimi yok. Devlet Tiyatroları sahnesi yok.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Eflani", "Eskipazar", "Ovacık", "Safranbolu", "Yenice"]
SALON_ILCE = {"karabük üniversitesi": "Merkez", "safranbolu": "Safranbolu", "eflani": "Eflani", "eskipazar": "Eskipazar",
              "ovacık": "Ovacık", "yenice": "Yenice"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

TAKVIM = "https://takvim.karabuk.edu.tr"


# ------------------------------------------------------------------
# 1) Karabük Üniversitesi — etkinlik takvimi (HTML)
# ------------------------------------------------------------------
def kbu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for link, ad, etiket, birim in re.findall(
            r'<a href="(/\d\d-\d\d-\d{4}-[^"]+-etkinlik-\d+)" title="([^"]*)"[^>]*><b>([^<]*)</b>.*?(?:<small>\(([^)]*)\)</small>)?</a>',
            sayfa, re.S):
        if link in goruldu or not re.search(r"etkinlik|kültür|sanat|spor", ortak.kucuk(html.unescape(etiket))):
            continue
        goruldu.add(link)
        gun = re.match(r"/(\d\d)-(\d\d)-(\d{4})-", link)
        baslik = basliklar(ortak.temizle(html.unescape(ad)))
        birim = ortak.temizle(html.unescape(birim or ""))
        yield {
            "baslik": baslik,
            "tarih": dt.date(int(gun[3]), int(gun[2]), int(gun[1])),
            "mekan": "Karabük Üniversitesi" + (" · " + birim if birim else ""),
            "ilce": "Safranbolu" if "safranbolu" in ortak.kucuk(baslik + " " + birim) else "Merkez",
            "kategori": ortak.kategori_tahmin(baslik + " " + etiket),
            "url": TAKVIM + link,
            "ozet": ortak.temizle(html.unescape(etiket)),
        }


KAYNAKLAR = [
    {"ad": "Karabük Üniversitesi", "tur": "universite", "url": TAKVIM + "/", "cek": kbu},
    {"ad": "Karabük İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://karabuk.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Karabük", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/karabuk", "cek": etkinlik_io,
     "sehir": "Karabük", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Karabük Belediyesi", "tur": "belediye", "url": "https://www.karabuk.bel.tr/duyurular.asp",
     "not": "duyurular idari; etkinlik takvimi yok"},
    {"ad": "Safranbolu Belediyesi", "tur": "belediye", "ilce": "Safranbolu", "url": None, "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Karabük Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.karabuk.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Safranbolu Lokumu ve Safran, Yörük Şenliği…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
