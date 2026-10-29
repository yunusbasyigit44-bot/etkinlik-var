"""Ardahan kaynakları (plaka 75). Kaynak haritası: 2026-10-29.

Okunabilir bir etkinlik takvimi bulunamadı: Ardahan Üniversitesi sitesinde yalnızca idari duyurular var,
belediye sitesinde etkinlik sayfası yok. Ortak kaynaklar listede duruyor; etkinlik çıkarsa kendiliğinden gelir.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Çıldır", "Damal", "Göle", "Hanak", "Posof"]
SALON_ILCE = {"ardahan üniversitesi": "Merkez", "nuri vatan": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Ardahan İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://ardahan.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Ardahan", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/ardahan", "cek": etkinlik_io,
     "sehir": "Ardahan", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Ardahan Üniversitesi", "tur": "universite", "url": "https://www.ardahan.edu.tr", "not": "sitede sadece idari duyurular var; etkinlik takvimi yok"},
    {"ad": "Ardahan Belediyesi", "tur": "belediye", "url": "https://www.ardahan.bel.tr", "not": "etkinlik sayfası yok"},
    {"ad": "Ardahan Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Çıldır Gölü Kış Festivali, Kura Nehri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
