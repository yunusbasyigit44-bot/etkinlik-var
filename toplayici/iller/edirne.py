"""Edirne kaynakları (plaka 22). Kaynak haritası: 2026-10-29.

Trakya Üniversitesi'nin etkinlik sayfası listeyi JavaScript ile yüklüyor, Edirne Belediyesi'nin
"etkinlikler" sayfası ise haber niteliğinde (olmuş etkinlikler); bu yüzden şimdilik sadece ortak kaynaklar var.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Enez", "Havsa", "İpsala", "Keşan", "Lalapaşa", "Meriç", "Süloğlu", "Uzunköprü"]
SALON_ILCE = {"trakya üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Edirne İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://edirne.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Edirne", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/edirne", "cek": etkinlik_io,
     "sehir": "Edirne", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Trakya Üniversitesi", "tur": "universite", "url": "https://www.trakya.edu.tr/tum-etkinlikler",
     "not": "etkinlik listesi JavaScript ile yükleniyor; düz sayfada veri yok"},
    {"ad": "Edirne Belediyesi", "tur": "belediye", "url": "https://www.edirne.bel.tr/gundem/etkinlikler",
     "not": "'etkinlikler' sayfası olmuş etkinliklerin haberlerini gösteriyor; yaklaşan takvim yok"},
    {"ad": "Edirne Valiliği", "tur": "valilik", "url": "https://www.edirne.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "8 ilçe kaymakamlığı ve belediyeleri (Keşan, Uzunköprü…)", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Tarihi Kırkpınar Yağlı Güreşleri, Kakava Şenlikleri, Edirne Sanat Festivali", "tur": "diger", "url": None,
     "not": "yıllık; 2026-27 tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
