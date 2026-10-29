"""Afyonkarahisar kaynakları (plaka 03). Kaynak haritası: 2026-10-29.

En verimli kaynak Afyon Kocatepe Üniversitesi; belediyenin de gerçek bir etkinlik sayfası var.
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import datetime as dt
import html
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Başmakçı", "Bayat", "Bolvadin", "Çay", "Çobanlar", "Dazkırı", "Dinar", "Emirdağ", "Evciler",
           "Hocalar", "İhsaniye", "İscehisar", "Kızılören", "Sandıklı", "Sinanpaşa", "Sultandağı", "Şuhut"]
SALON_ILCE = {"aku": "Merkez", "kocatepe": "Merkez", "rıza çerçel": "Merkez", "afsü": "Merkez", "erbakan": "Merkez",
              "aziziye": "Emirdağ"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)


# ------------------------------------------------------------------
# 1) Afyon Kocatepe Üniversitesi — sadece yaklaşan etkinlikleri gösteren sayfa (HTML)
# ------------------------------------------------------------------
def aku(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in re.split(r'<div class="row etkinlikler"', sayfa)[1:]:
        baslik = re.search(r"<p[^>]*>\s*<b>(.*?)</b>", blok, re.S)

        def alan(ad):
            r = re.search(r"<b>\s*" + ad + r"[^<]*:\s*</b>\s*([^<]*)<", blok)
            return ortak.temizle(r[1]) if r else ""

        bas_m, bit_m = alan("Başlangıç"), alan("Bitiş")
        bas, _ = ortak.tarih_bul(bas_m, bugun)
        bit, _ = ortak.tarih_bul(bit_m, bugun)
        if not (baslik and bas):
            continue
        resim = re.search(r"<img[^>]+src=['\"]([^'\"]+)['\"]", blok)
        gorsel = resim[1] if resim and "afisler" in resim[1] else None   # genel şablon resmini alma
        yer = alan("Yer") or "Afyon Kocatepe Üniversitesi"
        if ortak.baska_il_mi(yer, "Afyonkarahisar"):
            continue                       # ör. "Yer: Antalya" — Afyon'da değil
        tur = alan("Tür")
        ad = basliklar(ortak.temizle(baslik[1]))
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": ortak.saat_bul(bas_m),
            "mekan": yer,
            "ilce": salon_ilce(yer, "Merkez"),
            "kategori": ortak.kategori_tahmin(ad + " " + tur),
            "gorsel": gorsel,
            "ozet": " · ".join(x for x in (tur, alan("Düzenleyen").title()) if x) or None,
        }


# ------------------------------------------------------------------
# 2) Afyonkarahisar Belediyesi — Next.js sayfasına gömülü veri
# ------------------------------------------------------------------
BEL = "https://www.afyon.bel.tr"
_BEL_KAYIT = re.compile(r'"slug":"([^"]+)","href":"(/guncel/etkinlikler/[^"]+)","label":"([^"]+)","nodeType":"content-item"')


def belediye(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"]).replace('\\"', '"')
    # Aynı etkinlik sayfada birkaç kez geçer; görsel bir kopyada, tarih/yer başka kopyada olabilir.
    # Her kopyayı bir sonraki kayda kadar olan bölümüyle birlikte topla, sonra birleştir.
    eslesmeler = list(_BEL_KAYIT.finditer(sayfa))
    kayit = {}
    for i, k in enumerate(eslesmeler):
        slug, href, ad = k.groups()
        # Bölüm en fazla 3000 karakter: daha uzağa bakınca başka etkinliğin tarihi karışıyordu
        son = min(eslesmeler[i + 1].start() if i + 1 < len(eslesmeler) else len(sayfa), k.end() + 3000)
        bolum = sayfa[k.end():son]
        bilgi = kayit.setdefault(slug, {"href": href, "ad": ad, "yer": None, "resim": None})
        yer = re.search(r'"yer":(\[.*?\])\}', bolum, re.S)
        resim = re.search(r'"mediumUrl":"(/uploads/[^"]+)"', bolum) or re.search(r'"url":"(/uploads/[^"]+)"', bolum)
        bilgi["yer"] = bilgi["yer"] or (yer[1] if yer else None)
        bilgi["resim"] = bilgi["resim"] or (resim[1] if resim else None)
    for slug, bilgi in kayit.items():
        if not bilgi["yer"]:
            continue
        href, ad, yer_json = bilgi["href"], bilgi["ad"], bilgi["yer"]
        zamanlar = sorted(re.findall(r'"(?:start|end)date":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})"', yer_json))
        if not zamanlar:
            continue
        bas, bit = dt.datetime.fromisoformat(zamanlar[0]), dt.datetime.fromisoformat(zamanlar[-1])
        mekan = re.search(r"!2s([^!]+)!", yer_json)
        tesis = re.search(r'"kayitli_tesis":"([^"]+)"', yer_json)
        adres = re.search(r'"manuel_adres":"([^"]+)"', yer_json)
        mekan_ad = (urllib.parse.unquote(mekan[1]).replace("+", " ") if mekan else
                    tesis[1].replace("-", " ").title() if tesis else adres[1] if adres else None)
        resim = bilgi["resim"]
        yield {
            "baslik": basliklar(html.unescape(ad)),
            "tarih": bas.date(),
            "bitis": bit.date() if bit.date() > bas.date() + dt.timedelta(days=0) and (bit - bas).days >= 1 else None,
            "saat": bas.strftime("%H:%M"),
            "mekan": mekan_ad,
            "ilce": salon_ilce(mekan_ad or "", "Merkez"),
            "gorsel": BEL + resim if resim else None,
            "url": BEL + href,
            "ucretsiz": True,
        }


# ------------------------------------------------------------------
# 3) Afyonkarahisar Sağlık Bilimleri Üniversitesi — WordPress RSS, tarih başlıkta "(6 Kasım 2026)"
# ------------------------------------------------------------------
def afsu(kaynak, bugun):
    rss = ortak.indir("https://afsu.edu.tr/category/etkinlikler/feed/")
    for item in re.findall(r"<item>(.*?)</item>", rss, re.S):
        baslik = ortak.temizle(re.search(r"<title>(.*?)</title>", item, re.S)[1].replace("<![CDATA[", "").replace("]]>", ""))
        tarih = re.search(r"\((\d{1,2} \w+ \d{4})\)", baslik)
        if not tarih or "son tarih" in ortak.kucuk(baslik):
            continue                       # tarihsiz yazılar haberdir; "Son Tarih" başvuru tarihidir
        bas, _ = ortak.tarih_bul(tarih[1], bugun)
        link = re.search(r"<link>([^<]+)</link>", item)
        yield {
            "baslik": baslik.replace(tarih[0], "").strip(" -–"),
            "tarih": bas,
            "mekan": "Afyonkarahisar Sağlık Bilimleri Üniversitesi",
            "ilce": "Merkez",
            "url": link[1].strip() if link else kaynak["url"],
        }


# ------------------------------------------------------------------
# 4) Emirdağ Belediyesi — etkinlik sayfası (HTML)
# ------------------------------------------------------------------
KISA_AY = {"oca": "ocak", "şub": "şubat", "mar": "mart", "nis": "nisan", "may": "mayıs", "haz": "haziran", "tem": "temmuz",
           "ağu": "ağustos", "eyl": "eylül", "eki": "ekim", "kas": "kasım", "ara": "aralık"}


def emirdag(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('class="e-tarih"')[1:]:
        p = re.findall(r"<p>\s*([^<]+?)\s*</p>", blok[:300])
        baslik = re.search(r'<a href="(etkinlik/[^"]+)"[^>]*>\s*<h5>(.*?)</h5>', blok, re.S)
        if len(p) < 3 or not baslik:
            continue
        ay = KISA_AY.get(ortak.kucuk(p[1])[:3])
        bas, _ = ortak.tarih_bul(f"{p[0]} {ay} {p[2]}", bugun) if ay else (None, None)
        resim = re.search(r'<img src="([^"]+)"', blok)
        yer = re.search(r"fa-map-marker-alt\"></i>\s*([^<]+)<", blok)
        yield {
            "baslik": ortak.temizle(baslik[2]),
            "tarih": bas,
            "mekan": ortak.temizle(yer[1]) if yer else None,
            "ilce": "Emirdağ",
            "gorsel": urllib.parse.urljoin("https://www.emirdag.bel.tr/", resim[1]) if resim else None,
            "url": urllib.parse.urljoin("https://www.emirdag.bel.tr/", baslik[1]),
        }


KAYNAKLAR = [
    {"ad": "Afyon Kocatepe Üniversitesi", "tur": "universite", "url": "https://aku.edu.tr/etkinlikler", "cek": aku},
    {"ad": "Afyonkarahisar Belediyesi", "tur": "belediye", "url": "https://www.afyon.bel.tr/guncel/etkinlikler", "cek": belediye},
    {"ad": "Afyonkarahisar Sağlık Bilimleri Üniversitesi", "tur": "universite", "url": "https://afsu.edu.tr/category/etkinlikler/", "cek": afsu},
    {"ad": "Emirdağ Belediyesi", "tur": "belediye", "ilce": "Emirdağ", "url": "https://www.emirdag.bel.tr/etkinlikler", "cek": emirdag},
    {"ad": "Afyonkarahisar İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://afyon.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Afyonkarahisar", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/afyonkarahisar", "cek": etkinlik_io,
     "sehir": "Afyonkarahisar", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Afyonkarahisar Valiliği", "tur": "valilik", "url": "https://www.afyonkarahisar.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "17 ilçe kaymakamlığı", "tur": "kaymakamlik", "url": "https://www.sandikli.gov.tr/duyurular",
     "not": "duyurular idari (ihale vb.); etkinlik yok"},
    {"ad": "Belediye Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "sadece sezon arşivi var; oyun takvimi yok"},
    {"ad": "Dinar Belediyesi", "tur": "belediye", "ilce": "Dinar", "url": "https://www.dinar.bel.tr/duyurular",
     "not": "etkinlikler serbest metin duyurularda; otomatik okunmuyor"},
    {"ad": "Bolvadin Belediyesi", "tur": "belediye", "ilce": "Bolvadin", "url": "https://www.bolvadin.bel.tr", "not": "site hata veriyor (500)"},
    {"ad": "Sandıklı Belediyesi, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://afyonkarahisar.gsb.gov.tr", "not": "bot koruması — okunamıyor"},
    {"ad": "İlçe festivalleri (Bolvadin Kaymak, Çay Vişne, Sultandağı Kiraz…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
