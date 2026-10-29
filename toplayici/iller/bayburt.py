"""Bayburt kaynakları (plaka 69). Kaynak haritası: 2026-10-29.

Okunabilir özel bir takvim bulunamadı: Bayburt Belediyesi'nin etkinlik sayfasında sadece 3 eski kayıt var (2022 görselleri),
Bayburt Üniversitesi sitesi JavaScript ile çiziliyor (sayfada veri yok). Ortak kaynaklar listede; Devlet Tiyatroları sahnesi
yok, açılırsa kendiliğinden gelir.
"""
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Aydıntepe", "Demirözü"]
SALON_ILCE = {"bayburt üniversitesi": "Merkez", "baberti": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Bayburt İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bayburt.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bayburt", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bayburt", "cek": etkinlik_io,
     "sehir": "Bayburt", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bayburt Üniversitesi", "tur": "universite", "url": "https://www.bayburt.edu.tr",
     "not": "site JavaScript ile çiziliyor; sayfada okunabilir etkinlik verisi yok"},
    {"ad": "Bayburt Belediyesi", "tur": "belediye", "url": "https://www.bayburt.bel.tr/etkinlikler",
     "not": "etkinlik sayfasında sadece eski (2022) 3 kayıt var; güncellenince okunabilir"},
    {"ad": "Bayburt Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.bayburt.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık etkinlikler (Bayburt'un Kurtuluşu anmaları, Dede Korkut Kültür ve Sanat Şenlikleri…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
