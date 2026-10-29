"""İstanbul kaynakları (plaka 34). Kaynak haritası: 2026-10-29.

Okunan kaynaklar: İBB Şehir Tiyatroları (oyun sayfalarındaki gösterim listeleri), Kadıköy Belediyesi Kültür Sanat
(kultursanat.kadikoy.bel.tr), İstanbul Teknik Üniversitesi (kendi ana sayfasının kullandığı herkese açık etkinlik JSON'u).
Devlet Tiyatroları İstanbul sahneleri ortak kaynakla gelir.
Okunamayanlar: kultur.istanbul (takvim JS ile yükleniyor), Beşiktaş/Üsküdar/Beyoğlu belediyeleri (tarihli takvim yok).
"""
import datetime as dt
import html
import json
import re
import urllib.parse

import ortak
from ortak_kaynaklar import basliklar, devlet_opera, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir",
           "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy",
           "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane",
           "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli",
           "Sultangazi", "Şile", "Şişli", "Tuzla", "Ümraniye", "Üsküdar", "Zeytinburnu"]
SALON_ILCE = {"mecidiyeköy": "Şişli", "gazhane": "Kadıköy", "harbiye": "Şişli", "haldun taner": "Kadıköy", "caddebostan": "Kadıköy",
              "bostancı": "Kadıköy", "moda": "Kadıköy", "itü": "Sarıyer", "ayazağa": "Sarıyer", "maslak": "Sarıyer",
              "taksim": "Beyoğlu", "istiklal": "Beyoğlu", "galata": "Beyoğlu", "akm": "Beyoğlu",
              "atatürk kültür merkezi": "Beyoğlu", "sultanahmet": "Fatih", "topkapı": "Fatih", "kabataş": "Beyoğlu"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

_AYLAR = r"Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık"


# ------------------------------------------------------------------
# 1) İBB Şehir Tiyatroları — ana sayfadaki oyun kartları + her oyunun "Gösterimler" listesi (HTML)
# ------------------------------------------------------------------
IBB_ST = "https://sehirtiyatrolari.ibb.istanbul"
_GOSTERIM = re.compile(r"(\d{1,2} (?:" + _AYLAR + r")) (?:Pazartesi|Salı|Çarşamba|Perşembe|Cuma|Cumartesi|Pazar), (\d{2}:\d{2})")


def sehir_tiyatrolari(kaynak, bugun):
    ana = ortak.indir(IBB_ST)
    oyunlar = {}
    for parca in ana.split('href="/oyun/')[1:]:
        slug = parca.split('"', 1)[0]
        bilgi = oyunlar.setdefault(slug, {"ad": None, "resim": None, "tur": None})
        ad = re.search(r'title="([^"]+)"', parca[:300])
        resim = re.search(r'<img[^>]+src="(https://[^"]+)"', parca[:700])
        tur = re.search(r'class="text-xs leading-3[^>]*>\s*([^<]+?)\s*</a>', parca[:2500])
        bilgi["ad"] = bilgi["ad"] or (ortak.temizle(html.unescape(ad[1])) if ad else None)
        bilgi["resim"] = bilgi["resim"] or (resim[1] if resim else None)
        bilgi["tur"] = bilgi["tur"] or (ortak.temizle(tur[1]) if tur else None)
    for slug, bilgi in oyunlar.items():
        if not bilgi["ad"] or "atölye" in ortak.kucuk(bilgi["ad"]):
            continue                       # oyunculuk/yazım atölyeleri kayıtlı katılımcılara özel
        sayfa = ortak.indir(f"{IBB_ST}/oyun/{slug}")
        duz = re.sub(r"<script.*?</script>|<style.*?</style>", "", sayfa, flags=re.S)
        duz = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "\n", duz)))
        bas = duz.find("Gösterim Tarihleri ve Mekanları")
        if bas < 0:
            continue
        duz = duz[bas:]
        bulunanlar = list(_GOSTERIM.finditer(duz))
        gorulen = set()
        for i, g in enumerate(bulunanlar):
            son = bulunanlar[i + 1].start() if i + 1 < len(bulunanlar) else len(duz)
            mekan = duz[g.end():son]
            mekan = re.split(r"\b(?:Tükendi|Hemen|Satışa|Satış|Bilet)\b", mekan)[0]
            m = re.match(r"\s*(.*?(?:Sahnesi|Sahne|Merkezi|Tiyatrosu|Salonu|Müzesi))", mekan)
            mekan = ortak.temizle((m[1] if m else mekan[:60]).strip())
            tarih, _ = ortak.tarih_bul(g[1], bugun)
            if not tarih or (tarih, g[2], mekan) in gorulen:
                continue
            gorulen.add((tarih, g[2], mekan))
            tur = bilgi["tur"] or ""
            yield {
                "baslik": bilgi["ad"],
                "tarih": tarih,
                "saat": g[2],
                "mekan": mekan or "İBB Şehir Tiyatroları",
                "ilce": salon_ilce(mekan, None),
                "kategori": "Çocuk" if "çocuk" in ortak.kucuk(tur) else "Tiyatro",
                "gorsel": bilgi["resim"],
                "url": f"{IBB_ST}/oyun/{slug}",
                "ucretsiz": False,
                "ozet": "İBB Şehir Tiyatroları" + (" · " + tur if tur else ""),
            }


