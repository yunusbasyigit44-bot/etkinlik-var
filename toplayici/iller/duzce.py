"""Düzce kaynakları (plaka 81). Kaynak haritası: 2026-10-29.

Düzce Üniversitesi ana sitesinin sertifikası doğrulanamıyor; haber sitesindeki tarihler yayın tarihi (etkinlik tarihi yok).
Belediye ve valilik sayfalarında etkinlik takvimi yok. Bu yüzden Düzce'de ortak kaynaklar + eksik listesi var.
Devlet Tiyatroları sahnesi yok; kaynak listede duruyor, sahne açılırsa kendiliğinden gelir.
"""
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Merkez", "Akçakoca", "Cumayeri", "Çilimli", "Gölyaka", "Gümüşova", "Kaynaşlı", "Yığılca"]
SALON_ILCE = {"düzce üniversitesi": "Merkez", "konuralp": "Merkez", "akçakoca": "Akçakoca", "cumayeri": "Cumayeri",
              "çilimli": "Çilimli", "gölyaka": "Gölyaka", "gümüşova": "Gümüşova", "kaynaşlı": "Kaynaşlı", "yığılca": "Yığılca"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Düzce İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://duzce.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Düzce", "ilce_bul": salon_ilce, "varsayilan_ilce": "Merkez"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/duzce", "cek": etkinlik_io,
     "sehir": "Düzce", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Düzce Üniversitesi", "tur": "universite", "url": "https://haber.duzce.edu.tr",
     "not": "ana site sertifikası doğrulanamıyor; haber sitesinde etkinlik tarihi yok (sadece yayın tarihi)"},
    {"ad": "Düzce Belediyesi", "tur": "belediye", "url": "https://www.duzce.bel.tr/duyurular",
     "not": "duyurular imar/idari; etkinlik takvimi yok"},
    {"ad": "Akçakoca Belediyesi ve diğer ilçe belediyeleri", "tur": "belediye", "ilce": "Akçakoca", "url": None,
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Düzce Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.duzce.gov.tr/duyurular",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Akçakoca Fındık ve Kültür, Düzce Kültür Sanat…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
