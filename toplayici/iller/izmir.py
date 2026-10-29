"""İzmir kaynakları (plaka 35). Kaynak haritası: 2026-10-29.

İzmir Büyükşehir "Kültür Sanat" sitesinin herkese açık program verisi (İzmir Sanat, Şehir Tiyatroları, AASSM,
Elhamra, Aziz Vukolos, sergiler hep burada) ve Konak Belediyesi etkinlik sayfası okunur.
Devlet Opera ve Balesi ortak kaynakla gelir; Devlet Tiyatroları İzmir sahnesi ortak kaynakla gelir.
"""
import datetime as dt
import html
import json
import re

import ortak
from ortak_kaynaklar import basliklar, devlet_opera, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Aliağa", "Balçova", "Bayındır", "Bayraklı", "Bergama", "Beydağ", "Bornova", "Buca", "Çeşme", "Çiğli", "Dikili",
           "Foça", "Gaziemir", "Güzelbahçe", "Karabağlar", "Karaburun", "Karşıyaka", "Kemalpaşa", "Kınık", "Kiraz", "Konak",
           "Menderes", "Menemen", "Narlıdere", "Ödemiş", "Seferihisar", "Selçuk", "Tire", "Torbalı", "Urla"]
SALON_ILCE = {"ahmed adnan saygun": "Konak", "aassm": "Konak", "elhamra": "Konak", "aziz vukolos": "Konak",
              "ayavukla": "Konak", "kültürpark": "Konak", "ismet inönü": "Konak", "i̇smet inönü": "Konak",
              "ismet i̇nönü": "Konak", "izbbşt": "Konak", "vasıf çınar": "Konak", "ışılay saygın": "Konak",
              "konak metro": "Konak", "pakistan pavyonu": "Konak", "atlas pavyonu": "Konak", "kemeraltı": "Konak",
              "bostanlı": "Karşıyaka", "cem yazan": "Kiraz", "devlet tiyatro": "Konak", "opera": "Konak",
              "dokuz eylül": "Buca", "ege üniversitesi": "Bornova", "bornova": "Bornova"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KS_API = "https://kultursanatapi.izmir.bel.tr/api/"


# ------------------------------------------------------------------
# 1) İzmir Büyükşehir Kültür Sanat — sitenin kendi kullandığı herkese açık program verisi (JSON)
#    Her kayıt bir seans: tiyatro, konser, sergi, sinematek, festival...
# ------------------------------------------------------------------
def _kategori(baslik, kategoriler):
    k = ortak.kategori_tahmin(baslik)
    return ortak.kategori_tahmin(kategoriler) if k in ("Diğer", "Spor") else k


def kultursanat(kaynak, bugun):
    seanslar = json.loads(ortak.indir(KS_API + "session/list")).get("data") or []
    for s in seanslar:
        ad = ortak.temizle((s.get("event") or {}).get("name") or "")
        if not ad:
            continue
        try:
            bas = dt.datetime.fromisoformat(s["eventDate"])
            bit = dt.datetime.fromisoformat(s["eventEndDate"]) if s.get("eventEndDate") else None
        except (KeyError, ValueError):
            continue
        mekan = ortak.temizle((s.get("venue") or {}).get("name") or "")
        kategoriler = " ".join(c.get("name", "") for c in (s.get("categories") or []))
        sergi = "sergi" in ortak.kucuk(kategoriler + " " + ad)
        baslik = basliklar(ad)
        yield {
            "baslik": baslik,
            "tarih": bas.date(),
            "bitis": bit.date() if bit and bit.date() > bas.date() else None,
            "saat": None if sergi else bas.strftime("%H:%M"),
            "mekan": mekan or None,
            "ilce": salon_ilce(mekan, None),
            "kategori": _kategori(baslik, kategoriler),
            "ucretsiz": False if s.get("sessionType") == 0 else None,   # 0 = biletli seans (salon etkinliği)
            "gorsel": s.get("eventImageUrl") or None,
            "url": "https://kultursanat.izmir.bel.tr/",
        }


# ------------------------------------------------------------------
# 2) Konak Belediyesi — etkinlik listesi (HTML), tarih "26 Ekim - 17 Kasım 2026" ya da "22-23 Ekim 2026"
# ------------------------------------------------------------------
def _konak_tarih(metin, bugun):
    yil = re.search(r"(\d{4})", metin)
    parcalar = [p.strip() for p in metin.split("-")]
    bitis_p = parcalar[-1]
    bit, _ = ortak.tarih_bul(bitis_p, bugun)
    ay_son = re.search(r"([^\d\s]+)\s*(\d{4})?\s*$", bitis_p)
    ilk = parcalar[0]
    if len(parcalar) > 1 and not re.search(r"[^\d\s]", ilk) and ay_son:
        ilk = f"{ilk} {ay_son[1]}"          # "22-23 Ekim" -> "22 Ekim"
    bas, _ = ortak.tarih_bul(ilk + (" " + yil[1] if yil else ""), bugun)
    return bas, bit


def konak(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('class="activity-item"')[1:]:
        t = re.search(r"content-meta\">\s*<p>([^<]+)</p>", blok)
        a = re.search(r'<a href="([^"]+/etkinlik/[^"]+)"[^>]*>\s*<h4>(.*?)</h4>', blok, re.S)
        if not (t and a):
            continue
        bas, bit = _konak_tarih(ortak.temizle(t[1]), bugun)
        if not bas:
            continue
        resim = re.search(r'<img src="([^"]*/upload/activity/[^"]+)"', blok)
        gorsel = resim[1].replace(" ", "%20") if resim and not resim[1].endswith(".jfif") else None
        ad = basliklar(ortak.temizle(html.unescape(a[2])))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "mekan": "Konak Belediyesi",
            "ilce": "Konak",
            "kategori": ortak.kategori_tahmin(ad),
            "gorsel": gorsel,
            "url": a[1],
            "ucretsiz": True,
        }


KAYNAKLAR = [
    {"ad": "İzmir Büyükşehir Kültür Sanat (İzmir Sanat, Şehir Tiyatroları, AASSM, Elhamra)", "tur": "belediye",
     "url": "https://kultursanat.izmir.bel.tr/", "cek": kultursanat},
    {"ad": "Konak Belediyesi", "tur": "belediye", "ilce": "Konak", "url": "https://www.konak.bel.tr/tr/etkinlikler", "cek": konak},
    {"ad": "İzmir İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://izmir.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "İzmir", "ilce_bul": salon_ilce, "varsayilan_ilce": "Konak"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/izmir", "cek": etkinlik_io,
     "sehir": "İzmir", "ilce_bul": salon_ilce},
    {"ad": "Devlet Opera ve Balesi", "tur": "kultur", "url": "https://www.operabale.gov.tr", "cek": devlet_opera,
     "mudurluk": 3, "ilce_bul": salon_ilce, "varsayilan_ilce": "Konak"},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bornova Belediyesi", "tur": "belediye", "ilce": "Bornova", "url": "https://bornova.bel.tr/etkinlikler",
     "not": "etkinlikler sayfada JavaScript ile yükleniyor; otomatik okunmuyor"},
    {"ad": "Karşıyaka Belediyesi", "tur": "belediye", "ilce": "Karşıyaka", "url": "https://www.karsiyaka.bel.tr/etkinlikler",
     "not": "etkinlik listesi tarihsiz haber sayfaları; otomatik okunmuyor"},
    {"ad": "Dokuz Eylül Üniversitesi", "tur": "universite", "ilce": "Buca", "url": "https://www.deu.edu.tr",
     "not": "etkinlik takvimi ana sayfada yok; duyurular idari — okunmuyor"},
    {"ad": "Ege Üniversitesi", "tur": "universite", "ilce": "Bornova", "url": "https://www.ege.edu.tr",
     "not": "etkinlik takvimi ana sayfada yok — okunmuyor"},
    {"ad": "Buca, Bayraklı, Çiğli, Karabağlar, Çeşme, Urla belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi bakılmadı (sonraki tur)"},
    {"ad": "İzmir Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.izmir.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "İzmir Enternasyonal Fuarı, Kemeraltı Festivali, Çeşme Müzik Festivali, Selçuk Efes Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
