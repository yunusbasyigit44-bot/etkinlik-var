"""Gaziantep kaynakları (plaka 27). Kaynak haritası: 2026-10-29.

Çalışan kaynaklar: Gaziantep Büyükşehir Belediyesi (etkinlik kartları) ve Gaziantep Üniversitesi (ana sayfadaki takvim).
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Şahinbey", "Şehitkamil", "Araban", "İslahiye", "Karkamış", "Nizip", "Nurdağı", "Oğuzeli", "Yavuzeli"]
SALON_ILCE = {"gaziantep üniversitesi": "Şehitkamil", "gaün": "Şehitkamil", "hasan kalyoncu": "Şehitkamil",
              "kültür merkezi": "Şahinbey", "kalesi": "Şahinbey", "zeugma": "Şehitkamil", "panorama": "Şehitkamil",
              "mevlevi": "Şahinbey", "kurtuluş": "Şahinbey", "gastroantep": "Şahinbey", "anadolu": "Şehitkamil"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Gaziantep Büyükşehir Belediyesi — etkinlik kartları (HTML)
# ------------------------------------------------------------------
def buyuksehir(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    goruldu = set()
    for blok in re.split(r'<a href="(?=https://(?:www\.)?gaziantep\.bel\.tr/tr/basin/etkinlikler/)', sayfa)[1:]:
        link = re.match(r'([^"]+)"', blok)
        baslik = re.search(r"<h2[^>]*>\s*(.*?)\s*</h2>", blok, re.S)
        bas_m = re.search(r"Başlangıç</span>\s*<span[^>]*>([^<]+)<", blok)
        bit_m = re.search(r"Bitiş</span>\s*<span[^>]*>([^<]+)<", blok)
        if not (link and baslik and bas_m) or link[1] in goruldu:
            continue
        goruldu.add(link[1])
        bas, _ = ortak.tarih_bul(bas_m[1], bugun)
        bit, _ = ortak.tarih_bul(bit_m[1], bugun) if bit_m else (None, None)
        if not bas:
            continue
        resim = re.search(r'<img[^>]+src="(https://dosya\.gaziantep\.bel\.tr/[^"]+)"', blok)
        yer = re.search(r'ti-map-pin[^>]*></i>\s*<span[^>]*>([^<]+)<', blok)
        tur = re.search(r'<figure.*?<span[^>]*>\s*([^<]+?)\s*</span>', blok, re.S)
        mekan = ortak.temizle(yer[1]) if yer else None
        if mekan and ortak.kucuk(mekan) in ("diğer merkezler", "diğer"):
            mekan = None                    # genel etiket, gerçek mekan değil
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(re.sub(r"\d{1,2}\s+\w+\s+\d{4}", "", bas_m[1])),
            "mekan": mekan,
            "ilce": salon_ilce(mekan or "", "Şahinbey"),
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": resim[1] if resim else None,
            "url": link[1],
            "ucretsiz": True,
            "ozet": ortak.temizle(tur[1]) if tur else None,
        }


# ------------------------------------------------------------------
# 2) Gaziantep Üniversitesi — ana sayfadaki etkinlik takvimi (HTML)
# ------------------------------------------------------------------
def gantep(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    tarihler = dict(re.findall(r'<li id="etk_(\d+)">(\d{1,2}/\d{1,2}/\d{4})</li>', sayfa))
    goruldu = set()
    for no, baslik in re.findall(r'etkinlik_detay\.php\?etkinlik_ID=(\d+)" class="etkinlik-wrap"[^>]*>(.*?)</a>', sayfa, re.S):
        if no in goruldu or no not in tarihler:
            continue
        goruldu.add(no)
        g, a, y = (int(x) for x in tarihler[no].split("/"))
        yield {
            "baslik": basliklar(re.sub(r"[\"“”]|^'+|'+$", "", ortak.temizle(baslik)).strip()),
            "tarih": dt.date(y, a, g),
            "mekan": "Gaziantep Üniversitesi",
            "ilce": "Şehitkamil",
            "url": f"https://www.gaziantep.edu.tr/etkinlik_detay.php?etkinlik_ID={no}",
        }


KAYNAKLAR = [
    {"ad": "Gaziantep Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.gaziantep.bel.tr/tr/basin/etkinlikler", "cek": buyuksehir},
    {"ad": "Gaziantep Üniversitesi", "tur": "universite", "url": "https://www.gaziantep.edu.tr/", "cek": gantep},
    {"ad": "Gaziantep İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://gaziantep.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Gaziantep", "ilce_bul": salon_ilce, "varsayilan_ilce": "Şahinbey"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/gaziantep", "cek": etkinlik_io,
     "sehir": "Gaziantep", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Şehitkamil Belediyesi", "tur": "belediye", "ilce": "Şehitkamil", "url": "https://www.sehitkamil.bel.tr/Etkinlik_takvimi/sayfa",
     "not": "etkinlik takvimi sayfasında yaklaşan kayıt bulunamadı"},
    {"ad": "Şahinbey Belediyesi", "tur": "belediye", "ilce": "Şahinbey", "url": "https://www.sahinbey-bld.gov.tr",
     "not": "site bu bilgisayardan açılamadı"},
    {"ad": "Hasan Kalyoncu Üniversitesi", "tur": "universite", "url": "https://www.hku.edu.tr", "not": "etkinlik takvimi okunmuyor; sadece duyurular"},
    {"ad": "Gaziantep İslam Bilim ve Teknoloji Üniversitesi", "tur": "universite", "url": "https://www.gibtu.edu.tr/etkinlikrehberi.aspx",
     "not": "etkinlik rehberi otomatik okunmuyor"},
    {"ad": "Sanko Üniversitesi, Gaziantep Şehir Tiyatrosu", "tur": "diger", "url": None, "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Gaziantep Valiliği ve 9 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.gaziantep.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://gaziantep.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://gaziantep.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık festivaller (GastroAntep, Uluslararası Gaziantep Müzik, Zeugma Mozaik…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
