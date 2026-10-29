"""Bingöl kaynakları (plaka 12). Kaynak haritası: 2026-10-29.

Bingöl Üniversitesi etkinlikleri ASP.NET tablosundan (viewstate) geliyor, güvenle okunamadı.
Belediye ve valilik sitelerinde de takvim yok; ortak kaynaklar listede. Devlet Tiyatroları sahnesi yok.
"""
import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Adaklı", "Genç", "Karlıova", "Kiğı", "Solhan", "Yayladere", "Yedisu"]
SALON_ILCE = {"bingöl üniversitesi": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Bingöl İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bingol.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bingöl", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bingol", "cek": etkinlik_io,
     "sehir": "Bingöl", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bingöl Üniversitesi", "tur": "universite", "url": "https://www.bingol.edu.tr/tr/tum-etkinlikler",
     "not": "etkinlik listesi ASP.NET tablosunda (form durumu gerekiyor); otomatik okunmuyor"},
    {"ad": "Bingöl Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://www.bingol.bel.tr",
     "not": "okunabilir etkinlik takvimi bulunamadı"},
    {"ad": "Bingöl Valiliği, ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.bingol.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık etkinlikler (kış, kültür ve bal festivalleri)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
