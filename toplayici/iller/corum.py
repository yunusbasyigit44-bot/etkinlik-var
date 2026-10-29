"""Çorum kaynakları (plaka 19). Kaynak haritası: 2026-10-29.

Hitit Üniversitesi'nin etkinlik takvimi tek bir eski örnek gösteriyor, Çorum Belediyesi sitesi
okuma isteklerini reddediyor (HTTP 468); bu yüzden şimdilik sadece ortak kaynaklar var.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Alaca", "Bayat", "Boğazkale", "Dodurga", "İskilip", "Kargı", "Laçin", "Mecitözü", "Oğuzlar",
           "Osmancık", "Ortaköy", "Sungurlu", "Uğurludağ"]
SALON_ILCE = {"hitit üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Çorum İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://corum.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Çorum", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/corum", "cek": etkinlik_io,
     "sehir": "Çorum", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Hitit Üniversitesi", "tur": "universite", "url": "https://hitit.edu.tr/tr/hitit/etkinlik-takvimi",
     "not": "etkinlik takvimi sayfası güncel değil (tek eski örnek); duyurular idari"},
    {"ad": "Çorum Belediyesi", "tur": "belediye", "url": "https://www.corum.bel.tr", "not": "site okuma isteklerini reddediyor (HTTP 468) — okunamıyor"},
    {"ad": "Çorum Valiliği", "tur": "valilik", "url": "https://www.corum.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "13 ilçe kaymakamlığı ve belediyeleri", "tur": "kaymakamlik", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Uluslararası Hittit Festivali, Leblebi ve Kültür Festivali", "tur": "diger", "url": None,
     "not": "yıllık festivaller; 2026 tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
