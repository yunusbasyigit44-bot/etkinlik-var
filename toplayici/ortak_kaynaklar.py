"""Her ilde aynı şekilde çalışan kaynaklar: Devlet Tiyatroları, İl Kültür ve Turizm, etkinlik.io.

Bir ilin dosyasında kaynak sözlüğüne şu ek bilgiler yazılır:
  "sehir": "Adana"                    -> ilin adı (kaynakta nasıl geçiyorsa)
  "ilce_bul": fonksiyon(mekan) -> ilçe  -> mekandan ilçe tahmini (ilin dosyasında tanımlı)
  "varsayilan_ilce": "Seyhan"          -> ilçe bulunamazsa
"""
import datetime as dt
import json
import os
import re
import urllib.request

import ortak


KISALTMA = {"DT", "AKM", "CSO", "TRT", "OSB", "MEB", "KTB", "TBMM", "AVM", "SKS", "AFAD", "UNESCO", "TÜBİTAK", "İTÜ", "ODTÜ",
            "KTÜ", "ATÜ", "ADÜ", "OMÜ", "ESTÜ", "BTÜ", "ÇÜ", "DEÜ", "EÜ", "SDÜ", "AKÜ", "AFSÜ", "ADYÜ", "İBB", "ABB", "AB", "ABD",
            "NATO", "TEKNOFEST", "YKS", "LGS", "KPSS", "STK", "TEDx", "AI", "MYO", "GSF", "İİBF", "İİSBF"}


def basliklar(ad):
    """'OCAK'TA BAHAR' -> 'Ocak'ta Bahar' (tamamı büyük harf başlıkları okunur yapar)."""
    if ad != ad.upper():
        return ad
    kelimeler = []
    for buyuk in ad.split():
        # Kısaltmalar ve Roma rakamları büyük kalır: DT, AKM, CSO, TRT, II, IX, COP31
        if buyuk.strip("().,:;-'\"") in KISALTMA or re.fullmatch(r"[IVX]+|[A-ZÇĞİÖŞÜ]*\d+[A-ZÇĞİÖŞÜ\d]*", buyuk.strip("().,:;-")):
            kelimeler.append(buyuk)
            continue
        # İngilizce/Latince kelimeler (MEETING, NECROPOLEIS, WORKSHOP) Türkçe I→ı kuralıyla bozulmasın
        if buyuk.isascii() and re.search(r"(W|Q|X|ING\b|TION|EI|EE|OO|TH|IC\b)", buyuk):
            kelimeler.append(buyuk.capitalize())
            continue
        k = ortak.kucuk(buyuk)
        if kelimeler and k in ("ve", "ile", "için", "da", "de", "ya", "veya", "mi", "mı"):
            kelimeler.append(k)            # bağlaçlar küçük kalır: "Sanat ve Bilim"
            continue
        on = len(k) - len(k.lstrip("(\"'“‘«-"))      # baştaki parantez/tırnak atlanır: "(Öğrenci"
        if on >= len(k):
            kelimeler.append(k)
            continue
        bas = k[on].replace("i", "İ").replace("ı", "I").upper()
        kelimeler.append(k[:on] + bas + k[on + 1:])
    return " ".join(kelimeler)


def ilce_bulucu(ilceler, salonlar=None):
    """Mekan adından ilçe bulan fonksiyon üretir. salonlar: {"salon adından parça": "İlçe"}."""
    def bul(mekan, varsayilan=None):
        m = ortak.kucuk(mekan)
        for anahtar, ilce in (salonlar or {}).items():
            if anahtar in m:
                return ilce
        for ilce in ilceler:
            # kelime başında eşleşmeli: "Konya Okulu" içindeki "kulu" Kulu ilçesi değildir
            if re.search(r"(?<![a-zçğıöşü])" + re.escape(ortak.kucuk(ilce)), m):
                return ilce
        return varsayilan
    return bul


def _ilce(kaynak, mekan):
    bul = kaynak.get("ilce_bul")
    return bul(mekan or "", kaynak.get("varsayilan_ilce")) if bul else kaynak.get("varsayilan_ilce")


# ------------------------------------------------------------------
# Devlet Tiyatroları — sitenin kendi kullandığı program verisi (JSON)
# ------------------------------------------------------------------
_PROGRAM = {}


def _program():
    """Tüm Türkiye programı bir kez indirilir, iller arasında paylaşılır."""
    if "veri" not in _PROGRAM:
        _PROGRAM["veri"] = json.loads(ortak.indir("https://devtiyatro.gov.tr/api/v1/program/schedule"))
    return _PROGRAM["veri"]


def _oyun_bilgisi(slug, onbellek={}):
    """Oyun detayı: çocuk oyunu mu + afiş. Her oyun bir kez sorulur.

    Afiş linkleri 1 saat sonra geçersiz olduğu için afiş indirilip sitede saklanır.
    """
    if slug not in onbellek:
        bilgi = {"cocuk": False, "gorsel": None}
        try:
            d = json.loads(ortak.indir("https://devtiyatro.gov.tr/api/v1/plays/" + slug)).get("data") or {}
            bilgi["cocuk"] = bool(d.get("is_children_play"))
            afis = d.get("poster_thumb_url") or d.get("poster_url")
            if afis:
                bilgi["gorsel"] = ortak.gorsel_sakla(afis, "dt-" + slug)
        except Exception as hata:
            print("   oyun bilgisi alınamadı:", slug, hata)
        onbellek[slug] = bilgi
    return onbellek[slug]


