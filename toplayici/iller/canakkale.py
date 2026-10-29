"""Çanakkale kaynakları (plaka 17). Kaynak haritası: 2026-10-29.

ÇOMÜ'nün etkinlik sistemi (ets.comu.edu.tr) sadece JavaScript ile çalışıyor ve şifreli veri kullanıyor;
sayfa içeriği okunamıyor. Belediyenin "Tiyatro & Etkinlikler" sayfaları alt kategorilere bölünmüş,
yaklaşan etkinlik listesi yok. Ortak kaynaklar listede; etkinlik çıkarsa kendiliğinden gelir.
"""
import ortak
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Ayvacık", "Bayramiç", "Biga", "Bozcaada", "Çan", "Eceabat", "Ezine", "Gelibolu", "Gökçeada",
           "Lapseki", "Yenice"]
SALON_ILCE = {"çomü": "Merkez", "onsekiz mart": "Merkez", "terzioğlu": "Merkez", "çanakkale kültür": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Çanakkale İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://canakkale.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Çanakkale", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/canakkale", "cek": etkinlik_io,
     "sehir": "Çanakkale", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Çanakkale Onsekiz Mart Üniversitesi", "tur": "universite", "url": "https://ets.comu.edu.tr/takvim",
     "not": "etkinlik takvimi sadece JavaScript ile çalışıyor; okunamıyor"},
    {"ad": "Çanakkale Belediyesi", "tur": "belediye", "url": "https://www.canakkale.bel.tr/tr/sayfa/1135-tiyatro-etkinlikler",
     "not": "Tiyatro & Etkinlikler alt sayfalarında yaklaşan etkinlik listesi yok"},
    {"ad": "Çanakkale Valiliği ve 11 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.canakkale.gov.tr",
     "not": "duyurular idari ve haber; etkinlik takvimi yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://canakkale.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Biga, Gelibolu, Çan, Ezine, Bozcaada, Gökçeada belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Uluslararası Troia Festivali, Bozcaada Bağbozumu, Gökçeada Festivali…", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
