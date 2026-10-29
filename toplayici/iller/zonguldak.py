"""Zonguldak kaynakları (plaka 67). Kaynak haritası: 2026-10-29.

Okunabilir özel bir takvim bulunamadı: belediyenin /etkinlikler sayfası "Henüz etkinlik bulunmuyor" diyor, Bülent Ecevit
Üniversitesi'nin etkinlik listesi sadece afiş + yayın tarihi veriyor (etkinlik tarihi görselde). Ortak kaynaklar listede;
Devlet Tiyatroları sahnesi yok, açılırsa kendiliğinden gelir.
"""
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Alaplı", "Çaycuma", "Devrek", "Gökçebey", "Kilimli", "Kozlu", "Ereğli"]
SALON_ILCE = {"karadeniz ereğli": "Ereğli", "bülent ecevit": "Merkez", "beun": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Zonguldak İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://zonguldak.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Zonguldak", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/zonguldak", "cek": etkinlik_io,
     "sehir": "Zonguldak", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Zonguldak Bülent Ecevit Üniversitesi", "tur": "universite", "url": "https://www.beun.edu.tr/arsiv/tum-etkinlikler.html",
     "not": "liste sadece afiş ve yayın tarihi veriyor; etkinlik tarihi görselin içinde — otomatik okunmuyor"},
    {"ad": "Zonguldak Belediyesi", "tur": "belediye", "url": "https://www.zonguldak.bel.tr/etkinlikler",
     "not": "etkinlik sayfası var ama şu an boş ('Henüz etkinlik bulunmuyor'); dolunca okunabilir"},
    {"ad": "Karadeniz Ereğli, Çaycuma, Devrek belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Zonguldak Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.zonguldak.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Uluslararası Zonguldak Kömür Kongresi, Kozlu Madenci Anma…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
