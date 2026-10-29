"""Eskişehir kaynakları (plaka 26). Kaynak haritası: 2026-10-29.

Çalışan kaynaklar: Eskişehir Şehir Tiyatroları (aylık oyun takvimi), Anadolu Üniversitesi (etkinlik listesi),
Tepebaşı Belediyesi (etkinlik kartları). Büyükşehir'in etkinlik RSS'i boş, Odunpazarı sayfası okunmuyor.
Eskişehir'de Devlet Tiyatroları sahnesi yok; kaynak listede, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import html
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Odunpazarı", "Tepebaşı", "Alpu", "Beylikova", "Çifteler", "Günyüzü", "Han", "İnönü", "Mahmudiye",
           "Mihalgazi", "Mihalıççık", "Sarıcakaya", "Seyitgazi", "Sivrihisar"]
SALON_ILCE = {"anadolu üniversitesi": "Tepebaşı", "sanat sokağı": "Tepebaşı", "genco erkal": "Tepebaşı",
              "yunus emre": "Tepebaşı", "haller": "Odunpazarı", "osmangazi": "Odunpazarı", "estü": "Odunpazarı",
              "eskişehir teknik": "Odunpazarı", "tiyatro": "Tepebaşı"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Eskişehir Şehir Tiyatroları — aylık oyun programı (HTML, gün gün pencereler)
# ------------------------------------------------------------------
TIYATRO = "https://tiyatro.eskisehir.bel.tr/"
_SATIR = re.compile(
    r'class="oyunlar_sty">([^<]*)</td>\s*<td[^>]*>\|</td>\s*<td[^>]*class="oyunlar_sty">([^<]+)</td>'
    r'\s*<td[^>]*>\|</td>\s*<td[^>]*class="oyunlar_sty">([^<]*)</td>')


def tiyatro(kaynak, bugun):
    adresler = [TIYATRO + "oyuntakvimi.php"]
    y, a = bugun.year, bugun.month
    for _ in range(2):                      # sonraki 2 ay
        y, a = (y + 1, 1) if a == 12 else (y, a + 1)
        adresler.append(TIYATRO + f"glckaytakvimi.php?gdnsorgu={y}-{a:02d}")
    goruldu = set()
    for adres in adresler:
        try:
            sayfa = ortak.indir(adres)
        except Exception as hata:
            print("   tiyatro sayfası alınamadı:", adres, hata)
            continue
        for blok in re.split(r"<h4 class='modal-title'>", sayfa)[1:]:
            gun = re.match(r"(\d{2})-(\d{2})-(\d{4})", blok)
            if not gun:
                continue
            tarih = dt.date(int(gun[3]), int(gun[2]), int(gun[1]))
            for saat, ad, sahne in _SATIR.findall(blok):
                ad = basliklar(ortak.temizle(ad))
                if not ad or (ad, tarih, saat) in goruldu:
                    continue
                goruldu.add((ad, tarih, saat))
                sahne = ortak.temizle(sahne)
                yield {
                    "baslik": ad,
                    "tarih": tarih,
                    "saat": ortak.saat_bul(saat),
                    "mekan": sahne or "Eskişehir Şehir Tiyatroları",
                    "ilce": salon_ilce(sahne, "Tepebaşı"),
                    "kategori": "Tiyatro",
                    "ucretsiz": False,
                    "url": "https://www.biletinial.com/eskisehir-sehir-tiyatrolari",
                    "ozet": "Eskişehir Büyükşehir Belediyesi Şehir Tiyatroları",
                }


# ------------------------------------------------------------------
# 2) Anadolu Üniversitesi — etkinlik listesi (HTML, sayfalı)
# ------------------------------------------------------------------
def anadolu(kaynak, bugun):
    goruldu = set()
    for sayfa_no in (1, 2, 3):
        sayfa = ortak.indir(kaynak["url"] + ("" if sayfa_no == 1 else f"?page={sayfa_no}"))
        for blok in sayfa.split('<div class="event">')[1:]:
            link = re.search(r'<div class="headLine">\s*<a href="([^"]+)">(.*?)</a>', blok, re.S)
            zaman = re.search(r'class="calendar">\s*Tarih:\s*([^<]+)<', blok)
            if not (link and zaman) or link[1] in goruldu:
                continue
            goruldu.add(link[1])
            metin = zaman[1]
            tarihler = re.findall(r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}", metin)
            bas, _ = ortak.tarih_bul(tarihler[0], bugun) if tarihler else (None, None)
            bit, _ = ortak.tarih_bul(tarihler[1], bugun) if len(tarihler) > 1 else (None, None)
            if not bas:
                continue
            resim = re.search(r'data-src="([^"]+)"', blok)
            kat = re.search(r'class="category">\s*<a[^>]*>([^<]+)<', blok)
            ad = basliklar(ortak.temizle(link[2]).strip(' "“”'))
            yield {
                "baslik": ad,
                "tarih": bas,
                "bitis": bit if bit and bit > bas else None,
                "saat": ortak.saat_bul(re.sub(r"^\s*\d{1,2}\s+\w+\s+\d{4}", "", metin)),
                "mekan": "Anadolu Üniversitesi",
                "ilce": "Tepebaşı",
                "kategori": ortak.kategori_tahmin(ad + " " + (kat[1] if kat else "")),
                "gorsel": "https://www.anadolu.edu.tr" + resim[1] if resim and resim[1].startswith("/") else None,
                "url": "https://www.anadolu.edu.tr" + link[1],
                "ozet": ortak.temizle(kat[1]) if kat else None,
            }


# ------------------------------------------------------------------
# 3) Tepebaşı Belediyesi — etkinlik kartları (HTML)
# ------------------------------------------------------------------
def tepebasi(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split("etkinlik-card-body")[1:]:
        link = re.search(r'<h4 class="card-title[^>]*><a[^>]*href="([^"]+)">(.*?)</a>', blok, re.S)
        gun = re.search(r">\s*event\s*</i>.*?<span>([^<]+)</span>", blok, re.S)
        saat = re.search(r">\s*schedule\s*</i>.*?<span>([^<]+)</span>", blok, re.S)
        yer = re.search(r">\s*(?:location_on|place)\s*</i>.*?<span>([^<]+)</span>", blok, re.S)
        if not (link and gun):
            continue
        bas, _ = ortak.tarih_bul(html.unescape(gun[1]), bugun)
        if not bas:
            continue
        mekan = ortak.temizle(yer[1]) if yer else None
        yield {
            "baslik": basliklar(ortak.temizle(link[2])),
            "tarih": bas,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": mekan,
            "ilce": "Tepebaşı",
            "url": "https://www.tepebasi.bel.tr" + link[1],
        }


KAYNAKLAR = [
    {"ad": "Eskişehir Şehir Tiyatroları", "tur": "belediye", "url": TIYATRO + "oyuntakvimi.php", "cek": tiyatro},
    {"ad": "Anadolu Üniversitesi", "tur": "universite", "url": "https://www.anadolu.edu.tr/etkinlikler", "cek": anadolu},
    {"ad": "Tepebaşı Belediyesi", "tur": "belediye", "ilce": "Tepebaşı", "url": "https://www.tepebasi.bel.tr/Etkinlikler", "cek": tepebasi},
    {"ad": "Eskişehir İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://eskisehir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Eskişehir", "ilce_bul": salon_ilce, "varsayilan_ilce": "Tepebaşı"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/eskisehir", "cek": etkinlik_io,
     "sehir": "Eskişehir", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Eskişehir Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.eskisehir.bel.tr/tum-etkinlikler",
     "not": "etkinlik RSS'i ve listesi boş dönüyor; Şehir Tiyatroları ayrıca okunuyor"},
    {"ad": "Odunpazarı Belediyesi", "tur": "belediye", "ilce": "Odunpazarı", "url": "https://www.odunpazari.bel.tr/guncel/etkinlikler",
     "not": "etkinlik sayfası var ama otomatik okunmuyor"},
    {"ad": "Eskişehir Osmangazi Üniversitesi", "tur": "universite", "url": "https://www.ogu.edu.tr",
     "not": "etkinlik sayfası otomatik okunmuyor"},
    {"ad": "Eskişehir Teknik Üniversitesi", "tur": "universite", "url": "https://www.eskisehir.edu.tr/tr/Etkinlik",
     "not": "yaklaşan etkinlik yok / okunmuyor"},
    {"ad": "Eskişehir Valiliği ve 13 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.eskisehir.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://eskisehir.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://eskisehir.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık festivaller (Uluslararası Eskişehir Festivali, Uçan Balon, Sivrihisar Nasreddin Hoca…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
