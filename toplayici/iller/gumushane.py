"""Gümüşhane kaynakları (plaka 29). Kaynak haritası: 2026-10-29.

Gümüşhane'de otomatik okunabilen güncel bir etkinlik takvimi bulunamadı (belediyenin etkinlik sayfasında son kayıt
Ağustos 2026; KTB'de 2026 şenlik-festival takvimi sadece Excel dosyası olarak yayımlanmış). Ortak kaynaklar listede;
bunlara etkinlik düşerse kendiliğinden gelir. Gezilecek yerler dosyası hazır.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Kelkit", "Köse", "Kürtün", "Şiran", "Torul"]
SALON_ILCE = {"gümüşhane üniversitesi": "Merkez", "kültür merkezi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Gümüşhane İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://gumushane.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Gümüşhane", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/gumushane", "cek": etkinlik_io,
     "sehir": "Gümüşhane", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Gümüşhane Belediyesi", "tur": "belediye", "url": "https://gumushane.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama güncel değil (son kayıt Ağustos 2026)"},
    {"ad": "Gümüşhane Üniversitesi", "tur": "universite", "url": "https://www.gumushane.edu.tr", "not": "etkinlik takvimi sayfası bulunamadı; sadece haber ve duyuru"},
    {"ad": "2026 Gümüşhane Şenlik-Festival Takvimi (İl Kültür ve Turizm)", "tur": "kultur",
     "url": "https://gumushane.ktb.gov.tr/TR-449432/2026-yili-gumushane-ili-senlik-festival-takvimi.html",
     "not": "takvim sadece Excel dosyası olarak yayımlanmış; otomatik okunmuyor"},
    {"ad": "Gümüşhane Valiliği ve 5 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.gumushane.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Kelkit, Şiran, Torul belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok; çoğu sadece haber"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://gumushane.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://gumushane.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık etkinlikler (Kelkit Aydıncık Yayla, Karaca Mağarası, Zigana şenlikleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
