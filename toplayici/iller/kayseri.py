"""Kayseri kaynakları (plaka 38). Kaynak haritası: 2026-10-29.

Okunan kaynak: Erciyes Üniversitesi etkinlik listesi ("Güncel Etkinlikler" bölümü). Kayseri Büyükşehir etkinlik sayfası
sadece kurs/dergi/akademi duyurusu veriyor (takvim değil), Melikgazi'de güncel kayıt yok; ikisi de listede "not" olarak durur.
Devlet Tiyatroları Kayseri sahnesi ortak kaynakla gelir.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akkışla", "Bünyan", "Develi", "Felahiye", "Hacılar", "İncesu", "Kocasinan", "Melikgazi", "Özvatan",
           "Pınarbaşı", "Sarıoğlan", "Sarız", "Talas", "Tomarza", "Yahyalı", "Yeşilhisar"]
SALON_ILCE = {"erciyes üniversitesi": "Melikgazi", "erü": "Melikgazi", "kadir has": "Melikgazi", "kayseri devlet": "Melikgazi",
              "cem sultan": "Melikgazi", "kültür yolu": "Melikgazi", "abdullah gül": "Talas", "agü": "Talas",
              "kayseri üniversitesi": "Kocasinan", "kayseri şehir": "Melikgazi"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Erciyes Üniversitesi — etkinlik listesi (HTML); kartta "27 Ekim 2026 Salı 13:30" ve başlık
# ------------------------------------------------------------------
ERU = "https://www.erciyes.edu.tr"


def erciyes(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    guncel = sayfa.split("TAMAMLANAN ETKİNLİKLER")[0]
    for blok in guncel.split('role="listitem"')[1:]:
        link = re.search(r'<a href="(/tr/etkinlik-detay/[^"]+)"', blok)
        zaman = re.search(r'mr-2" aria-hidden="true"></i>\s*([^<]+?)\s*</div>', blok)
        baslik = re.search(r'fw7 fs15">\s*(.*?)\s*</div>', blok, re.S)
        if not (link and zaman and baslik):
            continue
        bas, _ = ortak.tarih_bul(zaman[1], bugun)
        if not bas:
            continue
        ad = basliklar(ortak.temizle(baslik[1]))
        kucuk = ortak.kucuk(ad)
        if "radyo yayını" in kucuk or "kariyer ve kişisel gelişim eğitimi" in kucuk:
            continue                       # kampüs içi yayın / öğrenci eğitimi
        resim = re.search(r"url\((/images/Etkinlik/[^)]+)\)", blok)
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(zaman[1]),
            "mekan": "Erciyes Üniversitesi",
            "ilce": "Melikgazi",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": ERU + urllib.parse.quote(resim[1], safe="/%") if resim else None,
            "url": ERU + urllib.parse.quote(link[1], safe="/%"),
        }


KAYNAKLAR = [
    {"ad": "Erciyes Üniversitesi", "tur": "universite", "ilce": "Melikgazi", "url": "https://www.erciyes.edu.tr/tr/etkinlikler", "cek": erciyes},
    {"ad": "Kayseri İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kayseri.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kayseri", "ilce_bul": salon_ilce, "varsayilan_ilce": "Melikgazi"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kayseri", "cek": etkinlik_io,
     "sehir": "Kayseri", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kayseri Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.kayseri.bel.tr/etkinlikler",
     "not": "etkinlik sayfası kurs, dergi ve akademi duyurusu veriyor; güncel takvim yok — okunmuyor"},
    {"ad": "Melikgazi Belediyesi", "tur": "belediye", "ilce": "Melikgazi", "url": "https://www.melikgazi.bel.tr/etkinlikler",
     "not": "sayfada tarihsiz, çoğu geçmiş kayıt var; okunmuyor"},
    {"ad": "Kocasinan ve Talas belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Kayseri Üniversitesi", "tur": "universite", "ilce": "Kocasinan", "url": "https://www.kayseri.edu.tr/tr/e/etkinlik/tum-etkinlikler",
     "not": "listede sadece tamamlanan etkinlikler görünüyor"},
    {"ad": "Abdullah Gül Üniversitesi", "tur": "universite", "ilce": "Talas", "url": "https://www.agu.edu.tr", "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Kayseri Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kayseri.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Kayseri Büyükşehir Şehir Tiyatrosu, Kadir Has Kültür Merkezi", "tur": "belediye", "url": None,
     "not": "oyun/konser takvimi okunabilir biçimde yayımlanmıyor"},
    {"ad": "Kayseri Kültür Yolu, Erciyes kış festivalleri…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
