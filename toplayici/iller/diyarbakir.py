"""Diyarbakır kaynakları (plaka 21). Kaynak haritası: 2026-10-29.

Çalışan: Diyarbakır Büyükşehir Belediyesi (Next.js sayfası, kartlar sunucudan hazır geliyor; şehir
tiyatrosu, sinema, konser), Dicle Üniversitesi etkinlik listesi. Devlet Tiyatroları sahnesi var.
"""
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Bağlar", "Bismil", "Çermik", "Çınar", "Çüngüş", "Dicle", "Eğil", "Ergani", "Hani", "Hazro", "Kayapınar",
           "Kocaköy", "Kulp", "Lice", "Silvan", "Sur", "Yenişehir"]
SALON_ILCE = {"dicle üniversitesi": "Sur", "sezai karakoç": "Yenişehir", "çandamed": "Yenişehir",
              "devlet tiyatro": "Yenişehir", "cegerxwîn": "Yenişehir", "cemil çiçek": "Sur"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Diyarbakır Büyükşehir Belediyesi — etkinlik kartları (sunucuda hazır HTML)
# ------------------------------------------------------------------
BEL = "https://www.diyarbakir.bel.tr"


def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("eventCardLink")[1:]:
        link = re.search(r'href="(/etkinlikler/[^"]+)"', blok)
        baslik = re.search(r'<h3 class="[^"]*eventTitle">(.*?)</h3>', blok, re.S)
        sp = re.findall(r"<span>([^<]*)</span>", blok)
        if not (link and baslik and sp):
            continue
        # sp[0] tarih (+ saat), sp[1] mekan
        bas, bit = ortak.tarih_bul(sp[0], bugun)
        if not bas:
            continue
        if len(sp) > 1 and "-" in sp[0] and re.search(r"\d{4}\s*-\s*\d", sp[0]):
            ikinci = re.findall(r"\d{1,2} \w+ \d{4}", sp[0])
            if len(ikinci) > 1:
                bit, _ = ortak.tarih_bul(ikinci[1], bugun)
        etiket = re.search(r'class="[^"]*eventTag">([^<]*)<', blok)
        resim = re.search(r"url=%2Fuploads%2F([^&\"]+)&", blok)
        mekan = ortak.temizle(sp[1]).title() if len(sp) > 1 else None
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(sp[0]),
            "mekan": mekan,
            "ilce": salon_ilce(mekan or "", "Yenişehir"),
            "kategori": ortak.kategori_tahmin(ad + " " + (etiket[1] if etiket else "")),
            "ucretsiz": True if "ücretsiz" in ortak.kucuk(blok) else None,
            "gorsel": BEL + "/uploads/" + resim[1] if resim else None,
            "url": BEL + link[1],
        }


# ------------------------------------------------------------------
# 2) Dicle Üniversitesi — etkinlik listesi (HTML), tarih "30.10.2026 - 01.11.2026"
# ------------------------------------------------------------------
DICLE = "https://www.dicle.edu.tr"


def dicle(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('class="col-lg-3 col-md-3 shadow newscol"')[1:]:
        link = re.search(r"<a href='(/etkinlikler/[^']+)'", blok)
        h5 = re.search(r"<h5[^>]*>(.*?)</h5>", blok, re.S)
        if not (link and h5):
            continue
        metin = ortak.temizle(h5[1])
        tarihler = re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", metin)
        if not tarihler:
            continue
        bas, _ = ortak.tarih_bul(tarihler[0], bugun)
        bit, _ = ortak.tarih_bul(tarihler[-1], bugun)
        ad = basliklar(metin.split(tarihler[0])[0].strip(" -"))
        resim = re.search(r"<img src='([^']+)'", blok)
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bas and bit > bas else None,
            "mekan": "Dicle Üniversitesi",
            "ilce": "Sur",
            "gorsel": DICLE + urllib.parse.quote(resim[1]) if resim else None,
            "url": DICLE + urllib.parse.quote(link[1], safe="/%!"),
        }


KAYNAKLAR = [
    {"ad": "Diyarbakır Büyükşehir Belediyesi", "tur": "belediye", "url": BEL + "/etkinlikler", "cek": belediye},
    {"ad": "Dicle Üniversitesi", "tur": "universite", "url": DICLE + "/etkinlikler/tumu", "cek": dicle},
    {"ad": "Diyarbakır İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://diyarbakir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Diyarbakır", "ilce_bul": salon_ilce, "varsayilan_ilce": "Yenişehir"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/diyarbakir", "cek": etkinlik_io,
     "sehir": "Diyarbakır", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kayapınar Belediyesi", "tur": "belediye", "ilce": "Kayapınar", "url": "https://www.kayapinar.bel.tr",
     "not": "sadece olmuş etkinliklerin haberleri; takvim yok"},
    {"ad": "Yenişehir Belediyesi", "tur": "belediye", "ilce": "Yenişehir", "url": "https://www.yenisehir.bel.tr",
     "not": "sadece olmuş etkinliklerin haberleri; takvim yok"},
    {"ad": "Sur Belediyesi", "tur": "belediye", "ilce": "Sur", "url": "https://www.sur.bel.tr/etkinlik", "not": "etkinlik sayfası var ama okunmuyor"},
    {"ad": "Bağlar Belediyesi", "tur": "belediye", "ilce": "Bağlar", "url": "https://www.bagliar.bel.tr", "not": "site açılmıyor"},
    {"ad": "Diyarbakır Valiliği", "tur": "valilik", "url": "https://www.diyarbakir.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "16 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Sur Kültür Yolu Festivali, Diyarbakır Kitap Fuarı", "tur": "diger", "url": None,
     "not": "yıllık; 2026 tarihleri kontrol edilemedi"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
