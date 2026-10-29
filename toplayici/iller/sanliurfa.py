"""Şanlıurfa kaynakları (plaka 63). Kaynak haritası: 2026-10-29.

Okunabilir bir yerel etkinlik takvimi bulunamadı: Büyükşehir ve Haliliye belediyeleri etkinlikleri haber biçiminde
(geçmiş, tarihsiz) yayımlıyor; Harran Üniversitesi listesinde tarih yok (sadece yayın tarihi). Ortak kaynaklar listede.
"""
import ortak
from ortak_kaynaklar import devlet_tiyatrosu, etkinlik_io, ilce_bulucu, ktb

ILCELER = ["Eyyübiye", "Haliliye", "Karaköprü", "Akçakale", "Birecik", "Bozova", "Ceylanpınar", "Halfeti", "Harran",
           "Hilvan", "Siverek", "Suruç", "Viranşehir"]
SALON_ILCE = {"harran üniversitesi": "Haliliye", "osmanbey": "Eyyübiye", "balıklıgöl": "Eyyübiye", "gap kültür": "Haliliye"}
salon_ilce = ilce_bulucu(ILCELER, SALON_ILCE)

KAYNAKLAR = [
    {"ad": "Şanlıurfa İl Kültür ve Turizm Müdürlüğü", "tur": "kultur", "url": "https://sanliurfa.ktb.gov.tr", "cek": ktb},
    {"ad": "Devlet Tiyatroları", "tur": "kultur", "url": "https://devtiyatro.gov.tr", "cek": devlet_tiyatrosu,
     "sehir": "Şanlıurfa", "ilce_bul": salon_ilce, "varsayilan_ilce": "Haliliye"},
    {"ad": "etkinlik.io (konser, sahne, festival)", "tur": "diger", "url": "https://etkinlik.io/sanliurfa", "cek": etkinlik_io,
     "sehir": "Şanlıurfa", "ilce_bul": salon_ilce},
    # --- Etkinlik takvimi yayınlamayan / ulaşılamayan kaynaklar (eksikler) ---
    {"ad": "Harran Üniversitesi", "tur": "universite", "url": "https://www.harran.edu.tr/Etkinlikler",
     "not": "liste sayfasında etkinlik tarihi yok (sadece yayın tarihi; çoğu çevrim içi kongre); okunmuyor"},
    {"ad": "Şanlıurfa Büyükşehir Belediyesi", "tur": "belediye", "url": "https://www.sanliurfa.bel.tr",
     "not": "etkinlikler haber biçiminde (geçmiş); takvim sayfası yok"},
    {"ad": "Haliliye Belediyesi", "tur": "belediye", "url": "https://www.haliliye.bel.tr/kategori/43/1/konserler",
     "not": "konser/tiyatro bölümleri geçmiş haberlerden oluşuyor; tarihli program yok"},
    {"ad": "Eyyübiye, Karaköprü ve diğer ilçe belediyeleri", "tur": "belediye", "url": "https://www.eyyubiye.bel.tr",
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Music Urfa (UNESCO Müzik Şehri)", "tur": "kultur", "url": "https://www.musicurfa.com.tr",
     "not": "etkinlik takvimi okunmuyor (sonraki tur)"},
    {"ad": "Şanlıurfa Valiliği ve ilçe kaymakamlıkları", "tur": "valilik", "url": "https://www.sanliurfa.gov.tr",
     "not": "duyurular idari; etkinlik yok"},
    {"ad": "Büyükşehir Şehir Tiyatrosu", "tur": "belediye", "url": None, "not": "okunabilir oyun takvimi bulunamadı"},
    {"ad": "Gençlik ve Spor İl Müdürlüğü, İl MEB", "tur": "diger", "url": None, "not": "etkinlik takvimi yok"},
    {"ad": "Yıllık festivaller (Göbeklitepe Kültür Yolu, Şanlıurfa Müzik Festivali, Halfeti…)", "tur": "diger", "url": None,
     "not": "yıllık; resmî tarihleri henüz yayımlanmamış"},
    {"ad": "STK'lar, öğrenci kulüpleri, kafeler", "tur": "diger", "url": None,
     "not": "çoğu sadece Instagram'da duyuruyor — 'Etkinliğini ekle' formu ile toplanacak"},
]
