"""Ağrı kaynakları (plaka 04). Kaynak haritası: 2026-10-29.

Tek düzenli kaynak Ağrı İbrahim Çeçen Üniversitesi'nin etkinlik listesi. Belediyenin etkinlik takvimi boş.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Diyadin", "Doğubayazıt", "Eleşkirt", "Hamur", "Patnos", "Taşlıçay", "Tutak"]
SALON_ILCE = {"aiçü": "Merkez", "ibrahim çeçen": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# Ağrı İbrahim Çeçen Üniversitesi — "Tüm Etkinlikler" listesi (HTML)
def aicu(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for satir in re.findall(r"<tr>(.*?)</tr>", sayfa, re.S):
        link = re.search(r'<a href="(detail\.aspx\?id=\d+[^"]*)"[^>]*>(.*?)</a>', satir, re.S)
        tarih = re.search(r"(\d{2}\.\d{2}\.\d{4})", satir)
        if not (link and tarih):
            continue
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        yield {
            "baslik": basliklar(ortak.temizle(link[2])),
            "tarih": bas,
            "mekan": "Ağrı İbrahim Çeçen Üniversitesi",
            "ilce": "Merkez",
            "url": "https://www.agri.edu.tr/" + link[1].replace("&amp;", "&"),
        }


KAYNAKLAR = [
    {"ad": "Ağrı İbrahim Çeçen Üniversitesi", "tur": "universite", "url": "https://www.agri.edu.tr/haberduyuru.aspx?bid=1&tid=3", "cek": aicu},
    {"ad": "Ağrı İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://agri.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Ağrı", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/agri", "cek": etkinlik_io,
     "sehir": "Ağrı", "ilce_bul": salon_ilce},
    {"ad": "Ağrı Belediyesi", "tur": "belediye", "url": "https://www.agri.bel.tr/etkinlikler/", "not": "etkinlik takvimi boş (kayıtlı içerik yok)"},
    {"ad": "Ağrı Valiliği", "tur": "valilik", "url": "https://www.agri.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "8 ilçe kaymakamlığı ve belediyeleri (Doğubayazıt, Patnos…)", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Doğubayazıt Ahmed-i Hânî anma etkinlikleri, Ağrı Dağı tırmanışları", "tur": "diger", "url": None,
     "not": "yıllık; resmî program henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
