"""Balıkesir kaynakları (plaka 10). Kaynak haritası: 2026-10-29.

Verimli kaynaklar: Balıkesir Üniversitesi etkinlik platformunun herkese açık JSON uçları ve
Bandırma Onyedi Eylül Üniversitesi etkinlik listesi. Büyükşehir belediyesi siteleri okunabilir etkinlik takvimi vermiyor.
"""
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Altıeylül", "Karesi", "Ayvalık", "Balya", "Bandırma", "Bigadiç", "Burhaniye", "Dursunbey", "Edremit", "Erdek",
           "Gömeç", "Gönen", "Havran", "İvrindi", "Kepsut", "Manyas", "Marmara", "Savaştepe", "Sındırgı", "Susurluk"]
SALON_ILCE = {"necatibey": "Karesi", "altınoluk": "Edremit", "atatürk kongre": "Altıeylül", "baün": "Altıeylül",
              "balıkesir üniversitesi": "Altıeylül", "aziz sancar": "Bandırma", "onyedi eylül": "Bandırma"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

BAUN = "https://form-api.balikesir.edu.tr"


# ------------------------------------------------------------------
# Balıkesir Üniversitesi — etkinlik platformunun herkese açık JSON'u (sayfa sayfa)
# ------------------------------------------------------------------
def baun(kaynak, bugun):
    goruldu = set()
    for sayfa_no in range(1, 8):
        veri = json.loads(ortak.indir(f"{BAUN}/api/events?is_past=false&page={sayfa_no}"))
        liste = veri.get("data") or []
        if not liste:
            break
        for e in liste:
            baslik = ortak.temizle(e.get("Name") or "")
            zaman = (e.get("StartDatetime") or "")[:16]
            if not baslik or len(zaman) < 16 or (baslik, zaman) in goruldu:
                continue
            goruldu.add((baslik, zaman))
            tarih, _ = ortak.tarih_bul(f"{zaman[8:10]}.{zaman[5:7]}.{zaman[:4]}", bugun)
            saat = zaman[11:16]
            resim = e.get("ImagePath")
            mekan = ortak.temizle(e.get("EventPlace") or "") or "Balıkesir Üniversitesi"
            ad = basliklar(baslik)
            yield {
                "baslik": ad,
                "tarih": tarih,
                "saat": None if saat == "00:00" else saat,
                "mekan": mekan,
                "ilce": salon_ilce(mekan, "Altıeylül"),
                "kategori": ortak.kategori_tahmin(ad),
                "gorsel": BAUN + urllib.parse.quote(resim) if resim else None,
                "url": "https://etkinlik.balikesir.edu.tr/",
                "ozet": ortak.temizle((e.get("Unit") or "").title()) or None,
            }
        if sayfa_no * (veri.get("limit") or 10) >= (veri.get("total") or 0):
            break


# ------------------------------------------------------------------
# Bandırma Onyedi Eylül Üniversitesi — etkinlik listesi (HTML)
# ------------------------------------------------------------------
def bandirma(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<div class="etkinlik">')[1:]:
        gun = re.search(r'class="gun">(\d{1,2})<', blok)
        ay = re.search(r'class="ay">([^<]+)<', blok)
        yil = re.search(r'class="yil">(\d{4})<', blok)
        baslik = re.search(r'<a class="etkinlikLink" data-id="(\d+)"[^>]*data-slug="([^"]*)"[^>]*>(.*?)</a>', blok, re.S)
        if not (gun and ay and yil and baslik):
            continue
        tarih, _ = ortak.tarih_bul(f"{gun[1]} {ay[1]} {yil[1]}", bugun)
        saat = re.search(r"<b>Saat:</b>\s*([0-2]?\d:[0-5]\d)", blok)
        yer = re.search(r"<b>Yer:</b>\s*([^<]+)<", blok)
        mekan = ortak.temizle(yer[1]) if yer else "Bandırma Onyedi Eylül Üniversitesi"
        ad = basliklar(ortak.temizle(baslik[3]).strip("“” \""))
        yield {
            "baslik": ad,
            "tarih": tarih,
            "saat": saat[1] if saat else None,
            "mekan": mekan,
            "ilce": "Bandırma",
            "kategori": ortak.kategori_tahmin(ad),
            "url": f"https://www.bandirma.edu.tr/tr/www/Etkinlik/Liste/{baslik[2]}-{baslik[1]}?k=-1",
        }


KAYNAKLAR = [
    {"ad": "Balıkesir Üniversitesi", "tur": "universite", "url": "https://etkinlik.balikesir.edu.tr/", "cek": baun},
    {"ad": "Bandırma Onyedi Eylül Üniversitesi", "tur": "universite", "url": "https://www.bandirma.edu.tr/tr/www/Etkinlik/Liste?k=-1",
     "ilce": "Bandırma", "cek": bandirma},
    {"ad": "Balıkesir İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://balikesir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Balıkesir", "ilce_bul": salon_ilce, "varsayilan_ilce": "Altıeylül"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/balikesir", "cek": etkinlik_io,
     "sehir": "Balıkesir", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Balıkesir Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.balikesir.bel.tr",
     "not": "ana sayfada okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Altıeylül, Karesi, Edremit, Ayvalık belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi yok / otomatik okunmuyor"},
    {"ad": "Balıkesir Şehir Tiyatrosu, kültür merkezleri", "tur": "belediye", "url": None, "not": "oyun takvimi yayımlanmıyor"},
    {"ad": "Balıkesir Valiliği, ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.balikesir.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "İlçe festivalleri (Ayvalık Zeytin, Edremit Zeytin, Bandırma vb.)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