# ------------------------------------------------------------------
# 2) Kadıköy Belediyesi Kültür Sanat — etkinlik listesi (HTML)
# ------------------------------------------------------------------
KKS = "https://kultursanat.kadikoy.bel.tr"


def _aralik(metin, bugun):
    """'01 Ağustos - 30 Ekim' / '29 Ekim - 04 Kasım' / '30 Ekim' -> (başlangıç, bitiş)."""
    ciftler = re.findall(r"(\d{1,2})\s+(" + _AYLAR + ")", metin)
    if not ciftler:
        return None, None
    ay = {a: i + 1 for i, a in enumerate(_AYLAR.split("|"))}
    bit, _ = ortak.tarih_bul(" ".join(ciftler[-1]), bugun)
    bas = dt.date(bit.year, ay[ciftler[0][1]], int(ciftler[0][0]))
    if bas > bit:
        bas = bas.replace(year=bit.year - 1)
    return bas, bit


def kadikoy(kaynak, bugun):
    sayfa = ortak.indir(kaynak["url"])
    for blok in sayfa.split('<article class="eleman">')[1:]:
        link = re.search(r'href="(/tr/kadikoyde-kultur-sanat/[^"]+)"', blok)
        baslik = re.search(r"<h2>.*?</span>\s*(.*?)\s*</h2>", blok, re.S)
        zaman = re.search(r"<time>(.*?)</time>", blok, re.S)
        if not (link and baslik and zaman):
            continue
        z = ortak.temizle(re.sub(r"<[^>]+>", " ", zaman[1]))
        bas, bit = _aralik(z, bugun)
        if not bas:
            continue
        yer = re.search(r'<span class="yer">.*?</span>\s*(.*?)\s*</span>', blok, re.S)
        resim = re.search(r'<p class="gorsel">\s*<img src="([^"]+)"', blok)
        ozet = re.search(r'<span class="acikla">\s*(.*?)\s*</span>', blok, re.S)
        ad = basliklar(ortak.temizle(html.unescape(baslik[1])))
        mekan = ortak.temizle(re.sub(r"<[^>]+>", "", html.unescape(yer[1]))) if yer else None
        yield {
            "baslik": ad,
            "tarih": bas,
            "bitis": bit if bit > bas else None,
            "saat": ortak.saat_bul(z),
            "mekan": mekan,
            "ilce": "Kadıköy",
            "kategori": ortak.kategori_tahmin(ad + " " + (ortak.temizle(ozet[1]) if ozet else "")),
            "gorsel": urllib.parse.urljoin(KKS, urllib.parse.quote(resim[1], safe=":/%")) if resim else None,
            "url": KKS + link[1],
            "ozet": ortak.temizle(html.unescape(ozet[1]))[:240] if ozet else None,
        }


