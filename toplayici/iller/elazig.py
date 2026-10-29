"""Elazığ kaynakları (plaka 23). Kaynak haritası: 2026-10-29.

Çalışan: Fırat Üniversitesi etkinlik listesi (konservatuvar konserleri, kongreler). Elazığ Belediyesi'nin
etkinlik sayfası var ama son kayıt Şubat 2026. Devlet Tiyatroları sahnesi yok; kaynak listede duruyor.
"""
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ağın", "Alacakaya", "Arıcak", "Baskil", "Karakoçan", "Keban", "Kovancılar", "Maden", "Palu", "Sivrice"]
SALON_ILCE = {"fırat üniversitesi": "Merkez", "atatürk kültür merkezi": "Merkez", "50. yıl parkı": "Merkez",
              "harput": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# Fırat Üniversitesi — etkinlik listesi (HTML), tarih "START DATE: 2026-06-11 20:00:00"
# ------------------------------------------------------------------
def firat(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('class="blog-item"')[1:]:
        link = re.search(r'<h3 class="title"><a href="([^"]+)"[^>]*>(.*?)</a>', blok, re.S)
        bas_m = re.search(r"START DATE:\s*(\d{4}-\d{2}-\d{2})(?: (\d{2}:\d{2}))?", blok)
        if not (link and bas_m):
            continue
        bit_m = re.search(r"END DATE:\s*(\d{4}-\d{2}-\d{2})", blok)
        bas, _ = ortak.tarih_bul(bas_m[1], bugun)
        bit, _ = ortak.tarih_bul(bit_m[1], bugun) if bit_m else (None, None)
        yer = re.search(r"YER:\s*([^<]+)", blok)
        resim = re.search(r'<img[^>]+src="(https://www\.firat\.edu\.tr/images/event/[^"]+)"', blok)
        mekan = ortak.temizle(yer[1]) if yer else "Fırat Üniversitesi"
        ad = basliklar(ortak.temizle(link[2]))
        saat = bas_m[2] if bas_m[2] and bas_m[2] != "00:00" else None
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": saat,
            "mekan": mekan,
            "ilce": salon_ilce(mekan, "Merkez"),
            "gorsel": resim[1] if resim else None,
            "url": link[1],
        }


KAYNAKLAR = [
    {"ad": "Fırat Üniversitesi", "tur": "universite", "url": "https://www.firat.edu.tr/page/event", "cek": firat},
    {"ad": "Elazığ İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://elazig.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Elazığ", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/elazig", "cek": etkinlik_io,
     "sehir": "Elazığ", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Elazığ Belediyesi", "tur": "belediye", "url": "https://www.elazig.bel.tr/etkinlik",
     "not": "etkinlik sayfası var ama güncel değil (son kayıt Şubat 2026)"},
    {"ad": "Elazığ Valiliği", "tur": "valilik", "url": "https://www.elazig.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "11 ilçe kaymakamlığı ve belediyeleri", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Fırat Kısa Film Festivali, Hazar Şiir Akşamları, Elazığ Gastronomi Festivali, Baskil Kayısı Festivali", "tur": "diger",
     "url": None, "not": "yıllık; 2026-27 tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
