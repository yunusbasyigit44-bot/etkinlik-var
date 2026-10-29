"""Toplayıcının ortak parçaları: sayfa indirme, Türkçe tarih okuma, kategori tahmini.

Sadece Python'un kendi kütüphaneleri kullanılır (kurulum gerekmez),
böylece hem Yunus'un bilgisayarında hem GitHub'da aynen çalışır.
"""
import datetime as dt
import gzip
import hashlib
import html
import os
import re
import ssl
import time
import urllib.request

TARAYICI = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EtkinlikVar/1.0 (+etkinlik derleyici)"

def indir(url, zaman_asimi=25):
    """Sayfayı metin olarak indirir. Siteleri yormamak için her istekten sonra kısa bekler.

    Sertifika doğrulaması hiçbir zaman kapatılmaz: sertifikası bozuk site "SSL hatası" verir ve
    kaynak tablosunda hata olarak görünür (sahte sayfa sitemize yanlış etkinlik sokamasın).
    """
    istek = urllib.request.Request(url, headers={"User-Agent": TARAYICI, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
            ham = yanit.read()
            if yanit.headers.get("Content-Encoding") == "gzip":
                ham = gzip.decompress(ham)
            karakter = yanit.headers.get_content_charset() or "utf-8"
            time.sleep(1)
            return ham.decode(karakter, errors="replace")
    except urllib.error.URLError as hata:
        if isinstance(hata.reason, ssl.SSLError):
            raise RuntimeError("SSL hatası (sertifika doğrulanamadı): " + url) from None
        raise


GORSEL_KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "veri", "gorsel")


def gorsel_sakla(url, ad):
    """Görseli bir kez indirip site/veri/gorsel/ içine kaydeder; sitedeki yolunu döner."""
    os.makedirs(GORSEL_KLASOR, exist_ok=True)
    uzanti = ".webp" if ".webp" in url.split("?")[0] else ".jpg"
    dosya = re.sub(r"[^a-z0-9-]", "", ad.lower())[:80] + uzanti
    hedef = os.path.join(GORSEL_KLASOR, dosya)
    if not os.path.exists(hedef):
        istek = urllib.request.Request(url, headers={"User-Agent": TARAYICI})
        with urllib.request.urlopen(istek, timeout=30) as y:
            veri = y.read()
        if len(veri) > 1_500_000:          # çok büyük görseli kaydetme
            return None
        with open(hedef, "wb") as f:
            f.write(veri)
        time.sleep(0.5)
    return "veri/gorsel/" + dosya


def temizle(metin):
    """HTML etiketlerini ve fazla boşlukları atar."""
    metin = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", metin or "", flags=re.S | re.I)
    metin = re.sub(r"<[^>]+>", " ", metin)
    return re.sub(r"\s+", " ", html.unescape(metin)).strip()


AYLAR = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
    "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
    "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12,
}
_AY_DESEN = "|".join(sorted(AYLAR, key=len, reverse=True))


def kucuk(metin):
    """Türkçe'ye uygun küçük harf (I→ı, İ→i)."""
    return (metin or "").replace("I", "ı").replace("İ", "i").lower()


def tarih_bul(metin, bugun=None):
    """Metindeki ilk tarihi bulur. (başlangıç, bitiş) döner; bulamazsa (None, None).

    Tanıdığı biçimler: 12 Kasım 2026 · 12-14 Kasım · 12 Kasım (yılsız) · 12.11.2026 · 12/11/2026 · 2026-11-12
    """
    bugun = bugun or dt.date.today()
    m = kucuk(metin)

    def yil_tahmin(gun, ay):
        # Yıl yazılmamışsa: tarih 2 aydan fazla geçmişte kalıyorsa gelecek yıldır.
        aday = dt.date(bugun.year, ay, gun)
        return aday if aday >= bugun - dt.timedelta(days=60) else dt.date(bugun.year + 1, ay, gun)

    try:
        r = re.search(r"(\d{4})-(\d{2})-(\d{2})", m)
        if r:
            d = dt.date(int(r[1]), int(r[2]), int(r[3]))
            return d, d
        # Ay aşan aralık: "1 Ağustos - 30 Ekim", "28 Ekim 2026 - 3 Kasım 2026", "20 Aralık - 5 Ocak"
        r = re.search(r"\b(\d{1,2})\s+(" + _AY_DESEN + r")\s*(\d{4})?\s*[-–]\s*(\d{1,2})\s+(" + _AY_DESEN + r")\s*(\d{4})?", m)
        if r and AYLAR[r[2]] != AYLAR[r[5]]:
            ay1, ay2 = AYLAR[r[2]], AYLAR[r[5]]
            bit = dt.date(int(r[6]), ay2, int(r[4])) if r[6] else yil_tahmin(int(r[4]), ay2)
            yil1 = int(r[3]) if r[3] else bit.year - (1 if ay1 > ay2 else 0)   # Aralık-Ocak: başlangıç önceki yıl
            return dt.date(yil1, ay1, int(r[1])), bit
        r = re.search(r"\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s+(" + _AY_DESEN + r")\s*(\d{4})?", m)
        if r:
            ay = AYLAR[r[3]]
            if r[4]:
                bas, bit = dt.date(int(r[4]), ay, int(r[1])), dt.date(int(r[4]), ay, int(r[2]))
            else:
                bas, bit = yil_tahmin(int(r[1]), ay), yil_tahmin(int(r[2]), ay)
            return bas, bit
        r = re.search(r"\b(\d{1,2})\s+(" + _AY_DESEN + r")\s*(\d{4})?", m)
        if r:
            ay = AYLAR[r[2]]
            d = dt.date(int(r[3]), ay, int(r[1])) if r[3] else yil_tahmin(int(r[1]), ay)
            return d, d
        r = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", m)
        if r:
            d = dt.date(int(r[3]), int(r[2]), int(r[1]))
            return d, d
    except ValueError:
        pass
    return None, None


