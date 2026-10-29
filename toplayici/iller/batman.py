"""Batman kaynakları (plaka 72). Kaynak haritası: 2026-10-29.

Batman: Devlet Tiyatroları sahnesi var (ortak kaynak). Üniversite sitesi okunamadı, belediye etkinlik sayfası boş.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Beşiri", "Gercüş", "Hasankeyf", "Kozluk", "Sason"]
SALON_ILCE = {"hasankeyf": "Hasankeyf"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Batman İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://batman.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Batman", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/batman", "cek": etkinlik_io,
     "sehir": "Batman", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Batman Üniversitesi", "tur": "universite", "url": "https://batman.edu.tr", "not": "site bağlantıyı kapatıyor — okunamıyor"},
    {"ad": "Batman Belediyesi", "tur": "belediye", "url": "https://www.batman.bel.tr/etkinlikler", "not": "etkinlik sayfası var ama şu an kayıt yok"},
    {"ad": "Batman Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller", "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
