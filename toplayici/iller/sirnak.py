"""Şırnak kaynakları (plaka 73). Kaynak haritası: 2026-10-29.

Şırnak: Devlet Tiyatroları sahnesi yok; kaynak listede duruyor. Üniversite etkinlik sayfasında gerçek etkinlik tarihi yok.
"""
import ortak  # noqa: F401
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Beytüşşebap", "Cizre", "Güçlükonak", "İdil", "Silopi", "Uludere"]
SALON_ILCE = {"cizre": "Cizre", "silopi": "Silopi"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Şırnak İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://sirnak.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Şırnak", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/sirnak", "cek": etkinlik_io,
     "sehir": "Şırnak", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Şırnak Üniversitesi", "tur": "universite", "url": "https://www.sirnak.edu.tr/tr/etkinlikler/", "not": "listedeki tarihler yayın tarihi; etkinlik tarihi ayrı verilmiyor — okunmuyor"},
    {"ad": "Şırnak ve Cizre belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Şırnak Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": None, "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller", "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
