"""Sakarya kaynakları (plaka 54). Kaynak haritası: 2026-10-29.

Okunabilir güncel bir etkinlik takvimi bulunamadı: Sakarya Üniversitesi etkinlik sitesinde başlıklar boş geliyor
(sadece tarih/yer var), Büyükşehir Belediyesi sitesi tamamen tarayıcıda çalışan bir uygulama. Ortak kaynaklar listelendi.
"""
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Adapazarı", "Serdivan", "Erenler", "Arifiye", "Akyazı", "Hendek", "Karasu", "Kaynarca", "Kocaali", "Pamukova",
           "Sapanca", "Söğütlü", "Ferizli", "Geyve", "Karapürçek", "Taraklı"]
SALON_ILCE = {"turgut özal kültür": "Serdivan", "sakarya üniversitesi": "Serdivan", "esentepe": "Serdivan"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Sakarya İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://sakarya.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Sakarya", "ilce_bul": salon_ilce, "varsayilan_ilce": "Adapazarı"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/sakarya", "cek": etkinlik_io,
     "sehir": "Sakarya", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Sakarya Üniversitesi", "tur": "universite", "ilce": "Serdivan", "url": "https://etkinlik.sakarya.edu.tr",
     "not": "etkinlik sitesi var ama liste başlıkları boş geliyor (sadece tarih/yer); site düzelince okunacak"},
    {"ad": "Sakarya Uygulamalı Bilimler Üniversitesi", "tur": "universite", "url": "https://www.subu.edu.tr",
     "not": "etkinlik takvimi bulunamadı"},
    {"ad": "Sakarya Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.sakarya.bel.tr",
     "not": "site tarayıcıda çalışan bir uygulama; okunabilir etkinlik listesi yok"},
    {"ad": "Adapazarı, Serdivan, Sapanca, Akyazı belediyeleri", "tur": "belediye", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Sakarya Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.sakarya.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Sakarya Caz, Sapanca Kültür Sanat, Uluslararası Sakarya Film…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
