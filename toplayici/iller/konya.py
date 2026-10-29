"""Konya kaynakları (plaka 42). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: Konya Büyükşehir Belediyesi etkinlik listesi (Kültür Sanat Konya), Necmettin Erbakan Üniversitesi.
Devlet Tiyatroları Konya sahnesi ayrıca izlenir. Selçuk Üniversitesi ve ilçe belediyeleri okunmuyor.
"""
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Akören", "Akşehir", "Altınekin", "Beyşehir", "Bozkır", "Cihanbeyli", "Çeltik", "Çumra", "Derbent", "Derebucak",
           "Doğanhisar", "Emirgazi", "Ereğli", "Güneysınır", "Hadim", "Halkapınar", "Hüyük", "Ilgın", "Kadınhanı", "Karapınar",
           "Karatay", "Kulu", "Meram", "Sarayönü", "Selçuklu", "Seydişehir", "Taşkent", "Tuzlukçu", "Yalıhüyük", "Yunak"]
SALON_ILCE = {"mevlana kültür": "Selçuklu", "mevlana müzesi": "Karatay", "erbakan": "Meram", "selçuk üniversitesi": "Selçuklu",
              "tüyap": "Selçuklu", "devlet tiyatro": "Selçuklu", "şehir tiyatro": "Selçuklu", "konya devlet": "Selçuklu",
              "aladdin": "Karatay", "alaaddin": "Karatay", "şems": "Karatay", "sema": "Karatay"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Konya Büyükşehir Belediyesi — etkinlik kartları (HTML, 3 sayfa)
# ------------------------------------------------------------------
def buyuksehir(kaynak, bugun):
    gorulen = set()
    for sayfa_no in (1, 2, 3):
        url = kaynak["url"] + ("" if sayfa_no == 1 else f"?sayfa={sayfa_no}")
        sayfa = ortak.indir(url)
        bloklar = sayfa.split('<div class="tiyatro-card">')[1:]
        if not bloklar:
            break
        for blok in bloklar:
            a = re.search(r'<a href="([^"]+)"[^>]*>\s*<img src="([^"]*)"[^>]*>\s*<h3>(.*?)</h3>', blok, re.S)
            t = re.search(r'class="date">([^<]+)<', blok)
            if not (a and t) or a[1] in gorulen:
                continue
            gorulen.add(a[1])
            bas, _ = ortak.tarih_bul(t[1], bugun)
            if not bas:
                continue
            tur = re.search(r'class="tag">([^<]+)<', blok)
            ad = basliklar(ortak.temizle(a[3]))
            yield {
                "baslik": ad,
                "tarih": bas,
                "mekan": "Konya Büyükşehir Belediyesi Kültür Sanat",
                "ilce": "Selçuklu",   # başlığa bakılmaz: "Konya Okulu" içinde "Kulu" ilçesi geçiyor
                "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
                "gorsel": html.unescape(a[2]) or None,
                "url": a[1],
            }


# ------------------------------------------------------------------
# 2) Necmettin Erbakan Üniversitesi — etkinlik listesi (HTML)
# ------------------------------------------------------------------
def erbakan(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="tarih mt-3">')[1:]:
        t = re.match(r"(.*?)</div>", blok, re.S)
        a = re.search(r'<a href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', blok, re.S)
        if not (t and a):
            continue
        bas, _ = ortak.tarih_bul(ortak.temizle(t[1]), bugun)
        if not bas:
            continue
        birim = re.search(r'class="birim mt-3">([^<]+)<', blok)
        ad = basliklar(ortak.temizle(a[2]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(ortak.temizle(t[1])),
            "mekan": "Necmettin Erbakan Üniversitesi",
            "ilce": "Meram",
            "kategori": ortak.kategori_tahmin(ad + " " + (birim[1] if birim else "")),
            "url": a[1],
            "ucretsiz": True,
            "ozet": ortak.temizle(birim[1]) if birim else None,
        }


KAYNAKLAR = [
    {"ad": "Konya Büyükşehir Belediyesi (Kültür Sanat Konya)", "tur": "belediye", "url": "https://www.konya.bel.tr/etkinlik", "cek": buyuksehir},
    {"ad": "Necmettin Erbakan Üniversitesi", "tur": "universite", "ilce": "Meram", "url": "https://erbakan.edu.tr/tr/etkinlikler", "cek": erbakan},
    {"ad": "Konya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://konya.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Konya", "ilce_bul": salon_ilce, "varsayilan_ilce": "Selçuklu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/konya", "cek": etkinlik_io,
     "sehir": "Konya", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Selçuk Üniversitesi", "tur": "universite", "ilce": "Selçuklu", "url": "https://www.selcuk.edu.tr",
     "not": "etkinlik takvimi ana sayfada yok; okunmuyor"},
    {"ad": "Selçuklu, Meram, Karatay belediyeleri", "tur": "belediye", "url": "https://www.selcuklu.bel.tr",
     "not": "okunabilir etkinlik takvimi bulunamadı (sonraki tur)"},
    {"ad": "Konya Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.konya.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://konya.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Şeb-i Arus (Mevlana anma törenleri), Konya Kitap Fuarı…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış (Şeb-i Arus aralık ayında)"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
