"""Rize kaynakları (plaka 53). Kaynak haritası: 2026-10-29.

Rize'de okunabilir güncel bir etkinlik takvimi bulunamadı: belediyenin etkinlik sayfası 2017-2023 arşivi (tarihsiz),
Recep Tayyip Erdoğan Üniversitesi etkinlik sayfası zaman aşımına uğruyor, duyuru sayfası idari. Ortak kaynaklar listelendi.
"""
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ardeşen", "Çamlıhemşin", "Çayeli", "Derepazarı", "Fındıklı", "Güneysu", "Hemşin", "İkizdere",
           "İyidere", "Kalkandere", "Pazar"]
salon_ilce = ilce_bulucu(ILCELER, {"rize üniversitesi": "Merkez", "erdoğan üniversitesi": "Merkez"})

KAYNAKLAR = [
    {"ad": "Rize İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://rize.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Rize", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/rize", "cek": etkinlik_io,
     "sehir": "Rize", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Recep Tayyip Erdoğan Üniversitesi", "tur": "universite", "url": "https://www.erdogan.edu.tr",
     "not": "etkinlik sayfası yanıt vermiyor (zaman aşımı); duyurular idari"},
    {"ad": "Rize Belediyesi", "tur": "belediye", "url": "https://www.rize.bel.tr/etkinlikler",
     "not": "etkinlik sayfası eski kayıtlardan oluşuyor; tarih bilgisi yok — okunamıyor"},
    {"ad": "Rize Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.rize.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Kaçkar Kültür ve Turizm, Çay Festivali, Ayder Şenlikleri, Tulum ve Müzik Festivali…)", "tur": "diger",
     "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
