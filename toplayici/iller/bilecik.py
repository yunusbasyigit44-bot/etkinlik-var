"""Bilecik kaynakları (plaka 11). Kaynak haritası: 2026-10-29.

Bilecik Şeyh Edebali Üniversitesi ve belediye sitelerinde okunabilir, gelecek tarihli etkinlik listesi bulunamadı;
şimdilik ortak kaynaklar listede, diğerleri "eksik" olarak işaretli. Devlet Tiyatroları sahnesi yok.
"""
import ortak
from ortak_kaynaklar import basliklar, devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Bozüyük", "Gölpazarı", "İnhisar", "Osmaneli", "Pazaryeri", "Söğüt", "Yenipazar"]
SALON_ILCE = {"şeyh edebali": "Merkez", "bşeü": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Bilecik İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://bilecik.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Bilecik", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/bilecik", "cek": etkinlik_io,
     "sehir": "Bilecik", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Bilecik Şeyh Edebali Üniversitesi", "tur": "universite", "url": "https://www.bilecik.edu.tr/main/arama/2",
     "not": "etkinlik arama sayfası var ama düzenli takvim yok; otomatik okunmuyor"},
    {"ad": "Bilecik Belediyesi", "tur": "belediye", "url": "https://www.bilecik.bel.tr",
     "not": "kültür-sanat projeleri ve atölye sayfası var; tarihli etkinlik takvimi okunmuyor"},
    {"ad": "Bozüyük, Osmaneli, Söğüt belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi yok / otomatik okunmuyor"},
    {"ad": "Bilecik Valiliği, ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.bilecik.gov.tr", "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Söğüt Ertuğrul Gazi'yi Anma ve Yörük Şenlikleri, Bozüyük Seramik günleri", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