def devlet_tiyatrosu(kaynak, bugun):
    for sehir in _program().get("data", []):
        if ortak.kucuk(sehir.get("city")) != ortak.kucuk(kaynak["sehir"]):
            continue
        for sahne in sehir.get("stages", []):
            mekan = basliklar(sahne.get("name") or "")
            for p in sahne.get("performances", []):
                oyun = (p.get("play") or {})
                konuk = (p.get("guest_group") or {})
                bilgi = _oyun_bilgisi(oyun["slug"]) if oyun.get("slug") else {"cocuk": False, "gorsel": None}
                yield {
                    "baslik": basliklar(oyun.get("name") or konuk.get("name") or "Tiyatro oyunu"),
                    "tarih": dt.date.fromisoformat(p["date"]),
                    "saat": (p.get("time") or "")[:5] or None,
                    "mekan": mekan,
                    "ilce": _ilce(kaynak, mekan),
                    "kategori": "Çocuk" if bilgi["cocuk"] else "Tiyatro",
                    "gorsel": bilgi["gorsel"],
                    "ucretsiz": False,
                    "url": "https://devtiyatro.gov.tr/oyunlar/" + oyun["slug"] if oyun.get("slug") else kaynak["url"],
                    "ozet": "Devlet Tiyatroları" + (" konuk topluluk: " + konuk["name"] if konuk.get("name") else ""),
                }


def devlet_tiyatrosu_sehirleri():
    """Devlet Tiyatrolarının o an programı olan şehirler (yeni il eklerken bakmak için)."""
    return sorted({s.get("city") for s in _program().get("data", [])})


# ------------------------------------------------------------------
# Devlet Opera ve Balesi — operabale.gov.tr'nin kendi kullandığı anahtarsız program verisi (JSON)
# Müdürlükler: 1 Ankara, 2 İstanbul, 3 İzmir, 4 Mersin, 5 Antalya, 6 Samsun. Kaynakta: "mudurluk": <no>.
# ------------------------------------------------------------------
OPERA_SAYFA = {1: "ankara-opera-ve-balesi-1", 2: "istanbul-opera-ve-balesi-2", 3: "izmir-opera-ve-balesi-3",
               4: "mersin-opera-ve-balesi-4", 5: "antalya-opera-ve-balesi-5", 6: "samsun-opera-ve-balesi-6"}


def devlet_opera(kaynak, bugun):
    no = kaynak["mudurluk"]
    veri = json.loads(ortak.indir(f"https://apimain.operabale.gov.tr/v1/web/temsil/mudurluk/listele/{no}"))
    for p in veri:
        try:
            gun = dt.datetime.fromisoformat(p["oyunTarihi"])
        except (KeyError, ValueError, TypeError):
            continue
        ad = basliklar(ortak.temizle(p.get("eserAdi") or ""))
        if not ad:
            continue
        sahne = basliklar(p.get("sahneAdi") or "")
        afis = (p.get("afisler") or [None])[0]
        gorsel = None
        if afis:
            try:
                gorsel = ortak.gorsel_sakla(afis, f"dob-{no}-{p.get('eserKodu')}")   # afiş linkleri süreli; indirip sakla
            except Exception as hata:
                print("   afiş alınamadı:", ad, hata)
        cocuk = re.search(r"pinokyo|okulumuz|çocuk|masal|keloğlan|pamuk prenses|uyuyan güzel|kibrit", ortak.kucuk(ad))
        yield {
            "baslik": ad,
            "tarih": gun.date(),
            "saat": (p.get("oyunSaatleri") or [gun.strftime("%H:%M")])[0],
            "mekan": sahne or "Devlet Opera ve Balesi",
            "ilce": _ilce(kaynak, sahne),
            "kategori": "Çocuk" if cocuk else ("Konser" if re.search(r"konser|resital|senfoni", ortak.kucuk(ad)) else "Tiyatro"),
            "ucretsiz": False,
            "gorsel": gorsel,
            "url": p.get("seoFullUrl") or "https://www.operabale.gov.tr/directorates/" + OPERA_SAYFA.get(no, ""),
            "ozet": "Devlet Opera ve Balesi",
        }


# ------------------------------------------------------------------
# iCal takvim akışı — WordPress "The Events Calendar" eklentisi (çoğu üniversite: <site>/etkinlik/?ical=1
# ya da /events/?ical=1). Kaynakta: "url": akış adresi, "mekan_varsayilan": "...", "ilce_bul", "varsayilan_ilce".
# ------------------------------------------------------------------
def _ical_olaylar(metin):
    metin = re.sub(r"\r?\n[ \t]", "", metin)          # katlanmış satırları birleştir
    for blok in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", metin, re.S):
        alan = {}
        for satir in blok.strip().splitlines():
            ad, _, deger = satir.partition(":")
            alan.setdefault(ad.split(";")[0], re.sub(r"\\n", " ", re.sub(r"\\([,;])", r"\1", deger)))
        yield alan