# ------------------------------------------------------------------
# 3) İstanbul Teknik Üniversitesi — ana sayfanın kullandığı herkese açık etkinlik JSON'u
# ------------------------------------------------------------------
def itu(kaynak, bugun):
    veri = json.loads(ortak.indir("https://etkinlik.itu.edu.tr/public/embed/etkinlikler.aspx"))
    for e in veri.get("EtkinlikList1", []) + veri.get("EtkinlikList2", []):
        try:
            bas = dt.datetime.fromisoformat(e["EtkinlikBaslangicTarihi"])
            bit = dt.datetime.fromisoformat(e["EtkinlikBitisTarihi"]) if e.get("EtkinlikBitisTarihi") else None
        except (KeyError, ValueError):
            continue
        ozet = ortak.temizle(e.get("EtkinlikkOzet") or "")
        yield {
            "baslik": ortak.temizle(e["EtkinlikAdı"]),
            "tarih": bas.date(),
            "bitis": bit.date() if bit and bit.date() > bas.date() else None,
            "saat": bas.strftime("%H:%M") if bas.hour else None,
            "mekan": "İstanbul Teknik Üniversitesi",
            "ilce": "Sarıyer",
            "kategori": ortak.kategori_tahmin(e["EtkinlikAdı"] + " " + (e.get("EtkinlikKategoriAdi") or "")),
            "gorsel": e.get("EtkinlikGorseli") or None,
            "url": f"https://etkinlik.itu.edu.tr/EtkinlikDetay.aspx?etkinlik={e['EtkinlikId']}",
            "ozet": ozet[:240] or None,
        }


KAYNAKLAR = [
    {"ad": "Devlet Opera ve Balesi", "tur": "kultur", "url": "https://www.operabale.gov.tr", "cek": devlet_opera,
     "mudurluk": 2, "ilce_bul": salon_ilce, "varsayilan_ilce": "Beyoğlu"},
    {"ad": "İBB Şehir Tiyatroları", "tur": "belediye", "url": IBB_ST, "cek": sehir_tiyatrolari},
    {"ad": "Kadıköy Belediyesi Kültür Sanat", "tur": "belediye", "ilce": "Kadıköy",
     "url": KKS + "/tr/kadikoyde-kultur-sanat", "cek": kadikoy},
    {"ad": "İstanbul Teknik Üniversitesi", "tur": "universite", "ilce": "Sarıyer", "url": "https://etkinlik.itu.edu.tr", "cek": itu},
    {"ad": "İstanbul İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://istanbul.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "İstanbul", "ilce_bul": salon_ilce, "varsayilan_ilce": "Beyoğlu"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/istanbul", "cek": etkinlik_io,
     "sehir": "İstanbul", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kültür İstanbul (İBB iştiraki)", "tur": "belediye", "url": "https://kultur.istanbul/etkinlikler",
     "not": "etkinlik takvimi JavaScript ile yükleniyor; okunamıyor"},
    {"ad": "Boğaziçi, İstanbul, Marmara, Yıldız Teknik ve diğer üniversiteler", "tur": "universite", "url": None,
     "not": "okunabilir etkinlik takvimi bulunamadı (sonraki tur)"},
    {"ad": "Beşiktaş Belediyesi", "tur": "belediye", "ilce": "Beşiktaş", "url": "https://www.besiktas.bel.tr", "not": "site zaman aşımı veriyor; etkinlik takvimi okunamadı"},
    {"ad": "Beyoğlu Belediyesi", "tur": "belediye", "ilce": "Beyoğlu", "url": "https://beyoglu.bel.tr/kultur-sanat/",
     "not": "etkinlik sayfalarında tarih yok; okunmuyor"},
    {"ad": "Üsküdar, Maltepe, Sarıyer ve diğer ilçe belediyeleri", "tur": "belediye", "url": None,
     "not": "tarihli etkinlik takvimi okunamadı (sonraki tur)"},
    {"ad": "İstanbul Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://istanbul.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "İstanbul Film, Caz, Müzik, Tiyatro, Bienal festivalleri (İKSV)", "tur": "diger", "url": None,
     "not": "yıllık; bilet sitelerinde — resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler, bağımsız sahneler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
