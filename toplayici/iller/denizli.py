"""Denizli kaynakları (plaka 20). Kaynak haritası: 2026-10-29.

Çalışan: Pamukkale Üniversitesi (ana sayfadaki etkinlik kartları), Merkezefendi Belediyesi Kültür-Sanat,
Denizli Kültür A.Ş. (şehir tiyatrosu; şu an boş dönüyor). Büyükşehir sitesinin etkinlik verisi sayfa
içindeki bir API anahtarıyla çekiliyor; bu yüzden okunmuyor.
"""
import datetime as dt
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Pamukkale", "Merkezefendi", "Acıpayam", "Babadağ", "Baklan", "Bekilli", "Beyağaç", "Bozkurt", "Buldan",
           "Çal", "Çameli", "Çardak", "Çivril", "Güney", "Honaz", "Kale", "Sarayköy", "Serinhisar", "Tavas"]
SALON_ILCE = {"pamukkale üniversitesi": "Pamukkale", "paü": "Pamukkale", "hasan kasapoğlu": "Merkezefendi",
              "merkezefendi": "Merkezefendi", "hierapolis": "Pamukkale", "denizli açık hava": "Merkezefendi",
              "kongre ve kültür": "Pamukkale"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Pamukkale Üniversitesi — ana sayfadaki "PAÜ'de Etkinlikler" kartları (HTML)
# ------------------------------------------------------------------
def pau(kaynak, bugun):
    sayfa = ortak.indir("https://www.pau.edu.tr")
    for blok in sayfa.split("h-100 item")[1:]:
        baslik = re.search(r"<h4>(.*?)</h4>", blok, re.S)
        tarih = re.search(r'class="date">([^<]+)<', blok)
        link = re.search(r'href="(/pau/tr/etkinlik/[^"]+)"', blok)
        if not (baslik and tarih):
            continue
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        tur = re.search(r'class="type">([^<]*)<', blok)
        resim = re.search(r'<img src="(https?://[^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[1]))
        yer = re.search(r'class="p-3 location">\s*([^<]+?)\s*</div>', blok)
        mekan = ortak.temizle(yer[1]) if yer else "Pamukkale Üniversitesi"
        yield {
            "baslik": ad,
            "tarih": bas,
            "mekan": mekan,
            "ilce": "Pamukkale",
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": resim[1] if resim and "pauetkinlikBg" not in resim[1] else None,
            "url": "https://www.pau.edu.tr" + link[1] if link else kaynak["url"],
        }


# ------------------------------------------------------------------
# 2) Merkezefendi Belediyesi Kültür-Sanat — etkinlik kartları (HTML)
# ------------------------------------------------------------------
MK = "https://www.merkezefendi.bel.tr/kultursanat/"


def merkezefendi(kaynak, bugun):
    sayfa = ortak.indir(MK + "etkinlikler.aspx")
    for blok in sayfa.split('class="blog_post_style2"')[1:]:
        baslik = re.search(r'<h3><a href="(etkinlik\.aspx[^"]+)">(.*?)</a>', blok, re.S)
        tarih = re.search(r"Tarih:\s*([^<]+)<", blok)
        if not (baslik and tarih):
            continue
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        saat = re.search(r"Saat:\s*([^<]+)<", blok)
        tur = re.search(r"Türü:\s*([^<]+)<", blok)
        resim = re.search(r'<img src="([^"]+)"', blok)
        ad = basliklar(ortak.temizle(baslik[2]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "saat": ortak.saat_bul(saat[1]) if saat else None,
            "mekan": "Merkezefendi Kültür Merkezi",
            "ilce": "Merkezefendi",
            "kategori": ortak.kategori_tahmin(ad + " " + (tur[1] if tur else "")),
            "gorsel": urllib.parse.quote(urllib.parse.urljoin(MK, resim[1]), safe=":/%?=&") if resim else None,
            "url": MK + baslik[1],
        }


# ------------------------------------------------------------------
# 3) Denizli Kültür A.Ş. (şehir tiyatrosu, konserler) — sitenin kendi JSON'u
# ------------------------------------------------------------------
def kultur_as(kaynak, bugun):
    veri = json.loads(ortak.indir("https://denizlikultur.com/service.ashx?islem=dataTiyatroEtkinlikler"))
    for e in veri.get("data") or []:
        try:
            zaman = dt.datetime.fromisoformat(str(e["etkinliktarihi"]))
        except (KeyError, ValueError):
            continue
        mekan = e.get("salonadi") or "Denizli Kültür A.Ş."
        ad = basliklar(ortak.temizle(e.get("etkinlikicerik") or e.get("oyunadi") or "Etkinlik"))
        yield {
            "baslik": ad,
            "tarih": zaman.date(),
            "saat": zaman.strftime("%H:%M"),
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkezefendi"),
            "kategori": ortak.kategori_tahmin(ad + " " + (e.get("oyunadi") or "")),
            "ucretsiz": False,
            "url": "https://denizlikultur.com/Default.aspx",
        }


KAYNAKLAR = [
    {"ad": "Pamukkale Üniversitesi", "tur": "universite", "url": "https://www.pau.edu.tr/pau/tr/etkinlikler", "cek": pau},
    {"ad": "Merkezefendi Belediyesi Kültür-Sanat", "tur": "belediye", "ilce": "Merkezefendi", "url": MK + "etkinlikler.aspx", "cek": merkezefendi},
    {"ad": "Denizli Kültür A.Ş. (şehir tiyatrosu, konser)", "tur": "kultur", "url": "https://denizlikultur.com", "cek": kultur_as},
    {"ad": "Denizli İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://denizli.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Denizli", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkezefendi"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/denizli", "cek": etkinlik_io,
     "sehir": "Denizli", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Denizli Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.denizli.bel.tr/etkinlikler",
     "not": "etkinlik listesi sayfadaki bir API anahtarıyla yükleniyor; anahtarı kullanmıyoruz — okunamıyor"},
    {"ad": "Pamukkale Belediyesi", "tur": "belediye", "ilce": "Pamukkale", "url": "https://www.pamukkale.bel.tr",
     "not": "etkinlik takvimi yok; sadece olmuş etkinliklerin haberleri"},
    {"ad": "Denizli Valiliği", "tur": "valilik", "url": "https://www.denizli.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "17 ilçe kaymakamlığı ve belediyeleri", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Pamukkale Hierapolis konserleri, Denizli Kültür Sanat Festivali", "tur": "diger", "url": None,
     "not": "yıllık/dönemsel; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
