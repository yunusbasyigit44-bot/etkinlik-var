"""Kütahya kaynakları (plaka 43). Kaynak haritası: 2026-10-29.

Okunabilir bir etkinlik takvimi bulunamadı (Dumlupınar Üniversitesi etkinlikleri JavaScript ile yükleniyor,
Sağlık Bilimleri Üniversitesi listesinde tarih yok, belediye sitesi bağlantıyı kesiyor). Bu yüzden ortak kaynaklar
(İl Kültür Turizm, etkinlik.io) ve gezilecek yerlerle yetinilir.
"""
import ortak
from ortak_kaynaklar import etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Altıntaş", "Aslanapa", "Çavdarhisar", "Domaniç", "Dumlupınar", "Emet", "Gediz", "Hisarcık", "Pazarlar",
           "Simav", "Şaphane", "Tavşanlı"]
SALON_ILCE = {"dpü": "Merkez", "dumlupınar üniversitesi": "Merkez", "evliya çelebi": "Merkez", "kütahya sağlık": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Kütahya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kutahya.ktb.gov.tr", "cek": ktb},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kutahya", "cek": etkinlik_io,
     "sehir": "Kütahya", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kütahya Dumlupınar Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": "https://www.dpu.edu.tr/index/etkinlikler",
     "not": "etkinlik listesi JavaScript ile yükleniyor; sayfa okunamıyor"},
    {"ad": "Kütahya Sağlık Bilimleri Üniversitesi", "tur": "universite", "ilce": "Merkez", "url": "https://www.ksbu.edu.tr/defaultx/etkinlikler",
     "not": "etkinlik afişleri var ama tarih yazmıyor; okunmuyor"},
    {"ad": "Kütahya Belediyesi", "tur": "belediye", "ilce": "Merkez", "url": "https://www.kutahya.bel.tr",
     "not": "etkinlik takvimi yok; bağlantı ara sıra kesiliyor"},
    {"ad": "Belediye Şehir Tiyatrosu ve kültür merkezleri", "tur": "belediye", "url": None, "not": "oyun takvimi bulunamadı"},
    {"ad": "Kütahya Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.kutahya.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Tavşanlı, Simav, Gediz, Emet belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü", "tur": "diger", "url": "https://kutahya.gsb.gov.tr", "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Kütahya Çini Festivali, Simav Festivali…", "tur": "diger", "url": None, "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
