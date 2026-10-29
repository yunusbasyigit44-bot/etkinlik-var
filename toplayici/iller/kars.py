"""Kars kaynakları (plaka 36). Kaynak haritası: 2026-10-29.

Okunabilir, tarihli bir etkinlik takvimi bulunamadı: Kafkas Üniversitesi etkinlik sayfaları boş geliyor,
belediye ve valilik sitelerinde sadece idari duyuru/haber var. Ortak kaynaklar (İl Kültür Turizm, Devlet Tiyatroları,
etkinlik.io) listede duruyor; yeni etkinlik çıkarsa kendiliğinden gelir.
"""
import ortak
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Akyaka", "Arpaçay", "Digor", "Kağızman", "Sarıkamış", "Selim", "Susuz"]
SALON_ILCE = {"kafkas": "Merkez", "kars": "Merkez"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Kars İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://kars.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Kars", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/kars", "cek": etkinlik_io,
     "sehir": "Kars", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Kafkas Üniversitesi", "tur": "universite", "url": "https://www.kafkas.edu.tr/kddb/tr/tumEtkinlikler2",
     "not": "etkinlik sayfası boş geliyor; takvim okunamadı"},
    {"ad": "Kars Belediyesi", "tur": "belediye", "url": "https://www.kars.bel.tr/duyurular",
     "not": "sadece idari duyuru ve haber; tarihli etkinlik takvimi yok"},
    {"ad": "Kars Valiliği ve 7 ilçe kaymakamlığı", "tur": "valilik", "url": "https://www.kars.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Sarıkamış, Kağızman, Digor belediyeleri", "tur": "belediye", "url": None, "not": "etkinlik takvimi okunmuyor"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "okunabilir etkinlik takvimi yok"},
    {"ad": "Kars Kafkas Kültür Yolu, Kars Kaz-Kış, Ani Harabeleri etkinlikleri", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
