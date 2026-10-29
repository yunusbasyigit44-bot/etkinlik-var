"""Kilis kaynakları (plaka 79). Kaynak haritası: 2026-10-29.

Kilis 7 Aralık Üniversitesi etkinlik sayfasındaki tarih, etkinliğin değil haberin yayın tarihi (çoğu "gerçekleştirildi" haberi);
bu yüzden okunmuyor. Belediye sitesinin sertifikası doğrulanamıyor. Bu yüzden Kilis'te ortak kaynaklar + eksik listesi var.
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
import ortak
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Elbeyli", "Musabeyli", "Polateli"]
SALON_ILCE = {"kilis 7 aralık": "Merkez", "elbeyli": "Elbeyli", "musabeyli": "Musabeyli", "polateli": "Polateli"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Kilis İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kilis.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kilis", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kilis", "cek": etkinlik_io,
     "sehir": "Kilis", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kilis 7 Aralık Üniversitesi", "tur": "universite", "url": "https://kilis.edu.tr/tr/etkinlikler",
     "not": "etkinlikler haber biçiminde; listedeki tarih yayın tarihi, etkinlik tarihi değil"},
    {"ad": "Kilis Belediyesi", "tur": "belediye", "url": "https://www.kilis.bel.tr", "not": "site sertifikası doğrulanamıyor — okunamıyor"},
    {"ad": "Kilis Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kilis.gov.tr/duyurular",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Elbeyli, Musabeyli, Polateli belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Kilis Zeytin ve Zeytinyağı, Kültür Sanat vb.)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