def _ical_zaman(deger):
    r = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2}))?", deger or "")
    if not r:
        return None, None
    return dt.date(int(r[1]), int(r[2]), int(r[3])), (f"{r[4]}:{r[5]}" if r[4] else None)


def ical(kaynak, bugun):
    for o in _ical_olaylar(ortak.indir(kaynak["url"])):
        bas, saat = _ical_zaman(o.get("DTSTART"))
        bit, _ = _ical_zaman(o.get("DTEND"))
        if not (bas and o.get("SUMMARY")):
            continue
        ad = basliklar(ortak.temizle(o["SUMMARY"].replace("''", '"')))
        yer = ortak.temizle(o.get("LOCATION") or "") or kaynak.get("mekan_varsayilan") or kaynak["ad"]
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit and bit > bas else None,
            "saat": saat if saat != "00:00" else None,
            "mekan": yer,
            "ilce": _ilce(kaynak, yer),
            "kategori": ortak.kategori_tahmin(ad + " " + (o.get("CATEGORIES") or "")),
            "url": o.get("URL") or kaynak["url"].split("?")[0],
            "ozet": o.get("CATEGORIES") or None,
        }


# ------------------------------------------------------------------
# İl Kültür ve Turizm Müdürlüğü — duyurular (serbest metin, tarih başlıkta)
# ------------------------------------------------------------------
def ktb(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    kok = re.match(r"https?://[^/]+", kaynak["url"])[0]
    for link, baslik in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{12,200})</a>', sayfa):
        b = ortak.temizle(baslik)
        if ortak.tarih_bul(b, bugun)[0] and re.search(r"etkinli|konser|sergi|festival|gösteri|söyleşi|program", ortak.kucuk(b)):
            yield {"baslik": b, "url": link if link.startswith("http") else kok + link}


# ------------------------------------------------------------------
# etkinlik.io — resmî API (yayıncı ağı başvurusu ile alınan anahtar gerekir)
# Anahtar ETKINLIK_IO_TOKEN ortam değişkeninde durur; koda/siteye yazılmaz.
# ------------------------------------------------------------------
EIO = "https://etkinlik.io/api/v2"
_EIO_SEHIRLER = {}


def _eio_getir(yol, anahtar):
    istek = urllib.request.Request(EIO + yol, headers={"User-Agent": ortak.TARAYICI, "X-Etkinlik-Token": anahtar,
                                                        "Accept": "application/json"})
    with urllib.request.urlopen(istek, timeout=30) as y:
        return json.loads(y.read().decode("utf-8"))


def etkinlik_io(kaynak, bugun):
    anahtar = os.environ.get("ETKINLIK_IO_TOKEN")
    if not anahtar:
        raise RuntimeError("API anahtarı yok (etkinlik.io yayıncı başvurusu bekleniyor)")
    if not _EIO_SEHIRLER:
        sehirler = _eio_getir("/cities", anahtar)
        for s in (sehirler.get("items", []) if isinstance(sehirler, dict) else sehirler):
            _EIO_SEHIRLER[ortak.kucuk(s.get("name"))] = s["id"]
    il_id = _EIO_SEHIRLER[ortak.kucuk(kaynak["sehir"])]
    atla, TR = 0, dt.timezone(dt.timedelta(hours=3))
    while atla < 500:
        sayfa = _eio_getir(f"/events?city_ids={il_id}&start_gte={bugun.isoformat()}&take=100&skip={atla}", anahtar)
        liste = sayfa.get("items", []) if isinstance(sayfa, dict) else sayfa
        for e in liste:
            bas = dt.datetime.fromisoformat(e["start_r001"].replace("Z", "+00:00")).astimezone(TR)
            bit = e.get("end_r001") and dt.datetime.fromisoformat(e["end_r001"].replace("Z", "+00:00")).astimezone(TR)
            yer = e.get("venue_data") or {}
            mekan = yer.get("name") or yer.get("address")
            ilce = (yer.get("district") or {}).get("name") if isinstance(yer.get("district"), dict) else yer.get("district_name")
            tur = ((e.get("category") or {}).get("name") or "") + " " + ((e.get("format") or {}).get("name") or "")
            yield {
                "baslik": e["name"],
                "tarih": bas.date(),
                "bitis": bit.date() if bit and bit.date() != bas.date() else None,
                "saat": bas.strftime("%H:%M"),
                "mekan": mekan,
                "ilce": _ilce(kaynak, (ilce or "") + " " + (mekan or "")),
                "kategori": ortak.kategori_tahmin(e["name"] + " " + tur),
                "ucretsiz": bool(e.get("is_free")),
                "url": e.get("url") or e.get("ticket_url"),
                "gorsel": e.get("poster_url"),
            }
        if len(liste) < 100:
            break
        atla += 100