def saat_bul(metin):
    # Önce tarihleri çıkar ki "05.11.2026" saat sanılmasın.
    m = re.sub(r"\d{1,4}[./-]\d{1,2}[./-]\d{2,4}", " ", kucuk(metin))
    r = re.search(r"(?<!\d)([01]?\d|2[0-3])[:.]([0-5]\d)(?!\d)", m)
    return f"{int(r[1]):02d}:{r[2]}" if r else None


# Sıra önemli: ilk eşleşen tür seçilir (özel olanlar genel olanlardan önce).
# Site bu türleri üst sınıflarda gruplar (index.html → SINIFLAR); yeni tür eklenirse oraya da ekle.
KATEGORILER = [
    ("Çocuk", ["çocuk", "masal", "kukla", "minik", "karagöz"]),
    ("Opera & Bale", ["opera", "bale", "operet"]),
    ("Dans", ["dans", "halk oyunları", "halkoyunları", "zeybek", "folklor", "tango", "salsa", "horon"]),
    ("Geleneksel Müzik", ["türkü", "aşık", "aşıklar", "fasıl", "tasavvuf", "sema", "mevlevi", "ilahi", "halk müziği",
                          "türk müziği", "sanat müziği", "ulusal müziğimiz", "mehter"]),
    ("Konser", ["konser", "müzik", "dinleti", "koro", "orkestra", "şarkı", "resital", "caz", "senfoni", "rock"]),
    ("Komedi", ["komedi", "stand-up", "stand up", "doğaçlama", "skeç"]),
    ("Tiyatro", ["tiyatro", "oyun sahne", "sahneleniyor", "perde", "gösteri", "müzikal"]),
    ("Sinema", ["film", "sinema", "gösterim", "belgesel", "kısa film"]),
    ("Edebiyat", ["kitap", "şiir", "edebiyat", "imza günü", "imza", "yazar", "öykü", "roman"]),
    ("Sergi", ["sergi", "sergisi", "fotoğraf", "resim", "müze", "karikatür", "heykel"]),
    ("Bilim & Teknoloji", ["teknoloji", "yazılım", "kodlama", "devfest", "hackathon", "siber", "robot", "yapay zeka",
                           "yapay zekâ", "bilim şenliği", "uzay", "teknofest", "girişimcilik"]),
    ("Kariyer", ["kariyer", "staj", "istihdam", "işkur", "mülakat", "iş fuarı", "sınavları", "yds", "kpss", "soru çözme"]),
    ("Sağlık", ["sağlık", "saglig", "kanser", "yoga", "kan bağışı", "tarama", "diyabet", "beslenme"]),
    ("Spor", ["turnuva", "maraton", "koşu", "yarış", "spor", "futbol", "voleybol", "basketbol", "hentbol", "satranç",
              "bisiklet", "ligi", "maç", "yüzme", "güreş"]),
    ("Doğa & Gezi", ["gezi", "gezisi", "turu", "yürüyüş", "doğa", "kamp", "fidan", "ağaç dikimi", "ormanı", "kuş gözlem"]),
    ("Yemek", ["yemek", "gastronomi", "lezzet", "mutfak", "tadım", "kahvaltı"]),
    ("Akademik", ["kongre", "sempozyum", "sertifika", "çalıştay", "bilimsel toplantı", "hukuk"]),
    ("Söyleşi", ["söyleşi", "konferans", "panel", "seminer", "talks", "buluşma", "sohbet", "anlamak"]),
    ("Atölye", ["atölye", "kurs", "eğitim", "workshop", "kutu oyunları"]),
    ("Festival", ["festival", "karnaval", "şenlik", "bozum", "hıdrellez", "nevruz"]),
    ("Fuar & Kermes", ["fuar", "kermes", "pazar yeri", "bazaar", "kitap fuarı"]),
    ("Gençlik", ["gençlik", "öğrenci topluluğu", "topluluğu", "üniversite tanıtım"]),
    ("Anma / Tören", ["anma", "tören", "kutlama", "cumhuriyet", "19 mayıs", "23 nisan", "30 ağustos", "hatırasına"]),
]


