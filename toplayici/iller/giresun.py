"""Giresun kaynakları (plaka 28). Kaynak haritası: 2026-10-29.

Giresun'da otomatik okunabilen bir etkinlik takvimi bulunamadı (belediye sadece haber/duyuru yayımlıyor,
Giresun Üniversitesi'nin etkinlik sayfası yok). Ortak kaynaklar (KTB, Devlet Tiyatroları, etkinlik.io) listede;
bunlara etkinlik düşerse kendiliğinden gelir. Gezilecek yerler dosyası hazır.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Alucra", "Bulancak", "Çamoluk", "Çanakçı", "Dereli", "Doğankent", "Espiye", "Eynesil", "Görele",
           "Güce", "Keşap", "Piraziz", "Şebinkarahisar", "Tirebolu", "Yağlıdere"]
SALON_ILCE = {"giresun üniversitesi": "Merkez", "kültür merkezi": "Merkez", "aksu": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Giresun İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://giresun.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Giresun", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/giresun", "cek": etkinlik_io,
     "sehir": "Giresun", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Giresun Belediyesi", "tur": "belediye", "url": "https://giresun.bel.tr",
     "not": "sadece haber ve vefat ilanları; etkinlik takvimi yok (etkinlik RSS kategorileri boş)"},
    {"ad": "Giresun Üniversitesi", "tur": "universite", "url": "https://www.giresun.edu.tr", "not": "etkinlik takvimi sayfası bulunamadı; sadece duyurular"},
    {"ad": "Giresun Valiliği ve 16 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.giresun.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Bulancak, Espiye, Tirebolu, Görele belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok; çoğu sadece haber"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://giresun.gsb.gov.tr", "not": "etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://giresun.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Yıllık etkinlikler (Uluslararası Giresun Aksu Festivali, Fındık Hasat Şenlikleri, Kümbet Yayla Şenliği…)", "tur": "diger",
     "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
