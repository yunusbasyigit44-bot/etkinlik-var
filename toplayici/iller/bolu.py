"""Bolu kaynakları (plaka 14). Kaynak haritası: 2026-10-29.

Bolu'da düzenli, gelecek tarihli etkinlik yayınlayan okunabilir bir sayfa bulunamadı:
İBÜ Ajanda (ajanda.ibu.edu.tr) haber portalı ve Temmuz 2026'dan beri güncellenmiyor,
belediyenin etkinlik sayfası boş. Ortak kaynaklar listede; sahne/etkinlik açılırsa kendiliğinden gelir.
"""
import ortak
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Dörtdivan", "Gerede", "Göynük", "Kıbrıscık", "Mengen", "Mudurnu", "Seben", "Yeniçağa"]
SALON_ILCE = {"baibü": "Merkez", "abant izzet baysal": "Merkez", "ibü": "Merkez", "bolmek": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Bolu İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bolu.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bolu", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bolu", "cek": etkinlik_io,
     "sehir": "Bolu", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bolu Abant İzzet Baysal Üniversitesi", "tur": "universite", "url": "https://ajanda.ibu.edu.tr/etkinlik/",
     "not": "Ajanda haber portalı; son kayıt Temmuz 2026, yaklaşan etkinlik takvimi yok"},
    {"ad": "Bolu Belediyesi", "tur": "belediye", "url": "https://www.bolu.bel.tr/kultursanatvesosyalisler/etkinlikler/",
     "not": "etkinlikler sayfası boş; duyurular idari"},
    {"ad": "Bolu Valiliği ve 8 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.bolu.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://bolu.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "İl Milli Eğitim Müdürlüğü", "tur": "diger", "url": "https://bolu.meb.gov.tr", "not": "idari haberler; etkinlik yok"},
    {"ad": "Mudurnu, Göynük, Gerede belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Mengen Aşçılık, Kıbrıscık Kültür, Köroğlu, Abant Yaz Festivali…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