def kategori_tahmin(metin):
    m = kucuk(metin)
    for ad, kelimeler in KATEGORILER:
        # Kelime başında eşleşme: "aydınlanma" içindeki "anma" sayılmasın
        if any(re.search(r"(?<![a-zçğıöşü])" + re.escape(k), m) for k in kelimeler):
            return ad
    return "Diğer"


def ucretsiz_mi(metin, kaynak_turu):
    """True / False / None (bilinmiyor). Kamu kurumlarının etkinlikleri çoğunlukla ücretsizdir."""
    m = kucuk(metin)
    if any(k in m for k in ["ücretsiz", "ucretsiz", "giriş serbest", "halka açık", "bedava"]):
        return True
    if any(k in m for k in ["bilet", "₺", " tl", "ücretli"]):
        return False
    return True if kaynak_turu in ("belediye", "valilik", "kaymakamlik", "universite") else None


GECMIS_HABER = re.compile(
    r"(düzenlendi|gerçekleştirildi|tamamlandı|yapıldı|sona erdi|kutlandı|anıldı|ziyaret etti|"
    r"tamamladı|ağırladı|renkli görüntüler|ödül(ler)?ini aldı|coşkusu)", re.I)


ILLER = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
         "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
         "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
         "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli",
         "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş",
         "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
         "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
         "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"]


def baska_il_mi(yer, il):
    """Yer sadece başka bir ilin adıysa (ör. 'Antalya') etkinlik bu ilde değildir."""
    y = kucuk(temizle(yer)).strip(" .,")
    return y != kucuk(il) and y in {kucuk(i) for i in ILLER}


def baslikta_baska_il(baslik, il, ilceler=()):
    """Başlık etkinliğin başka ilde olduğunu söylüyorsa True (ör. Çankırı'da 'COP31 Antalya Zirvesi', 'Antalya'da Kariyer Günü').

    Sadece yer bildiren kalıplara bakılır: "<il>'da/'de/'ta/'te" ya da "<il> Zirvesi/Fuarı/Kongresi/Festivali".
    "Sen İstanbul'dan Daha Güzelsin" gibi oyun adları ve "Van Gölü" gibi ortak yer adları elenmez.
    """
    b = kucuk(baslik)
    if kucuk(il) in b or any(kucuk(i) in b for i in ilceler if len(i) > 3):
        return False
    for i in ILLER:
        k = re.escape(kucuk(i))
        if kucuk(i) != kucuk(il) and re.search(
                r"(?<![a-zçğıöşü])" + k + r"(?:['’](?:da|de|ta|te)(?![a-zçğıöşü])|\s+(?:zirve|fuar|kongre|festival|maraton))", b):
            return True
    return False


KAPALI = re.compile(r"(kurulu? toplantısı|paydaş|senato|komisyon toplantısı|personel toplantısı|seçimi ilanı|ihale)")


def kamuya_kapali_mi(baslik):
    """İç toplantılar (kurul, senato, paydaş toplantısı) halka açık etkinlik değildir."""
    return bool(KAPALI.search(kucuk(baslik)))


def gecmis_haber_mi(baslik):
    """'... düzenlendi' gibi başlıklar olmuş bir etkinliğin haberidir, gelecek etkinlik değil."""
    return bool(GECMIS_HABER.search(kucuk(baslik)))


def kimlik(baslik, tarih, saat=None):
    """Aynı etkinliğin iki kaynakta tekrarını yakalamak ve 'Gidiyorum' sayacı için sabit kimlik."""
    anahtar = re.sub(r"[^a-z0-9çğıöşü]", "", kucuk(baslik))[:60] + str(tarih) + (saat or "")
    return hashlib.sha1(anahtar.encode()).hexdigest()[:12]
