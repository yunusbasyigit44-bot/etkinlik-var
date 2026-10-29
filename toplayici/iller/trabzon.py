"""Trabzon kaynakları (plaka 61). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Karadeniz Teknik Üniversitesi (ana sayfadaki yaklaşan etkinlik kartları), Trabzon Üniversitesi
(etkinlik listesi; tarih açıklama metninde). Trabzon Büyükşehir etkinlik sayfası sadece afiş + kayıt sistemi
(metinsiz, ajax), bu yüzden okunmuyor. Devlet Tiyatroları sahnesi var; kaynak listede.
"""
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Ortahisar", "Akçaabat", "Araklı", "Arsin", "Beşikdüzü", "Çarşıbaşı", "Çaykara", "Dernekpazarı", "Düzköy",
           "Hayrat", "Köprübaşı", "Maçka", "Of", "Sürmene", "Şalpazarı", "Tonya", "Vakfıkebir", "Yomra"]
SALON_ILCE = {"ktü": "Ortahisar", "karadeniz teknik": "Ortahisar", "trabzon üniversitesi": "Ortahisar", "goloğlu": "Ortahisar",
              "hamamizade": "Ortahisar", "devlet tiyatro": "Ortahisar", "fakülte": "Ortahisar", "amfi": "Ortahisar"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Karadeniz Teknik Üniversitesi — ana sayfadaki etkinlik kartları (gün, ay, başlık, yer, saat)
# ------------------------------------------------------------------
KTU = "https://www.ktu.edu.tr"


def ktu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in re.split(r'<a class="col" href="(?=/[^"]+/etkinlik/)', sayfa)[1:]:
        link = re.match(r'([^"]+)"', blok)
        gun = re.search(r">\s*(\d{1,2})\s*</div>\s*<p[^>]*>\s*([^<]+?)\s*</p>", blok)
        baslik = re.search(r"<h5[^>]*>(.*?)</h5>", blok, re.S)
        if not (link and gun and baslik):
            continue
        bas, _ = ortak.tarih_bul(f"{gun[1]} {gun[2]}", bugun)
        if not bas:
            continue
        yer = re.search(r'fa-map-marker-alt"></i>\s*</div>\s*<div[^>]*>\s*([^<]*?)\s*</div>', blok, re.S)
        saat = re.search(r'fa-clock"></i>\s*([0-9]{1,2}:[0-9]{2})', blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        mekan = ortak.temizle(yer[1]) if yer and ortak.temizle(yer[1]) else "Karadeniz Teknik Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": saat[1] if saat else None,
            "mekan": mekan,
            "ilce": "Ortahisar",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": resim[1] if resim else None,
            "url": urllib.parse.urljoin(KTU + "/", link[1]),
        }


# ------------------------------------------------------------------
# 2) Trabzon Üniversitesi — etkinlik listesi (tarih/yer açıklama metninde)
# ------------------------------------------------------------------
TU = "https://www.trabzon.edu.tr"


def trabzon_uni(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("<li>")[1:]:
        link = re.search(r'<a href="(/Etkinlik/\d+)"', blok)
        baslik = re.search(r"<h2>(.*?)</h2>", blok, re.S)
        icerik = re.search(r'info-content[^>]*>(.*?)</div>', blok, re.S)
        if not (link and baslik and icerik):
            continue
        metin = ortak.temizle(html.unescape(icerik[1]))
        bas, bit = ortak.tarih_bul(metin, bugun)
        if not bas:
            continue
        yer = re.search(r"(?:Yer|📍)\s*:?\s*(.+?)(?:\s+(?:Saat|Tarih)\b|$)", metin)
        resim = re.search(r'<img src="(/storage/[^"]+)"', blok)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = ortak.temizle(yer[1])[:80] if yer else "Trabzon Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(re.sub(r"\d{1,2} \w+ 20\d\d", " ", metin)),
            "mekan": mekan,
            "ilce": "Ortahisar",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": TU + resim[1] if resim else None,
            "url": TU + link[1],
        }


KAYNAKLAR = [
    {"ad": "Karadeniz Teknik Üniversitesi", "tur": "universite", "url": KTU, "cek": ktu},
    {"ad": "Trabzon Üniversitesi", "tur": "universite", "url": TU + "/etkinlik/", "cek": trabzon_uni},
    {"ad": "Trabzon İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://trabzon.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Trabzon", "ilce_bul": salon_ilce, "varsayilan_ilce": "Ortahisar"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/trabzon", "cek": etkinlik_io,
     "sehir": "Trabzon", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Trabzon Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.trabzon.bel.tr",
     "not": "etkinlikler sadece afiş görseli ve kayıt sistemi (metin/tarih yok); okunmuyor"},
    {"ad": "Trabzon Büyükşehir Şehir Tiyatrosu, Hamamizade İhsan Bey Kültür Merkezi", "tur": "belediye", "url": None,
     "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Ortahisar ve Akçaabat belediyeleri", "tur": "belediye", "url": "https://www.ortahisar.bel.tr",
     "not": "etkinlik takvimi yok / okunamadı"},
    {"ad": "Trabzon Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.trabzon.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Uluslararası Trabzon Film Festivali, Kadırga Yaylası Şenlikleri, Sera Gölü…)", "tur": "diger",
     "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
