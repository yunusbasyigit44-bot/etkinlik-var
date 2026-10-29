"""Bitlis kaynakları (plaka 13). Kaynak haritası: 2026-10-29.

Bitlis Eren Üniversitesi'nin etkinlik listesindeki tarihler yayın tarihi gibi duruyor (etkinlik günü açık değil),
bu yüzden okunmadı. Belediye ve valilikte takvim yok; ortak kaynaklar listede. Devlet Tiyatroları sahnesi yok.
"""
import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Adilcevaz", "Ahlat", "Güroymak", "Hizan", "Mutki", "Tatvan"]
SALON_ILCE = {"bitlis eren": "Merkez", "rahva": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Bitlis İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bitlis.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bitlis", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bitlis", "cek": etkinlik_io,
     "sehir": "Bitlis", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bitlis Eren Üniversitesi", "tur": "universite", "url": "https://www.beu.edu.tr/Etkinlikler",
     "not": "liste var ama etkinlik günü açık yazmıyor (yayın tarihi); otomatik okunmuyor"},
    {"ad": "Bitlis Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://www.bitlis.bel.tr",
     "not": "duyurular/haberler; etkinlik takvimi okunmuyor"},
    {"ad": "Tatvan ve Ahlat belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok / otomatik okunmuyor"},
    {"ad": "Bitlis Valiliği, ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.bitlis.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık etkinlikler (Ahlat kültür-sanat, Tatvan Nemrut)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
