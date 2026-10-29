"""Kırıkkale kaynakları (plaka 71). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Kırıkkale Üniversitesi (etkinlik listesi), Kırıkkale Belediyesi (etkinlik sayfası; şu an eski kayıt var).
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Bahşılı", "Balışeyh", "Çelebi", "Delice", "Karakeçili", "Keskin", "Sulakyurt", "Yahşihan"]
SALON_ILCE = {"kırıkkale üniversitesi": "Yahşihan", "kku": "Yahşihan", "cumhuriyet meydanı": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KKU = "https://www.kku.edu.tr"


# ------------------------------------------------------------------
# 1) Kırıkkale Üniversitesi — "Tüm etkinlikler" listesi (HTML, tarih "28 Ekim 2026")
# ------------------------------------------------------------------
def kku(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('class="kku-list-item"')[1:]:
        tarih = re.search(r'kku-list-date">\s*<i[^>]*></i>\s*([^<]+)<', blok)
        baslik = re.search(r'<a href="(/Anasayfa/Etkinlik/Index/\d+)">(.*?)</a>', blok, re.S)
        if not (tarih and baslik):
            continue
        bas, bit = ortak.tarih_bul(ortak.temizle(tarih[1]), bugun)
        if not bas:
            continue
        ad = basliklar(ortak.temizle(html.unescape(baslik[2])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": "Kırıkkale Üniversitesi",
            "ilce": "Yahşihan",
            "kategori": ortak.kategori_tahmin(ad),
            "url": urllib.parse.urljoin(KKU + "/", baslik[1]),
        }


# ------------------------------------------------------------------
# 2) Kırıkkale Belediyesi — etkinlik kartları (HTML; tarih "23.04.2025")
# ------------------------------------------------------------------
BEL = "https://www.kirikkale.bel.tr/"


def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in re.split(r'<a href="\?sayfa=etkinlik_detay', sayfa)[1:]:
        kimlik = re.match(r"&(?:amp;)?id=(\d+)", blok)
        ad = re.search(r'class="name">(.*?)</div>', blok, re.S)
        sp = re.findall(r"<span>\s*([^<]+?)\s*</span>", blok[:1500])
        if not (kimlik and ad and sp):
            continue
        bas, _ = ortak.tarih_bul(sp[0], bugun)
        if not bas:
            continue
        resim = re.search(r'<img src="([^"]+)"', blok)
        yer = sp[2] if len(sp) > 2 else None
        yield {
            "baslik": basliklar(ortak.temizle(ad[1])),
            "tarih": bas,
            "saat": ortak.saat_bul(sp[1]) if len(sp) > 1 else None,
            "mekan": yer,
            "ilce": salon_ilce(yer or "", "Merkez"),
            "gorsel": urllib.parse.urljoin(BEL, urllib.parse.quote(resim[1], safe="/:")) if resim else None,
            "url": BEL + "?sayfa=etkinlik_detay&id=" + kimlik[1],
        }


KAYNAKLAR = [
    {"ad": "Kırıkkale Üniversitesi", "tur": "universite", "url": KKU + "/Anasayfa/Etkinlik/Tumu", "cek": kku},
    {"ad": "Kırıkkale Belediyesi", "tur": "belediye", "url": BEL + "?sayfa=etkinlikler", "cek": belediye},
    {"ad": "Kırıkkale İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kirikkale.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kırıkkale", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kirikkale", "cek": etkinlik_io,
     "sehir": "Kırıkkale", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kırıkkale Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kirikkale.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Belediye Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "İlçe belediyeleri (Yahşihan, Keskin, Delice…)", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Yıllık festivaller", "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
